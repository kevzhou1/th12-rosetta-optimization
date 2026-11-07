"""Run Wine's real d3dx9_40 D3DXVec3Project/ProjectArray and the SSE replacements
side by side in a 32-bit x86 emulator (unicorn), and compare both against a
float32 model of Wine's arithmetic.

Usage:
  python3 -m venv venv && venv/bin/pip install -r requirements.txt
  venv/bin/python verify.py <Wine's i386 d3dx9_40.dll> <code> [cases=600]

<code> is one of:
  d3dx_sse.obj                                 the compiled functions (from build.sh)
  thcrap-patch/d3dx_sse/th12.v1.00b.js         the machine code as shipped in the patch
  "<game folder>/th12.exe"                     the original exe: builds what patch_th12.py
                                               would write as th12_sse.exe, in memory, and
                                               calls the functions through the game's own
                                               redirected import stubs

Whisky's copy of the dll:
  ~/Library/Application Support/com.isaacmarovitz.Whisky/Libraries/Wine/lib/wine/i386-windows/d3dx9_40.dll

The x87 control word is set the way wined3d leaves it for a d3d9 game (single
precision, round to nearest), so Wine's x87 results are directly comparable.
Each case checks: the returned pointer, the 3 floats written (bit-exact), that
nothing past each 12-byte result is touched, stdcall stack cleanup, and that
callee-saved registers survive. Asserts on the first mismatch."""
import json, os, struct, sys, random
import numpy as np
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE
from unicorn.x86_const import *

f32 = np.float32
DLL, CODE = sys.argv[1], sys.argv[2]
CASES = int(sys.argv[3]) if len(sys.argv) > 3 else 600

# ---------- load COFF object: function name -> code bytes (and no relocations) ----------
def coff_funcs(path):
    b = open(path, 'rb').read()
    nsec, _, symptr, nsym = struct.unpack_from('<HIII', b, 2)
    optsz = struct.unpack_from('<H', b, 16)[0]
    secs = []
    for i in range(nsec):
        name, vs, va, rs, rp, relp, lnp, nrel, nln, ch = struct.unpack_from('<8sIIIIIIHHI', b, 20 + optsz + 40 * i)
        secs.append((rs, rp, nrel))
    strtab = symptr + 18 * nsym
    out, i = {}, 0
    while i < nsym:
        raw = b[symptr + 18 * i: symptr + 18 * i + 18]
        nm, val, secno, typ, cls, naux = struct.unpack('<8sIhHBB', raw)
        if nm[:4] == b'\0\0\0\0':
            off = struct.unpack_from('<I', nm, 4)[0]
            nm = b[strtab + off: b.index(b'\0', strtab + off)]
        else:
            nm = nm.rstrip(b'\0')
        if typ == 0x20 and secno > 0 and cls == 2:  # external function
            rs, rp, nrel = secs[secno - 1]
            assert nrel == 0, f'{nm} has relocations'
            assert val == 0
            out[nm.decode()] = b[rp:rp + rs]
        i += 1 + naux
    return out


# ---------- emulator setup ----------
uc = Uc(UC_ARCH_X86, UC_MODE_32)
cr0 = uc.reg_read(UC_X86_REG_CR0); uc.reg_write(UC_X86_REG_CR0, (cr0 & ~4) | 2)
uc.reg_write(UC_X86_REG_CR4, uc.reg_read(UC_X86_REG_CR4) | 0x600)

# Wine dll at its preferred base (no relocations needed)
d = open(DLL, 'rb').read()
pe = struct.unpack_from('<I', d, 0x3c)[0]
nsec = struct.unpack_from('<H', d, pe + 6)[0]; optsz = struct.unpack_from('<H', d, pe + 20)[0]
base = struct.unpack_from('<I', d, pe + 24 + 28)[0]; imgsz = struct.unpack_from('<I', d, pe + 24 + 56)[0]
uc.mem_map(base, (imgsz + 0xfff) & ~0xfff)
uc.mem_write(base, d[:0x1000])
for i in range(nsec):
    nm, vs, va, rs, rp = struct.unpack_from('<8sIIII', d, pe + 24 + optsz + 40 * i)
    uc.mem_write(base + va, d[rp:rp + min(rs, vs if vs else rs)])
