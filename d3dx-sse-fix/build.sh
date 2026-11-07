#!/bin/sh
# Compile d3dx_sse.c into 32-bit Windows machine code (a COFF object), then
# generate the thcrap patch from it.
#
#   ./build.sh [path/to/th12.exe]     # exe is optional, used to validate the patch
#
# Flags: -ffreestanding (no C library), -msse2 -mfpmath=sse (no x87),
# -ffunction-sections (each function in its own section, so its bytes can be
# lifted out on their own), no unwind tables. make_patch.py refuses the result
# if anything needs relocation.
set -e
cd "$(dirname "$0")"
clang -target i686-pc-windows-msvc -ffreestanding -O2 -msse2 -mfpmath=sse -fno-builtin \
      -fno-stack-protector -ffunction-sections -fno-asynchronous-unwind-tables -fno-unwind-tables \
      -c d3dx_sse.c -o d3dx_sse.obj
objdump -d --x86-asm-syntax=intel --print-imm-hex d3dx_sse.obj > d3dx_sse.asm
python3 make_patch.py d3dx_sse.obj thcrap-patch/d3dx_sse "$@"
