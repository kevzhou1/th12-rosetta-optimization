#!/usr/bin/env python3
"""Make Touhou 12 (Undefined Fantastic Object) run faster under Wine on Apple Silicon.

TH12 spends about a fifth of its main thread in two functions of Wine's
d3dx9_40.dll, D3DXVec3Project and D3DXVec3ProjectArray. Wine's versions are x87
floating-point code, which Rosetta 2 emulates slowly. This script redirects the
game's calls to SSE versions of the two functions that give bit-identical
results. Optionally it also adds a "draw 2 of every 3 frames" frameskip.

  python3 patch_th12.py "<TH12 game folder>"               install
  python3 patch_th12.py "<TH12 game folder>" --dry-run     only show what it would do
  python3 patch_th12.py "<TH12 game folder>" --uninstall   undo

How the fix is applied depends on what's in the folder:
  thcrap found (<folder>/thcrap, or the folder given with --thcrap):
      The fix becomes a local thcrap patch, added to every thcrap run config
      (or only to --config NAME). Keep launching the game through your thcrap
      shortcut, e.g. "th12 (thpatch-en).exe".
  no thcrap, or --exe:
      Writes th12_sse.exe next to th12.exe. th12.exe itself is never changed.
      Launch th12_sse.exe instead of th12.exe.

Options:
  --frameskip     also install the 2-of-3 frameskip
  --exe           write th12_sse.exe even if thcrap is present
  --thcrap DIR    thcrap folder, if it isn't inside the game folder
  --config NAME   only change this thcrap run config (e.g. thpatch-en)

Needs Python 3.8 or newer and nothing else. Works with th12.exe v1.00b. The
calls are found by reading the exe's import table, not from fixed addresses,
so other v1.00b builds (Steam, score-counter bugfix, ...) should work too, but
only the original v1.00b has been tested.
"""
import argparse, array, hashlib, json, os, re, shutil, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
D3DX_DIR = os.path.join(HERE, 'd3dx-sse-fix', 'thcrap-patch', 'd3dx_sse')
FS_DIR = os.path.join(HERE, 'frameskip-patch', 'thcrap-patch', 'frameskip_custom')
PATCH_FILE = 'th12.v1.00b.js'           # the file each patch folder ships
TESTED_SHA256 = 'd8d644d2e64957a3031b1a1399d0502e1ddaa5252d2c4e492770ad6717827628'
GAME_EXE, OUT_EXE = 'th12.exe', 'th12_sse.exe'
CODE_SEC, DATA_SEC = b'.patchx', b'.patchw'   # sections added to th12_sse.exe
ARCHIVES = {'d3dx_sse': 'repos/local/d3dx_sse/', 'frameskip_custom': 'repos/local/frameskip_custom/'}
FUNCS = [  # import, codecave with the SSE code, binhack name
    ('D3DXVec3Project', 'd3dx_sse_Vec3Project', 'd3dx_sse_project'),
    ('D3DXVec3ProjectArray', 'd3dx_sse_Vec3ProjectArray', 'd3dx_sse_project_array'),
]


class PatchError(Exception):
    pass


def align(x, a):
    return (x + a - 1) // a * a


# ---------------------------------------------------------------- PE file ----