WINE_P, WINE_PA = base + 0x30790, base + 0x30a00
assert uc.mem_read(WINE_P, 4) == bytes.fromhex('8d4c2404')
uc.mem_write(0x66d40078, b'\0')  # d3dx debug channel flags: tracing off

# ---------- the SSE code under test ----------
if CODE.lower().endswith('.exe'):
    # build the patched exe the way patch_th12.py does, map its whole image, and
    # call the game's import stubs (now "jmp <SSE code>")
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    import patch_th12 as P
    orig = open(CODE, 'rb').read()
    d3dx = P.d3dx_patch(P.PE(orig), print)
    img = P.PE(P.build_exe(orig, [('SSE fix', d3dx)]))
    sites = d3dx['binhacks']
    size = struct.unpack_from('<I', img.b, img.opt + 56)[0]
    uc.mem_map(img.base, (size + 0xfff) & ~0xfff)
    uc.mem_write(img.base, bytes(img.b[:0x1000]))
    for _, vs, va, rs, rp, _ in img.sections():
        uc.mem_write(img.base + va, bytes(img.b[rp:rp + min(rs, vs or rs)]))
    SSE_P_AT = int(sites['d3dx_sse_project']['addr'], 16)
    SSE_PA_AT = int(sites['d3dx_sse_project_array']['addr'], 16)
    print('calling through the patched stubs at 0x%x and 0x%x' % (SSE_P_AT, SSE_PA_AT))
else:
    if CODE.lower().endswith('.js'):
        caves = json.load(open(CODE))['codecaves']
        SSE_P, SSE_PA = (bytes.fromhex(caves[k]['code'].replace(' ', ''))
                         for k in ('d3dx_sse_Vec3Project', 'd3dx_sse_Vec3ProjectArray'))
    else:
        funcs = coff_funcs(CODE)
        SSE_P, SSE_PA = funcs['_sse_Vec3Project@24'], funcs['_sse_Vec3ProjectArray@36']
    SSE_P_AT, SSE_PA_AT = 0x10000000, 0x10002000
    uc.mem_map(0x10000000, 0x4000)
    uc.mem_write(SSE_P_AT, SSE_P); uc.mem_write(SSE_PA_AT, SSE_PA)

STUB, CW, TGT = 0x100000, 0x100800, 0x100804
uc.mem_map(0x100000, 0x1000)
stub = bytes.fromhex('dbe3') + b'\xd9\x2d' + struct.pack('<I', CW) + b'\xff\x15' + struct.pack('<I', TGT)
STUB_END = STUB + len(stub)
uc.mem_write(STUB, stub + b'\xf4')
uc.mem_write(CW, struct.pack('<H', 0x007f))  # what wined3d's setup_fpu leaves: single precision, nearest

HEAP = 0x200000; uc.mem_map(HEAP, 0x100000)
STK = 0x800000; uc.mem_map(STK, 0x100000); TOP = STK + 0xff000

counts = {'ins': 0, 'x87': 0}
def hook(u, addr, size, _):
    counts['ins'] += 1
    op = bytes(u.mem_read(addr, min(size, 3)))
    i = 0
    while i < len(op) and op[i] in (0x66, 0x67, 0xf2, 0xf3, 0x2e, 0x3e, 0x26, 0x36, 0x64, 0x65):
        i += 1
    if i < len(op) and 0xd8 <= op[i] <= 0xdf: counts['x87'] += 1
uc.hook_add(UC_HOOK_CODE, hook)

SENT = {UC_X86_REG_EBX: 0x11111111, UC_X86_REG_ESI: 0x22222222, UC_X86_REG_EDI: 0x33333333, UC_X86_REG_EBP: 0x44444444}
def call(fn, args):
    esp = TOP - 4 * len(args)
    uc.mem_write(esp, struct.pack('<%dI' % len(args), *args))
    uc.reg_write(UC_X86_REG_ESP, esp)
    for r, v in SENT.items(): uc.reg_write(r, v)
    uc.mem_write(TGT, struct.pack('<I', fn))
    counts['ins'] = counts['x87'] = 0
    uc.emu_start(STUB, STUB_END)
    assert uc.reg_read(UC_X86_REG_ESP) == TOP, 'stdcall stack cleanup wrong'
    for r, v in SENT.items(): assert uc.reg_read(r) == v, 'callee-saved register clobbered'
    return uc.reg_read(UC_X86_REG_EAX)

