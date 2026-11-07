#!/usr/bin/env python3
"""Attribute a macOS `sample` profile of a 32-bit Wine game (running under
Rosetta) to the game's own code and to the Windows DLLs it calls.

`sample` can't symbolize 32-bit Windows code, but it still records the game's
return addresses as "???  (in <unknown binary>)  [0x........]". This script
walks one thread's call tree, assigns every sample to the deepest such 32-bit
address on its stack, and maps addresses to the PE file (exe/dll) that contains
them, using export names where the PE has them.

Usage:
  sample <pid> 3 -file th12_sample.txt
  attribute_profile.py th12_sample.txt --pe path/to/th12.exe \\
      --pe ~/Library/Application\\ Support/com.isaacmarovitz.Whisky/Libraries/Wine/lib/wine/i386-windows

Options:
  --thread TEXT  pick the thread whose header contains TEXT (default: the thread
                 with the most samples inside Rosetta's runtime)
  --pe PATH      PE file, or directory searched recursively; repeatable
  --top N        number of hottest addresses to list (default 25)

Caveats:
- Code compiled without frame pointers (th12.exe is) breaks the stack walk, so
  some samples have no 32-bit frame; they're reported as "no 32-bit frame".
- The innermost frame found is often the *caller* of the function that was
  running (e.g. the return address right after `call D3DXMatrixMultiply`).
- Module mapping assumes each PE loaded at its preferred ImageBase, which is
  what 32-bit Wine normally does. Several Wine DLLs share preferred bases, and
  the first match wins, so entries with only a handful of samples may be
  attributed to the wrong DLL. Pass only the DLLs you care about to avoid that.
"""
import argparse, bisect, collections, os, re, struct, sys

NODE = re.compile(r'^([\s+!:|]*)(\d+) (.*)$')
GUEST = re.compile(r'\(in <unknown binary>\)\s+\[0x([0-9a-f]+)\]')
LIB = re.compile(r'\(in ([^)]*)\)')
THREAD_HDR = re.compile(r'^\s+\d+ (Thread_\d+.*)$')


def read_threads(path):
    """Return {thread header: [(depth, count, text), ...]} from the Call graph section."""
    threads, cur, in_graph = {}, None, False
    for line in open(path, errors='replace'):
        line = line.rstrip('\n')
        if line.startswith('Call graph:'):
            in_graph = True
            continue
        if not in_graph:
            continue
        if line.startswith(('Total number in stack', 'Sort by top of stack', 'Binary Images:')):
            break
        m = THREAD_HDR.match(line)
        if m:
            cur = threads.setdefault(m.group(1).strip(), [])
            continue
        m = NODE.match(line)
        if m and cur is not None:
            cur.append((len(m.group(1)), int(m.group(2)), m.group(3)))
    return threads


def leaves(nodes):
    """Yield (self_samples, node_index, parent_list) for every node with self time."""
    parent, kids, stack = [None] * len(nodes), collections.Counter(), []
    for i, (d, c, _) in enumerate(nodes):
        while stack and nodes[stack[-1]][0] >= d:
            stack.pop()
        if stack:
            parent[i] = stack[-1]
            kids[stack[-1]] += c
        stack.append(i)
    for i, (_, c, _) in enumerate(nodes):
        if c - kids[i] > 0:
            yield c - kids[i], i, parent


def guest_addr(text):
    m = GUEST.search(text)
    if m:
        a = int(m.group(1), 16)
        if a < 2 ** 32:
            return a
    return None


