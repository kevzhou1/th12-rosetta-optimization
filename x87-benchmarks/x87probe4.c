#include <mach/mach_time.h>
#include <stdio.h>
static double now_s(void){static mach_timebase_info_data_t tb; if(!tb.denom) mach_timebase_info(&tb); return (double)mach_absolute_time()*tb.numer/tb.denom/1e9;}
static volatile float vf[256];
#define OP(name, body) static void name(int n){ for(int i=0;i<n;i++){ float a=vf[i&255],b; __asm__ volatile(body : "=m"(b) : "m"(a) : "ax"); vf[(i+7)&255]=b*1e-9f+1.f; } }
OP(o_fmul,   "flds %1\n\tfmuls %1\n\tfstps %0")
OP(o_fsincos,"flds %1\n\tfsincos\n\tfstps %0\n\tfstps %0")
OP(o_fsin,   "flds %1\n\tfsin\n\tfstps %0")
OP(o_fpatan, "flds %1\n\tfld1\n\tfpatan\n\tfstps %0")
OP(o_fsqrt,  "flds %1\n\tfsqrt\n\tfstps %0")
OP(o_fcomp,  "flds %1\n\tfcomps %1\n\tfnstsw %%ax\n\tfldz\n\tfstps %0")
static double ns(void(*f)(int)){ long it=0; double t0=now_s(),t; do{f(4096); it+=4096;}while((t=now_s())-t0<0.7); return (t-t0)/it*1e9; }
int main(void){ for(int i=0;i<256;i++) vf[i]=1.f+i*0.01f;
 printf("fld+fmul+fstp     %7.1f ns\n",ns(o_fmul));
 printf("fld+fcomp+fnstsw  %7.1f ns\n",ns(o_fcomp));
 printf("fld+fsqrt+fstp    %7.1f ns\n",ns(o_fsqrt));
 printf("fld+fsin+fstp     %7.1f ns\n",ns(o_fsin));
 printf("fld+fsincos+2fstp %7.1f ns\n",ns(o_fsincos));
 printf("fld+fpatan+fstp   %7.1f ns\n",ns(o_fpatan));
}
