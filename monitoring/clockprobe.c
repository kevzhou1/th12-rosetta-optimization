// Estimates the effective CPU clock a thread gets at each QoS class, using a
// chain of dependent integer adds (1 cycle latency each on Apple cores).
// No root needed. Build: clang -O2 -o clockprobe clockprobe.c
#include <mach/mach_time.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/qos.h>

static double now_ns(void) {
    static mach_timebase_info_data_t tb;
    if (!tb.denom) mach_timebase_info(&tb);
    return (double)mach_absolute_time() * tb.numer / tb.denom;
}

static int cmp(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

typedef struct { qos_class_t qos; const char *name; double med, best; } job_t;

static void *run(void *arg) {
    job_t *j = arg;
    uint64_t x = 0;
    enum { REPS = 15, ITERS = 1000000 }; // 100 adds/iter -> 1e8 cycles per rep
    double ghz[REPS];
    // warm-up ~300ms so DVFS can ramp
    double t_end = now_ns() + 300e6;
    while (now_ns() < t_end)
        for (int i = 0; i < 10000; i++) __asm__ volatile(".rept 100\n add %0, %0, #1\n .endr\n" : "+r"(x));
    for (int r = 0; r < REPS; r++) {
        double t0 = now_ns();
        for (int i = 0; i < ITERS; i++) __asm__ volatile(".rept 100\n add %0, %0, #1\n .endr\n" : "+r"(x));
        ghz[r] = (double)ITERS * 100.0 / (now_ns() - t0);
    }
    qsort(ghz, REPS, sizeof(double), cmp);
    j->med = ghz[REPS / 2];
    j->best = ghz[REPS - 1];
    return NULL;
}

int main(void) {
    job_t jobs[] = {
        {QOS_CLASS_USER_INTERACTIVE, "USER_INTERACTIVE"},
        {QOS_CLASS_DEFAULT, "DEFAULT (osu GameThreads)"},
        {QOS_CLASS_UTILITY, "UTILITY"},
        {QOS_CLASS_BACKGROUND, "BACKGROUND (E-core only)"},
    };
    for (size_t i = 0; i < sizeof jobs / sizeof *jobs; i++) {
        pthread_attr_t a;
        pthread_t t;
        pthread_attr_init(&a);
        pthread_attr_set_qos_class_np(&a, jobs[i].qos, 0);
        pthread_create(&t, &a, run, &jobs[i]);
        pthread_join(t, NULL);
        printf("%-28s median %.2f GHz   best %.2f GHz\n", jobs[i].name, jobs[i].med, jobs[i].best);
        fflush(stdout);
    }
    return 0;
}
