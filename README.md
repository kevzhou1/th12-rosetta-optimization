# Touhou 12 Apple Silicon Optimization

On my own M2 MBA, TH12 running through Whisky/Wine wasn't able to hold 60fps. This fix removes about a fifth of the
work on the game's main thread (according to whatever benchmark claude made)

## Quick start

You need:
- TH12 **v1.00b** (the *****shrine download version)
- **Python 3.8 or newer.**

```sh
git clone <this repo's URL> touhou-mac-perf      # or download the ZIP and unzip it
cd touhou-mac-perf
python3 patch_th12.py "/path/to/Touhou 12 folder" --dry-run   # shows what it will do
python3 patch_th12.py "/path/to/Touhou 12 folder"
```

To get the folder path, type `python3 patch_th12.py ` (with a trailing space) and drag
the game folder from Finder into the Terminal window. In Whisky, the bottle's
**Open C: Drive** button takes you to the folder in Finder.

What happens next depends on your setup:

- **If you use thcrap** (an English patch, for example), the fix is added to your
  thcrap configs as a local patch. Launch the game through your thcrap shortcut as
  before. If thcrap isn't in a `thcrap` folder inside the game folder, pass
  `--thcrap "/path/to/thcrap"`.
- **If you don't**, the script writes `th12_sse.exe` next to `th12.exe`. Launch
  `th12_sse.exe` instead; in Whisky, use **Run…** or pin it. It shares scores,
  replays and settings with `th12.exe`.

`th12.exe` itself is never modified. More options:

| | |
|---|---|
| `--frameskip` | Draw only 2 of every 3 frames (i was annoyed that the default custom exe only has 1/2 and 1/3 as options)
| `--uninstall` | Undo everything the script did. |
| `--exe` | Make `th12_sse.exe` even if thcrap is installed. |
| `--config NAME` | Only change one thcrap run config, e.g. `--config thpatch-en`. |

**Who it helps:** Apple Silicon Macs running TH12 through Wine. On Intel Macs,
Linux and Windows the slow part runs at full speed anyway, so there's nothing to gain.

**If you are using other versions of th12** I have no idea what will happen.

## Why this is the way it is

The game's main thread was pinned at 100% of one core. Almost all of that time was inside Rosetta's runtime library, emulating x87
  floating-point instructions in software. TH12 was built in 2009 with VS2008,
  and 99% of its float code is x87.
- About 19% of the main thread went to Wine's own `d3dx9_40.dll`.
  `D3DXVec3Project` / `D3DXVec3ProjectArray` do three full 4x4 matrix multiplies
  per point, all in x87. The game calls them through two 6-byte import stubs.
- The fix replaces those two functions with SSE versions. They do the same math
  in the same order, so the results are bit-identical.

## Layout

| Path | What |
|---|---|
| `patch_th12.py` | **The installer.** Applies the fix (and optionally the frameskip) through thcrap, or writes a standalone `th12_sse.exe`. Python standard library only. |
| `d3dx-sse-fix/d3dx_sse.c` | The fix: SSE `D3DXVec3Project` / `D3DXVec3ProjectArray`. |
| `d3dx-sse-fix/thcrap-patch/d3dx_sse/` | The compiled fix as a thcrap patch. `patch_th12.py` reads its machine code from here. |
| `d3dx-sse-fix/d3dx_sse.asm` | Disassembly of the compiled fix, for review. |
| `d3dx-sse-fix/build.sh` | Recompiles `d3dx_sse.c` into 32-bit Windows machine code and regenerates the thcrap patch (needs clang). |
| `d3dx-sse-fix/make_patch.py` | Object file -> thcrap codecaves + binhacks; validates against `th12.exe`. |
| `d3dx-sse-fix/verify.py` | Runs Wine's real dll and the SSE code side by side in an x86 emulator and checks they agree bit for bit. |
| `frameskip-patch/` | The "draw 2 of every 3 frames" patch, and `decide.s`, the assembly its code came from. |
| `monitoring/threadmon.py` | Per-thread CPU monitor for any macOS process (libproc, no root). Shows which thread is saturated. `threadmon.py <pid> [secs] [interval_ms]` |
| `monitoring/gcwatch.py` | Detects Java stop-the-world GC pauses from outside the JVM (written for Minecraft). `gcwatch.py <pid> [secs] [interval_ms]` |
| `monitoring/clockprobe.c` | Estimates the CPU clock a thread gets at each QoS class, e.g. to see Low Power Mode's effect. `clang -O2 -o clockprobe clockprobe.c` |
| `x87-benchmarks/` | x86_64 microbenchmarks that run under Rosetta: x87 vs SSE throughput, MSVC-style x87 patterns, per-instruction costs. `./build.sh` |
| `analysis/attribute_profile.py` | Turns a macOS `sample` profile of a Wine game into "which Windows module/function is the time in", using the 32-bit return addresses `sample` records but can't name. |
| `analysis/compare_x87.py` | x87 vs SSE instruction counts, compiler version, build date and D3DX imports for any Windows exe. |
| `analysis/example/th12_sample.txt` | The TH12 profile the D3DX finding came from. |

