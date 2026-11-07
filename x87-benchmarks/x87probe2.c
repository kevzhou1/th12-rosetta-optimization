// x87 patterns typical of MSVC 2005-era game code, run under Rosetta.
#include <mach/mach_time.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static double now_s(void){static mach_timebase_info_data_t tb; if(!tb.denom) mach_timebase_info(&tb); return (double)mach_absolute_time()*tb.numer/tb.denom/1e9;}
static volatile float vf[256]; static volatile int vi[256];
// compare: fld; fcomp; fnstsw ax; test ah,0x41; (bounds check like "if (x < 0 || x > 384)")
static void cmp(int n){ for(int i=0;i<n;i++){ int r; __asm__ volatile("flds %1\n\tfcomps %2\n\tfnstsw %%ax\n\tmovzbl %%ah,%0" : "=r"(r) : "m"(vf[i&255]), "m"(vf[(i+1)&255]) : "ax"); vi[i&255]=r; } }
// ftol: MSVC _ftol style float->int with rounding-mode change
static void ftol(int n){ for(int i=0;i<n;i++){ unsigned short cw, cw2; int r; __asm__ volatile("flds %3\n\tfnstcw %1\n\tmovw %1,%%ax\n\torw $0xc00,%%ax\n\tmovw %%ax,%2\n\tfldcw %2\n\tfistpl %0\n\tfldcw %1" : "=m"(r), "=m"(cw), "=m"(cw2) : "m"(vf[i&255]) : "ax"); vi[i&255]=r; } }
// fxch/fld st(i) arithmetic stack shuffling
static void stack(int n){ for(int i=0;i<n;i++){ __asm__ volatile("flds %0\n\tflds %1\n\tfxch\n\tfld %%st(1)\n\tfmulp\n\tfaddp\n\tfstps %0" : "+m"(vf[i&255]) : "m"(vf[(i+3)&255])); } }
static double bench(void(*f)(int), double s){ long it=0; double t0=now_s(),t; do{f(4096); it+=4096;}while((t=now_s())-t0<s); return it/(t-t0)/1e6; }
int main(int c, char**v){ for(int i=0;i<256;i++) vf[i]=i*1.5f;
  const char*m=c>1?v[1]:"all"; double s=c>2?atof(v[2]):1.5;
  if(!strcmp(m,"cmp")||!strcmp(m,"all")) printf("compare+fnstsw : %6.1f M/s\n", bench(cmp,s));
  if(!strcmp(m,"ftol")||!strcmp(m,"all")) printf("ftol (fldcw)   : %6.1f M/s\n", bench(ftol,s));
  if(!strcmp(m,"stack")||!strcmp(m,"all")) printf("fxch/st(i) math: %6.1f M/s\n", bench(stack,s));
  return 0; }
