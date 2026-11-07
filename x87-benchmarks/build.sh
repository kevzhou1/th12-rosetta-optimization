#!/bin/sh
# Build the x87-vs-SSE microbenchmarks as x86_64 binaries so they run under Rosetta.
#   x87probe   bullet-style update (sincos, mul, add): x87 vs SSE throughput
#   x87probe2  MSVC-2005-era patterns: compare+fnstsw, float->int via fldcw, fxch stack math
#              (profile these with `sample` to see which libRosettaRuntime offsets each hits)
#   x87probe3  splits the float->int conversion cost (fnstcw/fldcw vs fistp vs SSE cvttss2si)
#   x87probe4  approximate cost per x87 instruction (fmul, fcomp+fnstsw, fsqrt, fsin, fsincos, fpatan)
set -e
cd "$(dirname "$0")"
for p in x87probe x87probe2 x87probe3 x87probe4; do
    clang -arch x86_64 -O1 -o "$p" "$p.c"
done
echo "built: x87probe (./x87probe [x87|sse|both] [secs]), x87probe2 ([cmp|ftol|stack|all] [secs]), x87probe3, x87probe4"
