#!/usr/bin/env python3
"""Compare how much float code in Windows game executables is x87 vs SSE.

Rosetta translates SSE to native ARM instructions but emulates x87 in software
(roughly 15-50 ns per x87 instruction), so a game whose float math is mostly
x87 runs far slower under Whisky/Wine on Apple Silicon than one built for SSE.
Visual Studio switched its 32-bit default from x87 to SSE2 in VS2012 (linker 11).

Usage: compare_x87.py <game.exe> [more.exe ...]
Needs `objdump` (Xcode command line tools).
"""
import collections, datetime, re, struct, subprocess, sys

X87 = re.compile(r'^f(ld|st|add|sub|mul|div|com|ucom|xch|chs|abs|sqrt|sin|cos|patan|ptan|i|nst|ldcw|rndint|scale'
                 r'|prem|tst|free|ninit|xam|xtract|yl2x|2xm1|cmov|wait)')
SSE_SCALAR = re.compile(r'^(movss|addss|subss|mulss|divss|sqrtss|minss|maxss|comiss|ucomiss|cvt\w*s[sd]\w*'
                        r'|movsd|addsd|subsd|mulsd|divsd|sqrtsd|comisd|ucomisd)$')
SSE_PACKED = re.compile(r'^(movaps|movups|addps|subps|mulps|divps|shufps|unpck\w+ps|xorps|andps|andnps|orps|minps'
                        r'|maxps|sqrtps|rsqrtps|rcpps|cmp\w*ps|dpps|haddps|blendps|insertps)$')


def mnemonics(path):
    out = subprocess.run(['objdump', '-d', '--x86-asm-syntax=intel', path], capture_output=True, text=True).stdout
    c = collections.Counter()
    for line in out.splitlines():
        parts = line.split('\t')
        if len(parts) >= 2 and parts[1].strip():
            c[parts[1].split()[0]] += 1
    return c


def d3dx_imports(path):
    out = subprocess.run(['objdump', '-p', path], capture_output=True, text=True).stdout
    dll, funcs = None, []
    for line in out.splitlines():
        m = re.search(r'DLL Name: (\S+)', line)
        if m:
            dll = m.group(1).lower()
        elif dll and dll.startswith('d3dx9') and 'D3DX' in line:
            funcs.append(line.split()[-1])
    return funcs


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print(f"{'exe':16} {'linker':6} {'built':10} {'x87':>7} {'SSE scalar':>10} {'SSE packed':>10} {'x87 share':>9}  "
          f"D3DX projection imports")
    for p in sys.argv[1:]:
        b = open(p, 'rb').read(4096)
        pe = struct.unpack_from('<I', b, 0x3c)[0]
        mach, ts = struct.unpack_from('<H', b, pe + 4)[0], struct.unpack_from('<I', b, pe + 8)[0]
        link = f'{b[pe + 26]}.{b[pe + 27]}'
        c = mnemonics(p)
        nx = sum(v for k, v in c.items() if X87.match(k))
        ns = sum(v for k, v in c.items() if SSE_SCALAR.match(k))
        npk = sum(v for k, v in c.items() if SSE_PACKED.match(k))
        proj = [f for f in d3dx_imports(p) if 'Project' in f]
        built = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).date()
        name = p.rsplit('/', 1)[-1] + ('' if mach == 0x14c else ' (x64)')
        print(f'{name:16} {link:6} {built!s:10} {nx:7d} {ns:10d} {npk:10d} {nx / max(nx + ns + npk, 1):9.0%}  '
              f"{', '.join(proj) or '-'}")


if __name__ == '__main__':
    main()