# ---------- heap helpers ----------
_hp = [HEAP]
def alloc(n):
    a = _hp[0]; _hp[0] += (n + 15) & ~15; return a
def reset_heap(): _hp[0] = HEAP; uc.mem_write(HEAP, b'\xcd' * 0x100000)
def put(a, data): uc.mem_write(a, data); return a
def mat_bytes(m): return np.asarray(m, f32).reshape(16).tobytes()
def vp_bytes(vp): return struct.pack('<4I2f', *vp)

# ---------- float32 model of Wine's arithmetic ----------
def mm(a, b):
    o = np.zeros((4, 4), f32)
    for i in range(4):
        for j in range(4):
            s = f32(a[i, 0] * b[0, j]); s = f32(s + f32(a[i, 1] * b[1, j]))
            s = f32(s + f32(a[i, 2] * b[2, j])); o[i, j] = f32(s + f32(a[i, 3] * b[3, j]))
    return o

def model(v, vp, proj, view, world):
    with np.errstate(all='ignore'):
        m = np.eye(4, dtype=f32)
        for x in (world, view, proj):
            if x is not None: m = mm(m, x)
        x, y, z = (f32(t) for t in v)
        r = []
        for j in range(4):
            s = f32(x * m[0, j]); s = f32(s + f32(y * m[1, j])); s = f32(s + f32(z * m[2, j])); r.append(f32(s + m[3, j]))
        o = [f32(r[j] / r[3]) for j in range(3)]
        if vp is not None:
            X, Y, W, H, mn, mx = vp
            one, half = f32(1), f32(0.5)
            o = [f32(f32(X) + f32(f32(f32(one + o[0]) * f32(W)) * half)),
                 f32(f32(Y) + f32(f32(f32(one - o[1]) * f32(H)) * half)),
                 f32(f32(mn) + f32(o[2] * f32(f32(mx) - f32(mn))))]
        return o

def bits(x): return struct.unpack('<I', struct.pack('<f', float(x)))[0]
def same(a, b):
    a, b = float(a), float(b)
    if a != a and b != b: return True
    return bits(a) == bits(b)

# ---------- test data ----------
rng = np.random.default_rng(12)
def rnd_mat(kind):
    if kind == 'general': return rng.uniform(-3, 3, (4, 4)).astype(f32)
    if kind == 'proj':  # D3DXMatrixPerspectiveFovLH-like
        fov, asp, zn, zf = rng.uniform(0.3, 1.5), rng.uniform(0.7, 1.8), rng.uniform(0.1, 10), rng.uniform(100, 10000)
        ys = 1 / np.tan(fov / 2); xs = ys / asp
        return np.array([[xs, 0, 0, 0], [0, ys, 0, 0], [0, 0, zf / (zf - zn), 1], [0, 0, -zn * zf / (zf - zn), 0]], f32)
    if kind == 'affine':
        m = rng.uniform(-2, 2, (4, 4)).astype(f32); m[:, 3] = [0, 0, 0, 1]; m[3, :3] = rng.uniform(-500, 500, 3); return m
VPS = [(0, 0, 640, 480, 0.0, 1.0), (32, 16, 384, 448, 0.0, 1.0), (0, 0, 1280, 960, 0.25, 0.75)]

stats = {'P': [0, 0, 0], 'PA': [0, 0, 0]}  # [cases, sse==model, wine==model]
maxrel = [0.0]
def relerr(a, b):
    a, b = float(a), float(b)
    if a != a or b != b or abs(a) == float('inf') or abs(b) == float('inf'): return 0.0 if same(a, b) else float('inf')
    return abs(a - b) / max(abs(a), abs(b), 1e-6)