## How the fix is applied

- **Finding the calls.** `patch_th12.py` reads `th12.exe`'s import table to find
  the import slots for `D3DXVec3Project` and `D3DXVec3ProjectArray`. It then finds
  every `jmp [slot]` and `call [slot]` that uses them. On the original v1.00b
  these are the two import stubs at `0x46c6d4` and `0x46c6c8`. Each site becomes
  `jmp <SSE code>; nop` (or `call ...; nop`), which is the same 6 bytes, so
  nothing else moves.
- **With thcrap**, that becomes a thcrap patch: the SSE code goes in codecaves,
  and the redirects are binhacks with "expected" byte checks. For the original
  v1.00b, the generated file is byte-identical to the one in `thcrap-patch/`.
- **Without thcrap**, `th12_sse.exe` is a copy of `th12.exe` with a new code
  section (`.patchx`) holding the same machine code, the same redirects written in
  place, and an updated PE header and checksum. `--frameskip` also adds a small
  data section (`.patchw`) for the frameskip counters.

## Building and checking the fix

```sh
cd d3dx-sse-fix
./build.sh "<game folder>/th12.exe"     # -> d3dx_sse.obj, d3dx_sse.asm, thcrap-patch/d3dx_sse/

python3 -m venv venv && venv/bin/pip install -r requirements.txt
DLL=~/Library/Application\ Support/com.isaacmarovitz.Whisky/Libraries/Wine/lib/wine/i386-windows/d3dx9_40.dll
venv/bin/python verify.py "$DLL" d3dx_sse.obj                         # the compiled functions
venv/bin/python verify.py "$DLL" thcrap-patch/d3dx_sse/th12.v1.00b.js # the shipped bytes (no clang needed)
venv/bin/python verify.py "$DLL" "<game folder>/th12.exe"             # th12_sse.exe as patch_th12.py builds it,
                                                                      # called through the game's own stubs
```

How the replacement works:

- **Same arithmetic, same order as Wine.** A packed SSE row multiply adds the
  products in exactly the order Wine's loop does. d3d9 sets the x87 to single
  precision, so the results are bit-identical, not just close.
- **The combined matrix is built once per call.** Wine rebuilds it for every
  point.
- **Self-contained code.** Helpers are forced inline, and float constants are
  built from integer bits in registers. So each function's machine code has no
  calls and no data references, and works wherever it's placed. `make_patch.py`
  refuses the build if that's not true.

## Changing the frameskip ratio

Edit `fs_decide` in `frameskip-patch/thcrap-patch/frameskip_custom/th12.v1.00b.js`,
then run `patch_th12.py --frameskip` again. `83c002` is the number of frames drawn
(N). `83f803` and `83e803` are "out of how many" (M); change both. For example,
3 of 4 is `83c003`, `83f804`, `83e804`.

## Reproducing the investigation

```sh
# 1. which thread is saturated?
python3 monitoring/threadmon.py <wine pid of th12> 10

# 2. profile it (3 seconds), then attribute samples to Windows code
sample <pid> 3 -file th12_sample.txt
python3 analysis/attribute_profile.py th12_sample.txt \
    --pe "<game folder>/th12.exe" \
    --pe ~/Library/Application\ Support/com.isaacmarovitz.Whisky/Libraries/Wine/lib/wine/i386-windows

# 3. how bad is x87 under Rosetta?
x87-benchmarks/build.sh && x87-benchmarks/x87probe both 1 && x87-benchmarks/x87probe4

# 4. which games are x87-heavy?
python3 analysis/compare_x87.py "<game folder>/th12.exe" "<other game>/th16.exe"
```

Try step 2 on `analysis/example/th12_sample.txt` to see the original result:
about 19% in `d3dx9_40.dll!D3DXVec3Project` / `ProjectArray`.
