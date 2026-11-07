// Compare x87 vs SSE float throughput under Rosetta 2.
// Build: clang -arch x86_64 -O1 -o x87probe x87probe.c ; run: ./x87probe [x87|sse|both] [seconds]
#include <mach/mach_time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static double now_s(void) {
    static mach_timebase_info_data_t tb;
    if (!tb.denom) mach_timebase_info(&tb);
    return (double)mach_absolute_time() * tb.numer / tb.denom / 1e9;
}

// Touhou-ish bullet update: pos += speed * (cos a, sin a); a += da   (x87)
static void step_x87(float *x, float *y, float *a, int n) {
    for (int i = 0; i < n; i++) {
        __asm__ volatile(
            "flds %2\n\t"          // a
            "fsincos\n\t"          // st0=cos, st1=sin
            "fmuls %3\n\t"         // cos*speed
            "fadds %0\n\t"
            "fstps %0\n\t"         // x += ...
            "fmuls %3\n\t"         // sin*speed
            "fadds %1\n\t"
            "fstps %1\n\t"         // y += ...
            "flds %2\n\t"
            "fadds %4\n\t"
            "fstps %2\n\t"         // a += 0.01
            : "+m"(x[i]), "+m"(y[i]), "+m"(a[i])
            : "m"((float){2.5f}), "m"((float){0.01f}));
    }
}

#include <math.h>
static void step_sse(float *x, float *y, float *a, int n) {
    for (int i = 0; i < n; i++) {
        float s = sinf(a[i]), c = cosf(a[i]);
        x[i] += c * 2.5f; y[i] += s * 2.5f; a[i] += 0.01f;
    }
}

static double bench(void (*f)(float *, float *, float *, int), double secs) {
    enum { N = 2000 };
    static float x[N], y[N], a[N];
    for (int i = 0; i < N; i++) a[i] = i * 0.001f;
    long iters = 0;
    double t0 = now_s(), t;
    do { f(x, y, a, N); iters += N; } while ((t = now_s()) - t0 < secs);
    return iters / (t - t0) / 1e6;  // million bullet-updates per second
}

int main(int argc, char **argv) {
    const char *mode = argc > 1 ? argv[1] : "both";
    double secs = argc > 2 ? atof(argv[2]) : 2;
    if (!strcmp(mode, "x87") || !strcmp(mode, "both"))
        printf("x87 : %7.1f M bullet-updates/s\n", bench(step_x87, secs));
    if (!strcmp(mode, "sse") || !strcmp(mode, "both"))
        printf("SSE : %7.1f M bullet-updates/s\n", bench(step_sse, secs));
    return 0;
}