wine_cost, sse_cost = [], []
for case in range(CASES):
    reset_heap()
    mats = [None if rng.random() < 0.15 else rnd_mat(k) for k in ('proj', 'affine', 'affine')]
    if case % 7 == 0: mats = [rnd_mat('general') for _ in range(3)]
    proj, view, world = mats
    vp = None if rng.random() < 0.2 else VPS[case % len(VPS)]
    pa = [put(alloc(64), mat_bytes(m)) if m is not None else 0 for m in mats]
    vpa = put(alloc(24), vp_bytes(vp)) if vp else 0

    # --- single point ---
    v = rng.uniform(-400, 400, 3).astype(f32)
    va = put(alloc(12), v.tobytes())
    exp = model(v, vp, proj, view, world)
    res = {}
    for name, fn in (('wine', WINE_P), ('sse', SSE_P_AT)):
        oa = alloc(16); put(oa, b'\xcd' * 16)
        ret = call(fn, [oa, va, vpa, pa[0], pa[1], pa[2]])
        assert ret == oa, 'return value'
        raw = bytes(uc.mem_read(oa, 16)); assert raw[12:] == b'\xcd' * 4, 'wrote past 12 bytes'
        res[name] = struct.unpack('<3f', raw[:12])
        (wine_cost if name == 'wine' else sse_cost).append((counts['ins'], counts['x87']))
    stats['P'][0] += 1
    stats['P'][1] += all(same(a, b) for a, b in zip(res['sse'], exp))
    stats['P'][2] += all(same(a, b) for a, b in zip(res['wine'], exp))
    for a, b in zip(res['sse'], res['wine']): maxrel[0] = max(maxrel[0], relerr(a, b))
    assert all(same(a, b) for a, b in zip(res['sse'], exp)), (case, res, exp)

    # --- array ---
    n = [0, 1, 3, 16, 40][case % 5]
    instride = [12, 16, 20][case % 3]; outstride = [12, 16, 24][(case // 3) % 3]
    alias = case % 11 == 0
    if alias: outstride = instride
    pts = rng.uniform(-400, 400, (max(n, 1), 3)).astype(f32)
    def mk_in():
        a = alloc(instride * max(n, 1) + 16); put(a, b'\xab' * (instride * max(n, 1) + 16))
        for i in range(n): put(a + i * instride, pts[i].tobytes())
        return a
    outs = {}
    for name, fn in (('wine', WINE_PA), ('sse', SSE_PA_AT)):
        ia = mk_in()
        if alias: oa = ia
        else:
            oa = alloc(outstride * max(n, 1) + 16); put(oa, b'\xcd' * (outstride * max(n, 1) + 16))
        ret = call(fn, [oa, outstride, ia, instride, vpa, pa[0], pa[1], pa[2], n])
        assert ret == oa
        outs[name] = bytes(uc.mem_read(oa, outstride * max(n, 1) + 16))
    stats['PA'][0] += 1
    # untouched bytes (gaps between strided elements, tail) must be identical between wine and sse
    ok_sse = True; ok_wine = True
    for i in range(n):
        e = model(pts[i], vp, proj, view, world)
        s = struct.unpack_from('<3f', outs['sse'], i * outstride)
        w = struct.unpack_from('<3f', outs['wine'], i * outstride)
        ok_sse &= all(same(a, b) for a, b in zip(s, e)); ok_wine &= all(same(a, b) for a, b in zip(w, e))
        for a, b in zip(s, w): maxrel[0] = max(maxrel[0], relerr(a, b))
    mask = bytearray(len(outs['sse']))
    for i in range(n): mask[i * outstride: i * outstride + 12] = b'\x01' * 12
    assert all(m or a == b for m, a, b in zip(mask, outs['sse'], outs['wine'])), 'bytes outside the 12-byte results differ'
    assert ok_sse, ('array', case)
    stats['PA'][1] += ok_sse; stats['PA'][2] += ok_wine

print('D3DXVec3Project      cases=%d  sse==model %d  wine==model %d' % tuple(stats['P']))
print('D3DXVec3ProjectArray cases=%d  sse==model %d  wine==model %d' % tuple(stats['PA']))
print('max relative difference sse vs wine: %.3g' % maxrel[0])
wi = np.mean([c[0] for c in wine_cost]); wx = np.mean([c[1] for c in wine_cost])
si = np.mean([c[0] for c in sse_cost]); sx = np.mean([c[1] for c in sse_cost])
print('per Vec3Project call: wine %.0f instructions (%.0f x87), sse %.0f instructions (%.0f x87)' % (wi, wx, si, sx))
