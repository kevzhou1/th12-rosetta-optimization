#!/usr/bin/env python3
"""Turn the compiled SSE functions (d3dx_sse.obj) into a thcrap patch for th12 v1.00b.

The patch has:
  - two codecaves holding the raw 32-bit machine code of the SSE functions;
  - two binhacks that overwrite th12's 6-byte import stubs
        0x46c6d4: jmp [0x4982e0]   (D3DXVec3Project)
        0x46c6c8: jmp [0x4982e8]   (D3DXVec3ProjectArray)
    with "jmp <codecave>; nop", so every call in the game goes to the SSE code
    instead of Wine's x87 d3dx9_40.dll. thcrap checks the "expected" bytes first
    and refuses to patch an exe that doesn't match.

Usage: make_patch.py d3dx_sse.obj <out_dir> [path/to/th12.exe to validate against]
Writes <out_dir>/patch.js and <out_dir>/th12.v1.00b.js.
"""
import json, os, struct, sys

BINHACKS = [  # (name, thunk address, expected bytes, codecave, function symbol)
    ('d3dx_sse_project', 0x46c6d4, 'ff25e0824900', 'd3dx_sse_Vec3Project', '_sse_Vec3Project@24'),
    ('d3dx_sse_project_array', 0x46c6c8, 'ff25e8824900', 'd3dx_sse_Vec3ProjectArray', '_sse_Vec3ProjectArray@36'),
]


def coff_funcs(path):
    """name -> machine code of each external function; refuses code needing relocation."""
    b = open(path, 'rb').read()
    nsec, _, symptr, nsym = struct.unpack_from('<HIII', b, 2)
    optsz = struct.unpack_from('<H', b, 16)[0]
    secs = [struct.unpack_from('<8sIIIIIIHHI', b, 20 + optsz + 40 * i) for i in range(nsec)]
    strtab, out, i = symptr + 18 * nsym, {}, 0
    while i < nsym:
        nm, val, secno, typ, cls, naux = struct.unpack_from('<8sIhHBB', b, symptr + 18 * i)
        if nm[:4] == b'\0\0\0\0':
            o = struct.unpack_from('<I', nm, 4)[0]
            nm = b[strtab + o: b.index(b'\0', strtab + o)]
        else:
            nm = nm.rstrip(b'\0')
        if typ == 0x20 and secno > 0 and cls == 2:
            _, _, _, rs, rp, _, _, nrel, _, _ = secs[secno - 1]
            if nrel or val:
                sys.exit(f'{nm.decode()}: not self-contained (needs its own section and no relocations)')
            out[nm.decode()] = b[rp:rp + rs]
        i += 1 + naux
    return out


def exe_bytes(exe, va, n):
    b = open(exe, 'rb').read()
    pe = struct.unpack_from('<I', b, 0x3c)[0]
    nsec, optsz = struct.unpack_from('<H', b, pe + 6)[0], struct.unpack_from('<H', b, pe + 20)[0]
    rva = va - struct.unpack_from('<I', b, pe + 24 + 28)[0]
    for k in range(nsec):
        _, vs, vaddr, rs, rp = struct.unpack_from('<8sIIII', b, pe + 24 + optsz + 40 * k)
        if vaddr <= rva < vaddr + max(vs, rs):
            o = rva - vaddr + rp
            return b[o:o + n]


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    obj, out = sys.argv[1], sys.argv[2]
    code = coff_funcs(obj)

    def hexs(bs):
        return ' '.join(bs[k:k + 16].hex() for k in range(0, len(bs), 16))

    patch = {'codecaves': {}, 'binhacks': {}}
    for name, addr, expected, cave, sym in BINHACKS:
        patch['codecaves'][cave] = {'access': 're', 'code': hexs(code[sym])}
    for name, addr, expected, cave, sym in BINHACKS:
        what = 'D3DXVec3ProjectArray' if 'Array' in sym else 'D3DXVec3Project'
        patch['binhacks'][name] = {
            'title': f"SSE {what} (replaces Wine's x87 version; identical results)",
            'addr': hex(addr), 'expected': expected, 'code': f'e9[codecave:{cave}] 90'}

    if len(sys.argv) > 3:
        for name, addr, expected, *_ in BINHACKS:
            ok = exe_bytes(sys.argv[3], addr, 6) == bytes.fromhex(expected)
            print(f'{hex(addr)} expected bytes {"match" if ok else "DO NOT MATCH"} in {sys.argv[3]}')
            if not ok:
                sys.exit('wrong exe version; th12 v1.00b is required')

    os.makedirs(out, exist_ok=True)
    json.dump({'id': 'd3dx_sse',
               'title': "TH12: SSE replacements for Wine's x87 D3DXVec3Project/ProjectArray (faster under Rosetta)"},
              open(os.path.join(out, 'patch.js'), 'w'), indent='\t')
    json.dump(patch, open(os.path.join(out, 'th12.v1.00b.js'), 'w'), indent='\t')
    print(f'wrote {out}/patch.js and {out}/th12.v1.00b.js '
          f'({", ".join(f"{s}: {len(code[s])} bytes" for *_, s in BINHACKS)})')


if __name__ == '__main__':
    main()