class PE:
    def __init__(self, path):
        b = open(path, 'rb').read()
        if b[:2] != b'MZ':
            raise ValueError
        pe = struct.unpack_from('<I', b, 0x3c)[0]
        if b[pe:pe + 4] != b'PE\0\0' or struct.unpack_from('<H', b, pe + 4)[0] != 0x14c:
            raise ValueError  # only 32-bit x86 images
        opt = pe + 24
        nsec, optsz = struct.unpack_from('<H', b, pe + 6)[0], struct.unpack_from('<H', b, pe + 20)[0]
        self.name, self.base = os.path.basename(path), struct.unpack_from('<I', b, opt + 28)[0]
        self.size = struct.unpack_from('<I', b, opt + 56)[0]
        secs = [struct.unpack_from('<8sIIII', b, opt + optsz + 40 * i) for i in range(nsec)]

        def off(rva):
            for _, vs, va, rs, rp in secs:
                if va <= rva < va + max(vs, rs):
                    return rva - va + rp
        self.exports = []
        erva = struct.unpack_from('<I', b, opt + 96)[0]
        if erva and off(erva) is not None:
            e = off(erva)
            nfun, nnam, afun, anam, aord = struct.unpack_from('<IIIII', b, e + 20)
            funcs = [struct.unpack_from('<I', b, off(afun) + 4 * k)[0] for k in range(nfun)]
            for k in range(nnam):
                nrva = struct.unpack_from('<I', b, off(anam) + 4 * k)[0]
                ordi = struct.unpack_from('<H', b, off(aord) + 2 * k)[0]
                n = b[off(nrva): b.index(b'\0', off(nrva))].decode(errors='replace')
                self.exports.append((funcs[ordi], n))
            self.exports.sort()
        self._rvas = [r for r, _ in self.exports]

    def describe(self, addr):
        rva = addr - self.base
        k = bisect.bisect_right(self._rvas, rva) - 1
        if k >= 0:
            r, n = self.exports[k]
            return f'{self.name}!{n}+0x{rva - r:x}'
        return f'{self.name}+0x{rva:x}'


def load_pes(paths):
    pes = []
    for p in paths:
        files = [p] if os.path.isfile(p) else [os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs
                                                 if f.lower().endswith(('.exe', '.dll', '.drv'))]
        for f in files:
            try:
                pes.append(PE(f))
            except (ValueError, struct.error, OSError):
                pass
    return pes


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('sample')
    ap.add_argument('--thread')
    ap.add_argument('--pe', action='append', default=[])
    ap.add_argument('--top', type=int, default=25)
    a = ap.parse_args()

    threads = read_threads(a.sample)
    if not threads:
        sys.exit('no call graph found (is this `sample` output?)')
    def guest_samples(nodes):
        """samples whose stack contains at least one 32-bit (Windows) frame"""
        n = 0
        for s, i, parent in leaves(nodes):
            j = i
            while j is not None and guest_addr(nodes[j][2]) is None:
                j = parent[j]
            n += s if j is not None else 0
        return n

    if a.thread:
        pick = [t for t in threads if a.thread in t]
        if not pick:
            sys.exit('no thread matches %r; threads: %s' % (a.thread, ', '.join(threads)))
        name = pick[0]
    else:
        # Default: the thread spending the most time in identifiable 32-bit code. In a
        # Wine game that's normally the game's main thread (wined3d's render thread is
        # second). Pass --thread to pick another one.
        ranked = sorted(threads, key=lambda t: -guest_samples(threads[t]))
        print('threads with the most samples in 32-bit Windows code:')
        for t in ranked[:4]:
            print(f'  {guest_samples(threads[t]):6d}  {t}')
        print()
        name = ranked[0]
    nodes = threads[name]

    pes = load_pes(a.pe)

    def module_of(addr):
        for p in pes:
            if p.base <= addr < p.base + p.size:
                return p
        return None

    by_mod, by_addr, by_leaf, total = collections.Counter(), collections.Counter(), collections.Counter(), 0
    for s, i, parent in leaves(nodes):
        total += s
        m = LIB.search(nodes[i][2])
        by_leaf[m.group(1) if m else nodes[i][2][:40]] += s
        j, g = i, None
        while j is not None:
            g = guest_addr(nodes[j][2])
            if g is not None:
                break
            j = parent[j]
        if g is None:
            by_mod['(no 32-bit frame)'] += s
        else:
            p = module_of(g)
            by_mod[p.name if p else f'(unmapped 0x{g >> 16:04x}xxxx)'] += s
            by_addr[g] += s

    print(f'thread: {name}   samples: {total}\n')
    print('where the CPU was (leaf frame):')
    for k, v in by_leaf.most_common(8):
        print(f'  {v:6d} {v / total:6.1%}  {k}')
    print('\ndeepest 32-bit frame, by module:')
    for k, v in by_mod.most_common(12):
        print(f'  {v:6d} {v / total:6.1%}  {k}')
    print(f'\ntop {a.top} 32-bit return addresses:')
    for addr, v in by_addr.most_common(a.top):
        p = module_of(addr)
        print(f'  {v:6d} {v / total:6.1%}  0x{addr:08x}  {p.describe(addr) if p else ""}')


if __name__ == '__main__':
    main()