class PE:
    """Just enough of a 32-bit PE reader/writer for this job."""

    def __init__(self, data):
        self.b = b = bytearray(data)
        if b[:2] != b'MZ':
            raise PatchError('not a Windows executable')
        pe = struct.unpack_from('<I', b, 0x3c)[0]
        if b[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', b, pe + 4)[0] != 0x14c \
                or struct.unpack_from('<H', b, pe + 24)[0] != 0x10b:
            raise PatchError('not a 32-bit x86 Windows executable')
        self.pe, self.opt = pe, pe + 24
        self.sectab = self.opt + struct.unpack_from('<H', b, pe + 20)[0]
        self.base = struct.unpack_from('<I', b, self.opt + 28)[0]
        self.salign, self.falign = struct.unpack_from('<II', b, self.opt + 32)

    @property
    def nsec(self):
        return struct.unpack_from('<H', self.b, self.pe + 6)[0]

    def sections(self):
        """[(name, vsize, rva, rawsize, rawptr, characteristics)]"""
        out = []
        for i in range(self.nsec):
            o = self.sectab + 40 * i
            name, vs, va, rs, rp = struct.unpack_from('<8sIIII', self.b, o)
            out.append((name.rstrip(b'\0'), vs, va, rs, rp, struct.unpack_from('<I', self.b, o + 36)[0]))
        return out

    def off(self, rva):
        for _, vs, va, rs, rp, _ in self.sections():
            if va <= rva < va + min(vs or rs, rs):
                return rva - va + rp
        raise PatchError(f'address 0x{self.base + rva:x} is not in the file')

    def cstr(self, rva):
        o = self.off(rva)
        return bytes(self.b[o:self.b.index(0, o)]).decode('latin-1')

    def imports(self):
        """yield (dll, function, VA of its import address table slot)"""
        irva = struct.unpack_from('<I', self.b, self.opt + 104)[0]
        if not irva:
            return
        o = self.off(irva)
        while True:
            oft, _, _, name, ft = struct.unpack_from('<IIIII', self.b, o)
            o += 20
            if not name or not ft:
                break
            dll, t, k = self.cstr(name), self.off(oft or ft), 0
            while True:
                e = struct.unpack_from('<I', self.b, t + 4 * k)[0]
                if not e:
                    break
                if not e & 0x80000000:
                    yield dll, self.cstr(e + 2), self.base + ft + 4 * k
                k += 1

    def checksum(self):
        data = bytes(self.b) + b'\0' * (len(self.b) % 2)
        words = array.array('H', data)
        if sys.byteorder != 'little':
            words.byteswap()
        k = (self.opt + 64) // 2
        s = sum(words) - words[k] - words[k + 1]
        while s >> 16:
            s = (s & 0xffff) + (s >> 16)
        return s + len(self.b)


# ------------------------------------------------------- thcrap code strings ----
# The patches are stored as thcrap patch files. To apply them without thcrap,
# this understands the parts of thcrap's code syntax the patches use.

TOKEN = re.compile(r'\s+|([0-9a-fA-F]{2})|<codecave:(\w+)>|\[codecave:(\w+)\]|\[Rx([0-9a-fA-F]+)\]|<nop:(\d+)>')


def assemble(code, at, caves, base):
    """thcrap code string -> bytes placed at address `at`. caves: name -> address."""
    out, pos = bytearray(), 0
    while pos < len(code):
        m = TOKEN.match(code, pos)
        if not m:
            raise PatchError(f'unsupported thcrap code syntax: {code[pos:pos + 24]!r}')
        pos = m.end()
        hx, absolute, relative, rx, nop = m.groups()
        if hx:
            out.append(int(hx, 16))
        elif (absolute or relative) and (absolute or relative) not in caves:
            raise PatchError(f'unknown codecave {absolute or relative}')
        elif absolute:
            out += struct.pack('<I', caves[absolute])
        elif relative or rx:
            target = caves[relative] if relative else base + int(rx, 16)
            out += struct.pack('<i', target - (at + len(out) + 4))
        elif nop:
            out += b'\x90' * int(nop)
    return bytes(out)


def addr_of(spec, base):
    if isinstance(spec, int):
        return spec
    spec = spec.strip()
    return base + int(spec[2:], 16) if spec[:2] in ('Rx', 'rx') else int(spec, 16)


def load_thcrap_json(path):
    """thcrap's JSON allows trailing commas; Python's doesn't."""
    text = open(path, encoding='utf-8-sig').read()
    try:
        return json.loads(text)
    except ValueError:
        return json.loads(re.sub(r',(\s*[}\]])', r'\1', text))


def save_json(obj, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent='\t')


# ------------------------------------------------------------ the patches ----

def d3dx_patch(pe, log):
    """The SSE fix as a thcrap patch, with binhacks for the calls found in this exe."""
    caves = load_thcrap_json(os.path.join(D3DX_DIR, PATCH_FILE))['codecaves']
    slots = {fn: slot for dll, fn, slot in pe.imports()
             if re.fullmatch(r'd3dx9_\d+\.dll', dll, re.I) and fn in [f for f, _, _ in FUNCS]}
    binhacks = {}
    for fn, cave, hack in FUNCS:
        if fn not in slots:
            raise PatchError(f"this exe doesn't import {fn} from d3dx9")
        slot, sites, other = struct.pack('<I', slots[fn]), [], 0
        for _, vs, va, rs, rp, ch in pe.sections():
            if not ch & 0x20000000:   # only executable sections
                continue
            data = bytes(pe.b[rp:rp + min(vs or rs, rs)])
            i = data.find(slot)
            while i != -1:
                op = data[i - 2:i] if i >= 2 else b''
                if op in (b'\xff\x25', b'\xff\x15'):   # jmp [slot] / call [slot]: 6 bytes each
                    sites.append((pe.base + va + i - 2, op))
                else:
                    other += 1
                i = data.find(slot, i + 1)
        if not sites:
            raise PatchError(f'found no jmp/call through the {fn} import (packed or DRM-protected exe?)')
        for k, (site, op) in enumerate(sites):
            # jmp [slot] -> jmp sse; nop      call [slot] -> call sse; nop  (same length)
            binhacks[hack if k == 0 else f'{hack}_{k + 1}'] = {
                'title': f"SSE {fn} (replaces Wine's x87 version; identical results)",
                'addr': hex(site), 'expected': op.hex() + slot.hex(),
                'code': ('e9' if op == b'\xff\x25' else 'e8') + f'[codecave:{cave}] 90'}
        log(f'  {fn}: redirecting {len(sites)} site(s) at ' + ', '.join(hex(s) for s, _ in sites))
        if other:
            log(f'  warning: {other} other use(s) of the {fn} import stay on Wine\'s version')
    return {'codecaves': caves, 'binhacks': binhacks}


def frameskip_patch():
    return load_thcrap_json(os.path.join(FS_DIR, PATCH_FILE))


def check_expected(pe, patch, what):
    for name, h in patch['binhacks'].items():
        exp = bytes.fromhex(h['expected'].replace(' ', ''))
        a = addr_of(h['addr'], pe.base)
        o = pe.off(a - pe.base)
        if bytes(pe.b[o:o + len(exp)]) != exp:
            raise PatchError(f'{what}: the code at 0x{a:x} is not what the patch expects; this exe is a different build')


# -------------------------------------------------------------- exe mode ----

def build_exe(src, patches):
    """Return a copy of the exe with the patches applied: the codecaves go into
    new sections at the end, and the binhacks overwrite code in place."""
    pe = PE(src)
    if any(n in (CODE_SEC, DATA_SEC) for n, *_ in pe.sections()):
        raise PatchError(f'{GAME_EXE} already contains this patch')
    for what, p in patches:
        check_expected(pe, p, what)

    # strip a trailing signature (it would be invalid anyway); refuse other appended data
    end = max(rp + rs for _, _, _, rs, rp, _ in pe.sections())
    if len(pe.b) > end:
        sec_off, sec_size = struct.unpack_from('<II', pe.b, pe.opt + 128)
        if sec_off == align(end, 8) and sec_off + sec_size == len(pe.b):
            struct.pack_into('<II', pe.b, pe.opt + 128, 0, 0)
            del pe.b[end:]
        else:
            raise PatchError('the exe has extra data appended after its sections; not supported')
    if len(pe.b) % pe.falign:
        pe.b += b'\0' * (align(len(pe.b), pe.falign) - len(pe.b))

    # lay out the codecaves (16-byte aligned) in one code and one data section
    caves = {}
    for _, p in patches:
        for name, c in p.get('codecaves', {}).items():
            if name in caves:
                raise PatchError(f'codecave {name} defined twice')
            caves[name] = c
    groups = {CODE_SEC: [], DATA_SEC: []}
    for name, c in caves.items():
        groups[CODE_SEC if 'e' in c.get('access', 'rwe') else DATA_SEC].append(name)
    zero = dict.fromkeys(caves, 0)
    size = {n: max(len(assemble(c.get('code', ''), 0, zero, 0)), int(c.get('size', 0))) for n, c in caves.items()}

    next_rva = align(max(va + max(vs, rs) for _, vs, va, rs, _, _ in pe.sections()), pe.salign)
    layout, addr = [], {}
    for sec, names in groups.items():
        if not names:
            continue
        off = 0
        for n in names:
            addr[n] = pe.base + next_rva + off
            off = align(off + size[n], 16)
        layout.append((sec, next_rva, names, off))
        next_rva = align(next_rva + off, pe.salign)

    hdr_end = pe.sectab + 40 * (pe.nsec + len(layout))
    first_raw = min(rp for _, _, _, rs, rp, _ in pe.sections() if rs)
    hdr_size = struct.unpack_from('<I', pe.b, pe.opt + 60)[0]
    if hdr_end > min(hdr_size, first_raw) or any(pe.b[pe.sectab + 40 * pe.nsec:hdr_end]):
        raise PatchError('no room in the exe header for another section')

    for sec, rva, names, vsize in layout:
        data = bytearray(vsize)
        for n in names:
            o = addr[n] - pe.base - rva
            code = assemble(caves[n].get('code', ''), addr[n], addr, pe.base)
            data[o:o + len(code)] = code
        raw = align(vsize, pe.falign)
        hdr = struct.pack('<8sIIIIIIHHI', sec, vsize, rva, raw, len(pe.b), 0, 0, 0, 0,
                          0x60000020 if sec == CODE_SEC else 0xc0000040)
        pe.b[pe.sectab + 40 * pe.nsec:pe.sectab + 40 * pe.nsec + 40] = hdr
        struct.pack_into('<H', pe.b, pe.pe + 6, pe.nsec + 1)
        field = 4 if sec == CODE_SEC else 8        # SizeOfCode / SizeOfInitializedData
        struct.pack_into('<I', pe.b, pe.opt + field, struct.unpack_from('<I', pe.b, pe.opt + field)[0] + raw)
        pe.b += bytes(data) + b'\0' * (raw - vsize)
    struct.pack_into('<I', pe.b, pe.opt + 56, next_rva)          # SizeOfImage

    for _, p in patches:
        for name, h in p['binhacks'].items():
            a = addr_of(h['addr'], pe.base)
            exp = bytes.fromhex(h['expected'].replace(' ', ''))
            code = assemble(h['code'], a, addr, pe.base)
            if len(code) != len(exp):
                raise PatchError(f'binhack {name}: new code is not the same length as the code it replaces')
            o = pe.off(a - pe.base)
            pe.b[o:o + len(code)] = code
    struct.pack_into('<I', pe.b, pe.opt + 64, pe.checksum())
    return bytes(pe.b)


def is_ours(path):
    try:
        return any(n == CODE_SEC for n, *_ in PE(open(path, 'rb').read()).sections())
    except (PatchError, OSError, struct.error):
        return False


# ----------------------------------------------------------- thcrap mode ----

def thcrap_build(thdir, sha, size):
    """(game id, build) thcrap uses for this exe, read from thcrap's versions.js files."""
    by_size = None
    for root, _, files in os.walk(os.path.join(thdir, 'repos')):
        if 'versions.js' in files:
            text = open(os.path.join(root, 'versions.js'), encoding='utf-8', errors='replace').read()
            m = re.search(r'"%s"\s*:\s*\[\s*"(\w+)"\s*,\s*"([^"]+)"' % sha, text)
            if m:
                return m.group(1), m.group(2)
            m = re.search(r'"%d"\s*:\s*\[\s*"(\w+)"\s*,\s*"([^"]+)"' % size, text)
            by_size = by_size or (m and (m.group(1), m.group(2)))
    return by_size


def run_configs(thdir, only):
    cfgdir = os.path.join(thdir, 'config')
    out = []
    for f in sorted(os.listdir(cfgdir)):
        if not f.endswith('.js') or (only and f not in (only, only + '.js')):
            continue
        try:
            cfg = load_thcrap_json(os.path.join(cfgdir, f))
        except ValueError:
            print(f'  skipping {f}: could not parse it')
            continue
        if isinstance(cfg, dict) and isinstance(cfg.get('patches'), list):
            out.append((os.path.join(cfgdir, f), cfg))
    if only and not out:
        raise PatchError(f'no thcrap run config named {only} in {cfgdir}')
    return out


def thcrap_install(thdir, pe, exe_bytes, a, do, log):
    sha = hashlib.sha256(exe_bytes).hexdigest()
    gb = thcrap_build(thdir, sha, len(exe_bytes))
    if not gb:
        raise PatchError("thcrap doesn't recognise this th12.exe, so it wouldn't load the patch. "
                         'Run again with --exe to make a patched th12_sse.exe instead.')
    game, build = gb
    fname = f'{game}.{build}.js'

    d3dx = d3dx_patch(pe, log)
    check_expected(pe, d3dx, 'SSE fix')
    if d3dx == load_thcrap_json(os.path.join(D3DX_DIR, PATCH_FILE)):
        log('  (identical to the tested patch for the original v1.00b)')
    dst = os.path.join(thdir, ARCHIVES['d3dx_sse'])

    def write_d3dx():
        os.makedirs(dst, exist_ok=True)
        shutil.copy2(os.path.join(D3DX_DIR, 'patch.js'), os.path.join(dst, 'patch.js'))
        save_json(d3dx, os.path.join(dst, fname))
    do(f'write the SSE fix to {dst}{fname}', write_d3dx)
    want = [ARCHIVES['d3dx_sse']]

    if a.frameskip:
        if fname != PATCH_FILE:
            raise PatchError(f'the frameskip patch is only for th12 v1.00b (thcrap says this is {game} {build})')
        check_expected(pe, frameskip_patch(), 'frameskip')
        dst = os.path.join(thdir, ARCHIVES['frameskip_custom'])
        do(f'copy the frameskip patch to {dst}', lambda: shutil.copytree(FS_DIR, dst, dirs_exist_ok=True))
        want.append(ARCHIVES['frameskip_custom'])

    for path, cfg in run_configs(thdir, a.config):
        have = [p.get('archive') for p in cfg['patches'] if isinstance(p, dict)]
        add = [w for w in want if w not in have]
        name = os.path.basename(path)
        if not add:
            log(f'  {name} already has {", ".join(want)}')
            continue
        bak = path + '.bak-patch_th12'

        def edit(path=path, cfg=cfg, add=add, bak=bak):
            if not os.path.exists(bak):
                shutil.copy2(path, bak)
            cfg['patches'] += [{'archive': w} for w in add]
            save_json(cfg, path)
        note = '' if os.path.exists(bak) else f' (backup: {os.path.basename(bak)})'
        do(f'add {", ".join(add)} to {name}{note}', edit)


def thcrap_uninstall(thdir, a, do, log):
    ours = set(ARCHIVES.values())
    configs = run_configs(thdir, a.config)
    for path, cfg in configs:
        keep = [p for p in cfg['patches'] if not (isinstance(p, dict) and p.get('archive') in ours)]
        if len(keep) != len(cfg['patches']):
            def edit(path=path, cfg=cfg, keep=keep):
                cfg['patches'] = keep
                save_json(cfg, path)
            do(f'remove the fix from {os.path.basename(path)}', edit)
    still = {p.get('archive') for _, c in run_configs(thdir, None) for p in c['patches'] if isinstance(p, dict)}
    for arch in ARCHIVES.values():
        d = os.path.join(thdir, arch)
        if os.path.isdir(d) and (a.config is None or arch not in still):
            do(f'delete {d}', lambda d=d: shutil.rmtree(d))


# ------------------------------------------------------------------- main ----

def main():
    if sys.version_info < (3, 8):
        sys.exit('Python 3.8 or newer is needed')
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                 epilog='Run with no arguments for the full explanation.')
    ap.add_argument('game', help='TH12 game folder (or the path to th12.exe)')
    ap.add_argument('--frameskip', action='store_true', help='also install the 2-of-3 frameskip')
    ap.add_argument('--exe', action='store_true', help='write th12_sse.exe even if thcrap is present')
    ap.add_argument('--thcrap', metavar='DIR', help="thcrap folder, if it isn't <game folder>/thcrap")
    ap.add_argument('--config', metavar='NAME', help='only change this thcrap run config')
    ap.add_argument('--uninstall', action='store_true', help='undo')
    ap.add_argument('--dry-run', action='store_true', help="show what would happen, don't change anything")
    if len(sys.argv) == 1:
        sys.exit(__doc__)
    a = ap.parse_args()

    game = os.path.dirname(a.game) if os.path.isfile(a.game) else a.game
    exe_path = os.path.join(game, GAME_EXE)
    thdir = a.thcrap or os.path.join(game, 'thcrap')
    if a.thcrap and not os.path.isdir(os.path.join(thdir, 'config')):
        raise PatchError(f'{thdir} is not a thcrap folder (no config/ inside)')
    use_thcrap = os.path.isdir(os.path.join(thdir, 'config')) and not a.exe

    def do(msg, fn):
        print(('  [dry run] ' if a.dry_run else '  ') + msg)
        if not a.dry_run:
            fn()

    if a.uninstall:
        print('Uninstalling')
        if os.path.isdir(os.path.join(thdir, 'config')):
            thcrap_uninstall(thdir, a, do, print)
        out = os.path.join(game, OUT_EXE)
        if is_ours(out):
            do(f'delete {out}', lambda: os.remove(out))
        print('Done.' if not a.dry_run else 'Dry run: nothing was changed.')
        return

    if not os.path.isfile(exe_path):
        raise PatchError(f'no {GAME_EXE} in {game}')
    exe = open(exe_path, 'rb').read()
    pe = PE(exe)
    if b'th12.dat' not in exe or b'th12.cfg' not in exe:
        raise PatchError(f"{exe_path} doesn't look like Touhou 12's th12.exe")
    if is_ours(exe_path):
        raise PatchError(f'{exe_path} was already patched by this script; put the original th12.exe back first')
    sha = hashlib.sha256(exe).hexdigest()
    print(f'{exe_path}\n  sha256 {sha}')
    print('  this is the tested th12 v1.00b' if sha == TESTED_SHA256 else
          '  not the tested build: the fix will be applied only if the code it changes looks as expected')

    if use_thcrap:
        print(f'Installing into thcrap at {thdir}')
        thcrap_install(thdir, pe, exe, a, do, print)
        print('Launch the game through your thcrap shortcut as usual.' if not a.dry_run else
              'Dry run: nothing was changed.')
    else:
        out = os.path.join(game, OUT_EXE)
        if os.path.exists(out) and not is_ours(out):
            raise PatchError(f'{out} exists and was not made by this script; not overwriting it')
        print(f'Writing {OUT_EXE}')
        patches = [('SSE fix', d3dx_patch(pe, print))]
        if a.frameskip:
            patches.append(('frameskip', frameskip_patch()))
        new = build_exe(exe, patches)
        do(f'write {out} ({len(new)} bytes; {GAME_EXE} is unchanged)', lambda: open(out, 'wb').write(new))
        print(f'Launch {OUT_EXE} instead of {GAME_EXE}. It uses the same scores, replays and settings.'
              if not a.dry_run else 'Dry run: nothing was changed.')


if __name__ == '__main__':
    try:
        main()
    except PatchError as e:
        sys.exit(f'error: {e}')
    except (struct.error, IndexError, UnicodeDecodeError) as e:
        sys.exit(f'error: could not read the exe; it may be damaged ({e})')
