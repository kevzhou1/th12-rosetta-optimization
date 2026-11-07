// Split the cost of MSVC inline float->int (fnstcw/fldcw/fistp/fldcw) under Rosetta,
// and compare to SSE cvttss2si on the same value.
#include <mach/mach_time.h>
#include <stdio.h>
static double now_s(void){static mach_timebase_info_data_t tb; if(!tb.denom) mach_timebase_info(&tb); return (double)mach_absolute_time()*tb.numer/tb.denom/1e9;}
static volatile float vf[256]; static volatile int vi[256];
static void full(int n){ for(int i=0;i<n;i++){ unsigned short cw,cw2; int r; __asm__ volatile("flds %3\n\tfnstcw %1\n\tmovw %1,%%ax\n\torw $0xc00,%%ax\n\tmovw %%ax,%2\n\tfldcw %2\n\tfistpl %0\n\tfldcw %1":"=m"(r),"=m"(cw),"=m"(cw2):"m"(vf[i&255]):"ax"); vi[i&255]=r; } }
static void cwonly(int n){ for(int i=0;i<n;i++){ unsigned short cw,cw2; __asm__ volatile("fnstcw %0\n\tmovw %0,%%ax\n\torw $0xc00,%%ax\n\tmovw %%ax,%1\n\tfldcw %1\n\tfldcw %0":"=m"(cw),"=m"(cw2)::"ax"); } }
static void fistonly(int n){ for(int i=0;i<n;i++){ int r; __asm__ volatile("flds %1\n\tfistpl %0":"=m"(r):"m"(vf[i&255])); vi[i&255]=r; } }
static void sse_fromx87(int n){ for(int i=0;i<n;i++){ int r; float t; __asm__ volatile("flds %2\n\tfstps %1\n\tcvttss2si %1,%0":"=r"(r),"=m"(t):"m"(vf[i&255])); vi[i&255]=r; } }
static void fldfstp(int n){ for(int i=0;i<n;i++){ float t; __asm__ volatile("flds %1\n\tfstps %0":"=m"(t):"m"(vf[i&255])); } }
static double bench(void(*f)(int)){ long it=0; double t0=now_s(),t; do{f(4096); it+=4096;}while((t=now_s())-t0<1.0); return it/(t-t0)/1e6; }
int main(void){ for(int i=0;i<256;i++) vf[i]=i*1.37f;
 printf("full inline ftol (fnstcw+2x fldcw+fistp): %7.2f M/s\n",bench(full));
 printf("  fnstcw + 2x fldcw only                : %7.2f M/s\n",bench(cwonly));
 printf("  fld + fistp only                      : %7.2f M/s\n",bench(fistonly));
 printf("fld + fstp + SSE cvttss2si (replacement): %7.2f M/s\n",bench(sse_fromx87));
 printf("  fld + fstp only                       : %7.2f M/s\n",bench(fldfstp));
 return 0; }
