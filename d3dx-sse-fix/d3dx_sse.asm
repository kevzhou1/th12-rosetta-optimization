
d3dx_sse.obj:	file format coff-i386

Disassembly of section .text:

00000000 <_sse_Vec3Project@24>:
       0: 83 ec 70                     	sub	esp, 0x70
       3: 8b 84 24 88 00 00 00         	mov	eax, dword ptr [esp + 0x88]
       a: 8b 8c 24 84 00 00 00         	mov	ecx, dword ptr [esp + 0x84]
      11: ba 00 00 80 3f               	mov	edx, 0x3f800000
      16: 66 0f 6e ca                  	movd	xmm1, edx
      1a: 0f c6 c9 00                  	shufps	xmm1, xmm1, 0x0         # xmm1 = xmm1[0,0,0,0]
      1e: 0f 57 e4                     	xorps	xmm4, xmm4
      21: 85 c0                        	test	eax, eax
      23: 0f 11 4c 24 60               	movups	xmmword ptr [esp + 0x60], xmm1
      28: 74 62                        	je	0x8c <_sse_Vec3Project@24+0x8c>
      2a: 0f 10 00                     	movups	xmm0, xmmword ptr [eax]
      2d: 0f 10 58 10                  	movups	xmm3, xmmword ptr [eax + 0x10]
      31: 0f 10 70 20                  	movups	xmm6, xmmword ptr [eax + 0x20]
      35: 0f c6 c9 00                  	shufps	xmm1, xmm1, 0x0         # xmm1 = xmm1[0,0,0,0]
      39: 0f 28 e8                     	movaps	xmm5, xmm0
      3c: 0f 59 e9                     	mulps	xmm5, xmm1
      3f: 0f 28 d3                     	movaps	xmm2, xmm3
      42: 0f 59 d4                     	mulps	xmm2, xmm4
      45: 0f 11 14 24                  	movups	xmmword ptr [esp], xmm2
      49: 0f 28 fe                     	movaps	xmm7, xmm6
      4c: 0f 59 fc                     	mulps	xmm7, xmm4
      4f: 0f 59 d9                     	mulps	xmm3, xmm1
      52: 0f 59 f1                     	mulps	xmm6, xmm1
      55: 0f 10 50 30                  	movups	xmm2, xmmword ptr [eax + 0x30]
      59: 0f 59 ca                     	mulps	xmm1, xmm2
      5c: 0f 59 d4                     	mulps	xmm2, xmm4
      5f: 0f 59 c4                     	mulps	xmm0, xmm4
      62: 0f 10 24 24                  	movups	xmm4, xmmword ptr [esp]
      66: 0f 58 ec                     	addps	xmm5, xmm4
      69: 0f 58 d8                     	addps	xmm3, xmm0
      6c: 0f 58 c4                     	addps	xmm0, xmm4
      6f: 0f 58 ef                     	addps	xmm5, xmm7
      72: 0f 58 ea                     	addps	xmm5, xmm2
      75: 0f 58 df                     	addps	xmm3, xmm7
      78: 0f 58 da                     	addps	xmm3, xmm2
      7b: 0f 58 f0                     	addps	xmm6, xmm0
      7e: 0f 58 f2                     	addps	xmm6, xmm2
      81: 0f 58 c7                     	addps	xmm0, xmm7
      84: 0f 58 c8                     	addps	xmm1, xmm0
      87: 0f 28 e5                     	movaps	xmm4, xmm5
      8a: eb 19                        	jmp	0xa5 <_sse_Vec3Project@24+0xa5>
      8c: f3 0f 10 e1                  	movss	xmm4, xmm1              # xmm4 = xmm1[0],xmm4[1,2,3]
      90: 0f 28 dc                     	movaps	xmm3, xmm4
      93: 0f c6 dc 51                  	shufps	xmm3, xmm4, 0x51        # xmm3 = xmm3[1,0],xmm4[1,1]
      97: 0f 28 f4                     	movaps	xmm6, xmm4
      9a: 0f c6 f4 45                  	shufps	xmm6, xmm4, 0x45        # xmm6 = xmm6[1,1],xmm4[0,1]
      9e: 0f 28 cc                     	movaps	xmm1, xmm4
      a1: 0f c6 cc 15                  	shufps	xmm1, xmm4, 0x15        # xmm1 = xmm1[1,1],xmm4[1,0]
      a5: 8b 84 24 80 00 00 00         	mov	eax, dword ptr [esp + 0x80]
      ac: 85 c9                        	test	ecx, ecx
      ae: 0f 84 0c 01 00 00            	je	0x1c0 <_sse_Vec3Project@24+0x1c0>
      b4: 0f 10 29                     	movups	xmm5, xmmword ptr [ecx]
      b7: 0f 11 6c 24 10               	movups	xmmword ptr [esp + 0x10], xmm5
      bc: 0f 10 41 10                  	movups	xmm0, xmmword ptr [ecx + 0x10]
      c0: 0f 11 44 24 30               	movups	xmmword ptr [esp + 0x30], xmm0
      c5: 0f 10 51 20                  	movups	xmm2, xmmword ptr [ecx + 0x20]
      c9: 0f 11 54 24 20               	movups	xmmword ptr [esp + 0x20], xmm2
      ce: 0f 10 79 30                  	movups	xmm7, xmmword ptr [ecx + 0x30]
      d2: 0f 11 7c 24 40               	movups	xmmword ptr [esp + 0x40], xmm7
      d7: 0f 28 c4                     	movaps	xmm0, xmm4
      da: 0f c6 c4 00                  	shufps	xmm0, xmm4, 0x0         # xmm0 = xmm0[0,0],xmm4[0,0]
      de: 0f 59 c5                     	mulps	xmm0, xmm5
      e1: 0f 11 34 24                  	movups	xmmword ptr [esp], xmm6
      e5: 0f 28 f4                     	movaps	xmm6, xmm4
      e8: 0f c6 f4 55                  	shufps	xmm6, xmm4, 0x55        # xmm6 = xmm6[1,1],xmm4[1,1]
      ec: 0f 10 6c 24 30               	movups	xmm5, xmmword ptr [esp + 0x30]
      f1: 0f 59 f5                     	mulps	xmm6, xmm5
      f4: 0f 58 f0                     	addps	xmm6, xmm0
      f7: 0f 28 c4                     	movaps	xmm0, xmm4
      fa: 0f c6 c4 aa                  	shufps	xmm0, xmm4, 0xaa        # xmm0 = xmm0[2,2],xmm4[2,2]
      fe: 0f 59 c2                     	mulps	xmm0, xmm2
     101: 0f 58 c6                     	addps	xmm0, xmm6
     104: 0f c6 e4 ff                  	shufps	xmm4, xmm4, 0xff        # xmm4 = xmm4[3,3,3,3]
     108: 0f 59 e7                     	mulps	xmm4, xmm7
     10b: 0f 58 e0                     	addps	xmm4, xmm0
     10e: 0f 11 64 24 50               	movups	xmmword ptr [esp + 0x50], xmm4
     113: 0f 28 e3                     	movaps	xmm4, xmm3
     116: 0f c6 e3 00                  	shufps	xmm4, xmm3, 0x0         # xmm4 = xmm4[0,0],xmm3[0,0]
     11a: 0f 10 54 24 10               	movups	xmm2, xmmword ptr [esp + 0x10]
     11f: 0f 59 e2                     	mulps	xmm4, xmm2
     122: 0f 28 f3                     	movaps	xmm6, xmm3
     125: 0f c6 f3 55                  	shufps	xmm6, xmm3, 0x55        # xmm6 = xmm6[1,1],xmm3[1,1]
     129: 0f 28 fd                     	movaps	xmm7, xmm5
     12c: 0f 59 f5                     	mulps	xmm6, xmm5
     12f: 0f 58 f4                     	addps	xmm6, xmm4
     132: 0f 28 e3                     	movaps	xmm4, xmm3
     135: 0f c6 e3 aa                  	shufps	xmm4, xmm3, 0xaa        # xmm4 = xmm4[2,2],xmm3[2,2]
     139: 0f 10 6c 24 20               	movups	xmm5, xmmword ptr [esp + 0x20]
     13e: 0f 59 e5                     	mulps	xmm4, xmm5
     141: 0f 58 e6                     	addps	xmm4, xmm6
     144: 0f c6 db ff                  	shufps	xmm3, xmm3, 0xff        # xmm3 = xmm3[3,3,3,3]
     148: 0f 10 44 24 40               	movups	xmm0, xmmword ptr [esp + 0x40]
     14d: 0f 59 d8                     	mulps	xmm3, xmm0
     150: 0f 58 dc                     	addps	xmm3, xmm4
     153: 0f 10 24 24                  	movups	xmm4, xmmword ptr [esp]
     157: 0f c6 e4 00                  	shufps	xmm4, xmm4, 0x0         # xmm4 = xmm4[0,0,0,0]
     15b: 0f 59 e2                     	mulps	xmm4, xmm2
     15e: 0f 10 34 24                  	movups	xmm6, xmmword ptr [esp]
     162: 0f c6 f6 55                  	shufps	xmm6, xmm6, 0x55        # xmm6 = xmm6[1,1,1,1]
     166: 0f 59 f7                     	mulps	xmm6, xmm7
     169: 0f 58 f4                     	addps	xmm6, xmm4
     16c: 0f 10 24 24                  	movups	xmm4, xmmword ptr [esp]
     170: 0f c6 e4 aa                  	shufps	xmm4, xmm4, 0xaa        # xmm4 = xmm4[2,2,2,2]
     174: 0f 59 e5                     	mulps	xmm4, xmm5
     177: 0f 58 e6                     	addps	xmm4, xmm6
     17a: 0f 10 34 24                  	movups	xmm6, xmmword ptr [esp]
     17e: 0f c6 f6 ff                  	shufps	xmm6, xmm6, 0xff        # xmm6 = xmm6[3,3,3,3]
     182: 0f 59 f0                     	mulps	xmm6, xmm0
     185: 0f 28 d0                     	movaps	xmm2, xmm0
     188: 0f 58 f4                     	addps	xmm6, xmm4
     18b: 0f 28 e1                     	movaps	xmm4, xmm1
     18e: 0f c6 e1 00                  	shufps	xmm4, xmm1, 0x0         # xmm4 = xmm4[0,0],xmm1[0,0]
     192: 0f 10 44 24 10               	movups	xmm0, xmmword ptr [esp + 0x10]
     197: 0f 59 e0                     	mulps	xmm4, xmm0
     19a: 0f 28 c1                     	movaps	xmm0, xmm1
     19d: 0f c6 c1 55                  	shufps	xmm0, xmm1, 0x55        # xmm0 = xmm0[1,1],xmm1[1,1]
     1a1: 0f 59 c7                     	mulps	xmm0, xmm7
     1a4: 0f 58 c4                     	addps	xmm0, xmm4
     1a7: 0f 28 e1                     	movaps	xmm4, xmm1
     1aa: 0f c6 e1 aa                  	shufps	xmm4, xmm1, 0xaa        # xmm4 = xmm4[2,2],xmm1[2,2]
     1ae: 0f 59 e5                     	mulps	xmm4, xmm5
     1b1: 0f 58 e0                     	addps	xmm4, xmm0
     1b4: 0f c6 c9 ff                  	shufps	xmm1, xmm1, 0xff        # xmm1 = xmm1[3,3,3,3]
     1b8: 0f 59 ca                     	mulps	xmm1, xmm2
     1bb: 0f 58 cc                     	addps	xmm1, xmm4
     1be: eb 05                        	jmp	0x1c5 <_sse_Vec3Project@24+0x1c5>
     1c0: 0f 11 64 24 50               	movups	xmmword ptr [esp + 0x50], xmm4
     1c5: 8b 4c 24 7c                  	mov	ecx, dword ptr [esp + 0x7c]
     1c9: 8b 54 24 78                  	mov	edx, dword ptr [esp + 0x78]
     1cd: 85 c0                        	test	eax, eax
     1cf: 0f 84 0e 01 00 00            	je	0x2e3 <_sse_Vec3Project@24+0x2e3>
     1d5: 0f 10 38                     	movups	xmm7, xmmword ptr [eax]
     1d8: 0f 11 7c 24 10               	movups	xmmword ptr [esp + 0x10], xmm7
     1dd: 0f 10 40 10                  	movups	xmm0, xmmword ptr [eax + 0x10]
     1e1: 0f 10 68 20                  	movups	xmm5, xmmword ptr [eax + 0x20]
     1e5: 0f 11 6c 24 40               	movups	xmmword ptr [esp + 0x40], xmm5
     1ea: 0f 10 50 30                  	movups	xmm2, xmmword ptr [eax + 0x30]
     1ee: 0f 11 54 24 20               	movups	xmmword ptr [esp + 0x20], xmm2
     1f3: 0f 10 54 24 50               	movups	xmm2, xmmword ptr [esp + 0x50]
     1f8: 0f 28 e2                     	movaps	xmm4, xmm2
     1fb: 0f c6 e2 00                  	shufps	xmm4, xmm2, 0x0         # xmm4 = xmm4[0,0],xmm2[0,0]
     1ff: 0f 59 e7                     	mulps	xmm4, xmm7
     202: 0f 11 34 24                  	movups	xmmword ptr [esp], xmm6
     206: 0f 28 f2                     	movaps	xmm6, xmm2
     209: 0f c6 f2 55                  	shufps	xmm6, xmm2, 0x55        # xmm6 = xmm6[1,1],xmm2[1,1]
     20d: 0f 59 f0                     	mulps	xmm6, xmm0
     210: 0f 28 f8                     	movaps	xmm7, xmm0
     213: 0f 11 44 24 30               	movups	xmmword ptr [esp + 0x30], xmm0
     218: 0f 58 f4                     	addps	xmm6, xmm4
     21b: 0f 28 e2                     	movaps	xmm4, xmm2
     21e: 0f c6 e2 aa                  	shufps	xmm4, xmm2, 0xaa        # xmm4 = xmm4[2,2],xmm2[2,2]
     222: 0f 59 e5                     	mulps	xmm4, xmm5
     225: 0f 58 e6                     	addps	xmm4, xmm6
     228: 0f c6 d2 ff                  	shufps	xmm2, xmm2, 0xff        # xmm2 = xmm2[3,3,3,3]
     22c: 0f 10 44 24 20               	movups	xmm0, xmmword ptr [esp + 0x20]
     231: 0f 59 d0                     	mulps	xmm2, xmm0
     234: 0f 58 d4                     	addps	xmm2, xmm4
     237: 0f 28 e3                     	movaps	xmm4, xmm3
     23a: 0f c6 e3 00                  	shufps	xmm4, xmm3, 0x0         # xmm4 = xmm4[0,0],xmm3[0,0]
     23e: 0f 10 6c 24 10               	movups	xmm5, xmmword ptr [esp + 0x10]
     243: 0f 59 e5                     	mulps	xmm4, xmm5
     246: 0f 28 f3                     	movaps	xmm6, xmm3
     249: 0f c6 f3 55                  	shufps	xmm6, xmm3, 0x55        # xmm6 = xmm6[1,1],xmm3[1,1]
     24d: 0f 59 f7                     	mulps	xmm6, xmm7
     250: 0f 58 f4                     	addps	xmm6, xmm4
     253: 0f 28 e3                     	movaps	xmm4, xmm3
     256: 0f c6 e3 aa                  	shufps	xmm4, xmm3, 0xaa        # xmm4 = xmm4[2,2],xmm3[2,2]
     25a: 0f 10 7c 24 40               	movups	xmm7, xmmword ptr [esp + 0x40]
     25f: 0f 59 e7                     	mulps	xmm4, xmm7
     262: 0f 58 e6                     	addps	xmm4, xmm6
     265: 0f c6 db ff                  	shufps	xmm3, xmm3, 0xff        # xmm3 = xmm3[3,3,3,3]
     269: 0f 59 d8                     	mulps	xmm3, xmm0
     26c: 0f 58 dc                     	addps	xmm3, xmm4
     26f: 0f 10 24 24                  	movups	xmm4, xmmword ptr [esp]
     273: 0f c6 e4 00                  	shufps	xmm4, xmm4, 0x0         # xmm4 = xmm4[0,0,0,0]
     277: 0f 59 e5                     	mulps	xmm4, xmm5
     27a: 0f 10 34 24                  	movups	xmm6, xmmword ptr [esp]
     27e: 0f c6 f6 55                  	shufps	xmm6, xmm6, 0x55        # xmm6 = xmm6[1,1,1,1]
     282: 0f 10 6c 24 30               	movups	xmm5, xmmword ptr [esp + 0x30]
     287: 0f 59 f5                     	mulps	xmm6, xmm5
     28a: 0f 58 f4                     	addps	xmm6, xmm4
     28d: 0f 10 24 24                  	movups	xmm4, xmmword ptr [esp]
     291: 0f c6 e4 aa                  	shufps	xmm4, xmm4, 0xaa        # xmm4 = xmm4[2,2,2,2]
     295: 0f 59 e7                     	mulps	xmm4, xmm7
     298: 0f 58 e6                     	addps	xmm4, xmm6
     29b: 0f 10 34 24                  	movups	xmm6, xmmword ptr [esp]
     29f: 0f c6 f6 ff                  	shufps	xmm6, xmm6, 0xff        # xmm6 = xmm6[3,3,3,3]
     2a3: 0f 59 f0                     	mulps	xmm6, xmm0
     2a6: 0f 58 f4                     	addps	xmm6, xmm4
     2a9: 0f 28 e1                     	movaps	xmm4, xmm1
     2ac: 0f c6 e1 00                  	shufps	xmm4, xmm1, 0x0         # xmm4 = xmm4[0,0],xmm1[0,0]
     2b0: 0f 10 44 24 10               	movups	xmm0, xmmword ptr [esp + 0x10]
     2b5: 0f 59 e0                     	mulps	xmm4, xmm0
     2b8: 0f 28 c1                     	movaps	xmm0, xmm1
     2bb: 0f c6 c1 55                  	shufps	xmm0, xmm1, 0x55        # xmm0 = xmm0[1,1],xmm1[1,1]
     2bf: 0f 59 c5                     	mulps	xmm0, xmm5
     2c2: 0f 58 c4                     	addps	xmm0, xmm4
     2c5: 0f 28 e1                     	movaps	xmm4, xmm1
     2c8: 0f c6 e1 aa                  	shufps	xmm4, xmm1, 0xaa        # xmm4 = xmm4[2,2],xmm1[2,2]
     2cc: 0f 59 e7                     	mulps	xmm4, xmm7
     2cf: 0f 58 e0                     	addps	xmm4, xmm0
     2d2: 0f c6 c9 ff                  	shufps	xmm1, xmm1, 0xff        # xmm1 = xmm1[3,3,3,3]
     2d6: 0f 10 44 24 20               	movups	xmm0, xmmword ptr [esp + 0x20]
     2db: 0f 59 c8                     	mulps	xmm1, xmm0
     2de: 0f 58 cc                     	addps	xmm1, xmm4
     2e1: eb 05                        	jmp	0x2e8 <_sse_Vec3Project@24+0x2e8>
     2e3: 0f 10 54 24 50               	movups	xmm2, xmmword ptr [esp + 0x50]
     2e8: 8b 44 24 74                  	mov	eax, dword ptr [esp + 0x74]
     2ec: f3 0f 10 02                  	movss	xmm0, dword ptr [edx]   # xmm0 = mem[0],zero,zero,zero
     2f0: f3 0f 10 6a 04               	movss	xmm5, dword ptr [edx + 0x4] # xmm5 = mem[0],zero,zero,zero
     2f5: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     2f9: 0f 59 c2                     	mulps	xmm0, xmm2
     2fc: 0f c6 ed 00                  	shufps	xmm5, xmm5, 0x0         # xmm5 = xmm5[0,0,0,0]
     300: 0f 59 eb                     	mulps	xmm5, xmm3
     303: 0f 58 e8                     	addps	xmm5, xmm0
     306: f3 0f 10 42 08               	movss	xmm0, dword ptr [edx + 0x8] # xmm0 = mem[0],zero,zero,zero
     30b: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     30f: 0f 59 c6                     	mulps	xmm0, xmm6
     312: 0f 58 c5                     	addps	xmm0, xmm5
     315: 0f 58 c1                     	addps	xmm0, xmm1
     318: 0f 28 c8                     	movaps	xmm1, xmm0
     31b: 0f c6 c8 ff                  	shufps	xmm1, xmm0, 0xff        # xmm1 = xmm1[3,3],xmm0[3,3]
     31f: 0f 5e c1                     	divps	xmm0, xmm1
     322: 85 c9                        	test	ecx, ecx
     324: 74 79                        	je	0x39f <_sse_Vec3Project@24+0x39f>
     326: 0f 57 e4                     	xorps	xmm4, xmm4
     329: f3 0f 2a 21                  	cvtsi2ss	xmm4, dword ptr [ecx]
     32d: 0f 57 d2                     	xorps	xmm2, xmm2
     330: f3 0f 2a 51 08               	cvtsi2ss	xmm2, dword ptr [ecx + 0x8]
     335: 0f 57 db                     	xorps	xmm3, xmm3
     338: f3 0f 2a 59 0c               	cvtsi2ss	xmm3, dword ptr [ecx + 0xc]
     33d: ba 00 00 00 3f               	mov	edx, 0x3f000000
     342: 0f 10 6c 24 60               	movups	xmm5, xmmword ptr [esp + 0x60]
     347: 0f 28 cd                     	movaps	xmm1, xmm5
     34a: f3 0f 58 c8                  	addss	xmm1, xmm0
     34e: f3 0f 59 ca                  	mulss	xmm1, xmm2
     352: 66 0f 6e d2                  	movd	xmm2, edx
     356: 0f c6 d2 00                  	shufps	xmm2, xmm2, 0x0         # xmm2 = xmm2[0,0,0,0]
     35a: f3 0f 59 ca                  	mulss	xmm1, xmm2
     35e: f3 0f 58 cc                  	addss	xmm1, xmm4
     362: 0f 28 e0                     	movaps	xmm4, xmm0
     365: 0f c6 e0 55                  	shufps	xmm4, xmm0, 0x55        # xmm4 = xmm4[1,1],xmm0[1,1]
     369: f3 0f 5c ec                  	subss	xmm5, xmm4
     36d: f3 0f 10 61 10               	movss	xmm4, dword ptr [ecx + 0x10] # xmm4 = mem[0],zero,zero,zero
     372: f3 0f 59 eb                  	mulss	xmm5, xmm3
     376: f3 0f 10 59 14               	movss	xmm3, dword ptr [ecx + 0x14] # xmm3 = mem[0],zero,zero,zero
     37b: f3 0f 5c dc                  	subss	xmm3, xmm4
     37f: 0f 14 eb                     	unpcklps	xmm5, xmm3              # xmm5 = xmm5[0],xmm3[0],xmm5[1],xmm3[1]
     382: 0f 12 c0                     	movhlps	xmm0, xmm0              # xmm0 = xmm0[1,1]
     385: 0f 14 d0                     	unpcklps	xmm2, xmm0              # xmm2 = xmm2[0],xmm0[0],xmm2[1],xmm0[1]
     388: 0f 57 c0                     	xorps	xmm0, xmm0
     38b: f3 0f 2a 41 04               	cvtsi2ss	xmm0, dword ptr [ecx + 0x4]
     390: 0f 59 d5                     	mulps	xmm2, xmm5
     393: 0f 14 c4                     	unpcklps	xmm0, xmm4              # xmm0 = xmm0[0],xmm4[0],xmm0[1],xmm4[1]
     396: 0f 58 c2                     	addps	xmm0, xmm2
     399: f3 0f 11 08                  	movss	dword ptr [eax], xmm1
     39d: eb 08                        	jmp	0x3a7 <_sse_Vec3Project@24+0x3a7>
     39f: f3 0f 11 00                  	movss	dword ptr [eax], xmm0
     3a3: 0f c6 c0 e9                  	shufps	xmm0, xmm0, 0xe9        # xmm0 = xmm0[1,2,2,3]
     3a7: 0f 13 40 04                  	movlps	qword ptr [eax + 0x4], xmm0
     3ab: 83 c4 70                     	add	esp, 0x70
     3ae: c2 18 00                     	ret	0x18

Disassembly of section .text:

00000000 <_sse_Vec3ProjectArray@36>:
       0: 55                           	push	ebp
       1: 53                           	push	ebx
       2: 57                           	push	edi
       3: 56                           	push	esi
       4: 83 ec 58                     	sub	esp, 0x58
       7: 8b 8c 24 8c 00 00 00         	mov	ecx, dword ptr [esp + 0x8c]
       e: 8b 44 24 6c                  	mov	eax, dword ptr [esp + 0x6c]
      12: 85 c9                        	test	ecx, ecx
      14: 0f 84 1e 04 00 00            	je	0x438 <_sse_Vec3ProjectArray@36+0x438>
      1a: 8b 94 24 88 00 00 00         	mov	edx, dword ptr [esp + 0x88]
      21: 8b b4 24 84 00 00 00         	mov	esi, dword ptr [esp + 0x84]
      28: bf 00 00 80 3f               	mov	edi, 0x3f800000
      2d: 66 0f 6e c7                  	movd	xmm0, edi
      31: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
      35: 0f 57 d2                     	xorps	xmm2, xmm2
      38: 0f 28 c8                     	movaps	xmm1, xmm0
      3b: 0f c6 c8 00                  	shufps	xmm1, xmm0, 0x0         # xmm1 = xmm1[0,0],xmm0[0,0]
      3f: 0f 11 4c 24 38               	movups	xmmword ptr [esp + 0x38], xmm1
      44: 85 d2                        	test	edx, edx
      46: 74 7f                        	je	0xc7 <_sse_Vec3ProjectArray@36+0xc7>
      48: 0f 10 0a                     	movups	xmm1, xmmword ptr [edx]
      4b: 0f 10 62 10                  	movups	xmm4, xmmword ptr [edx + 0x10]
      4f: 0f 10 5a 20                  	movups	xmm3, xmmword ptr [edx + 0x20]
      53: 0f 10 7a 30                  	movups	xmm7, xmmword ptr [edx + 0x30]
      57: 0f 28 c4                     	movaps	xmm0, xmm4
      5a: 0f 59 c2                     	mulps	xmm0, xmm2
      5d: 0f 11 04 24                  	movups	xmmword ptr [esp], xmm0
      61: 0f 57 ed                     	xorps	xmm5, xmm5
      64: 0f 28 d3                     	movaps	xmm2, xmm3
      67: 0f 59 d5                     	mulps	xmm2, xmm5
      6a: 0f 28 f7                     	movaps	xmm6, xmm7
      6d: 0f 59 f5                     	mulps	xmm6, xmm5
      70: 0f 28 c1                     	movaps	xmm0, xmm1
      73: 0f 59 cd                     	mulps	xmm1, xmm5
      76: 0f 10 6c 24 38               	movups	xmm5, xmmword ptr [esp + 0x38]
      7b: 0f 59 c5                     	mulps	xmm0, xmm5
      7e: 0f 10 2c 24                  	movups	xmm5, xmmword ptr [esp]
      82: 0f 58 c5                     	addps	xmm0, xmm5
      85: 0f 10 6c 24 38               	movups	xmm5, xmmword ptr [esp + 0x38]
      8a: 0f 59 e5                     	mulps	xmm4, xmm5
      8d: 0f 58 e1                     	addps	xmm4, xmm1
      90: 0f 10 2c 24                  	movups	xmm5, xmmword ptr [esp]
      94: 0f 58 cd                     	addps	xmm1, xmm5
      97: 0f 10 6c 24 38               	movups	xmm5, xmmword ptr [esp + 0x38]
      9c: 0f 58 c2                     	addps	xmm0, xmm2
      9f: 0f 58 c6                     	addps	xmm0, xmm6
      a2: 0f 58 e2                     	addps	xmm4, xmm2
      a5: 0f 58 e6                     	addps	xmm4, xmm6
      a8: 0f 11 64 24 18               	movups	xmmword ptr [esp + 0x18], xmm4
      ad: 0f 59 dd                     	mulps	xmm3, xmm5
      b0: 0f 58 d9                     	addps	xmm3, xmm1
      b3: 0f 58 de                     	addps	xmm3, xmm6
      b6: 0f 28 e3                     	movaps	xmm4, xmm3
      b9: 0f 58 ca                     	addps	xmm1, xmm2
      bc: 0f 59 fd                     	mulps	xmm7, xmm5
      bf: 0f 58 f9                     	addps	xmm7, xmm1
      c2: 0f 28 d0                     	movaps	xmm2, xmm0
      c5: eb 21                        	jmp	0xe8 <_sse_Vec3ProjectArray@36+0xe8>
      c7: f3 0f 10 d0                  	movss	xmm2, xmm0              # xmm2 = xmm0[0],xmm2[1,2,3]
      cb: 0f 28 c2                     	movaps	xmm0, xmm2
      ce: 0f c6 c2 51                  	shufps	xmm0, xmm2, 0x51        # xmm0 = xmm0[1,0],xmm2[1,1]
      d2: 0f 11 44 24 18               	movups	xmmword ptr [esp + 0x18], xmm0
      d7: 0f 28 c2                     	movaps	xmm0, xmm2
      da: 0f c6 c2 45                  	shufps	xmm0, xmm2, 0x45        # xmm0 = xmm0[1,1],xmm2[0,1]
      de: 0f 28 e0                     	movaps	xmm4, xmm0
      e1: 0f 28 fa                     	movaps	xmm7, xmm2
      e4: 0f c6 fa 15                  	shufps	xmm7, xmm2, 0x15        # xmm7 = xmm7[1,1],xmm2[1,0]
      e8: 0f 11 54 24 28               	movups	xmmword ptr [esp + 0x28], xmm2
      ed: 8b 94 24 80 00 00 00         	mov	edx, dword ptr [esp + 0x80]
      f4: 85 f6                        	test	esi, esi
      f6: 0f 84 e5 00 00 00            	je	0x1e1 <_sse_Vec3ProjectArray@36+0x1e1>
      fc: 0f 10 2e                     	movups	xmm5, xmmword ptr [esi]
      ff: 0f 11 3c 24                  	movups	xmmword ptr [esp], xmm7
     103: 0f 10 7e 10                  	movups	xmm7, xmmword ptr [esi + 0x10]
     107: 0f 10 76 20                  	movups	xmm6, xmmword ptr [esi + 0x20]
     10b: 0f 10 5e 30                  	movups	xmm3, xmmword ptr [esi + 0x30]
     10f: 0f 10 44 24 28               	movups	xmm0, xmmword ptr [esp + 0x28]
     114: 0f 28 d0                     	movaps	xmm2, xmm0
     117: 0f c6 d0 00                  	shufps	xmm2, xmm0, 0x0         # xmm2 = xmm2[0,0],xmm0[0,0]
     11b: 0f 59 d5                     	mulps	xmm2, xmm5
     11e: 0f 28 c8                     	movaps	xmm1, xmm0
     121: 0f c6 c8 55                  	shufps	xmm1, xmm0, 0x55        # xmm1 = xmm1[1,1],xmm0[1,1]
     125: 0f 59 cf                     	mulps	xmm1, xmm7
     128: 0f 58 ca                     	addps	xmm1, xmm2
     12b: 0f 28 d0                     	movaps	xmm2, xmm0
     12e: 0f c6 d0 aa                  	shufps	xmm2, xmm0, 0xaa        # xmm2 = xmm2[2,2],xmm0[2,2]
     132: 0f 59 d6                     	mulps	xmm2, xmm6
     135: 0f 58 d1                     	addps	xmm2, xmm1
     138: 0f c6 c0 ff                  	shufps	xmm0, xmm0, 0xff        # xmm0 = xmm0[3,3,3,3]
     13c: 0f 59 c3                     	mulps	xmm0, xmm3
     13f: 0f 58 c2                     	addps	xmm0, xmm2
     142: 0f 11 44 24 28               	movups	xmmword ptr [esp + 0x28], xmm0
     147: 0f 10 54 24 18               	movups	xmm2, xmmword ptr [esp + 0x18]
     14c: 0f 28 c2                     	movaps	xmm0, xmm2
     14f: 0f c6 c2 00                  	shufps	xmm0, xmm2, 0x0         # xmm0 = xmm0[0,0],xmm2[0,0]
     153: 0f 59 c5                     	mulps	xmm0, xmm5
     156: 0f 28 ca                     	movaps	xmm1, xmm2
     159: 0f c6 ca 55                  	shufps	xmm1, xmm2, 0x55        # xmm1 = xmm1[1,1],xmm2[1,1]
     15d: 0f 59 cf                     	mulps	xmm1, xmm7
     160: 0f 58 c8                     	addps	xmm1, xmm0
     163: 0f 28 c2                     	movaps	xmm0, xmm2
     166: 0f c6 c2 aa                  	shufps	xmm0, xmm2, 0xaa        # xmm0 = xmm0[2,2],xmm2[2,2]
     16a: 0f 59 c6                     	mulps	xmm0, xmm6
     16d: 0f 58 c1                     	addps	xmm0, xmm1
     170: 0f c6 d2 ff                  	shufps	xmm2, xmm2, 0xff        # xmm2 = xmm2[3,3,3,3]
     174: 0f 59 d3                     	mulps	xmm2, xmm3
     177: 0f 58 d0                     	addps	xmm2, xmm0
     17a: 0f 11 54 24 18               	movups	xmmword ptr [esp + 0x18], xmm2
     17f: 0f 28 c4                     	movaps	xmm0, xmm4
     182: 0f c6 c4 00                  	shufps	xmm0, xmm4, 0x0         # xmm0 = xmm0[0,0],xmm4[0,0]
     186: 0f 59 c5                     	mulps	xmm0, xmm5
     189: 0f 28 cc                     	movaps	xmm1, xmm4
     18c: 0f c6 cc 55                  	shufps	xmm1, xmm4, 0x55        # xmm1 = xmm1[1,1],xmm4[1,1]
     190: 0f 59 cf                     	mulps	xmm1, xmm7
     193: 0f 58 c8                     	addps	xmm1, xmm0
     196: 0f 28 c4                     	movaps	xmm0, xmm4
     199: 0f c6 c4 aa                  	shufps	xmm0, xmm4, 0xaa        # xmm0 = xmm0[2,2],xmm4[2,2]
     19d: 0f 59 c6                     	mulps	xmm0, xmm6
     1a0: 0f 58 c1                     	addps	xmm0, xmm1
     1a3: 0f c6 e4 ff                  	shufps	xmm4, xmm4, 0xff        # xmm4 = xmm4[3,3,3,3]
     1a7: 0f 59 e3                     	mulps	xmm4, xmm3
     1aa: 0f 58 e0                     	addps	xmm4, xmm0
     1ad: 0f 10 04 24                  	movups	xmm0, xmmword ptr [esp]
     1b1: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     1b5: 0f 59 c5                     	mulps	xmm0, xmm5
     1b8: 0f 10 0c 24                  	movups	xmm1, xmmword ptr [esp]
     1bc: 0f c6 c9 55                  	shufps	xmm1, xmm1, 0x55        # xmm1 = xmm1[1,1,1,1]
     1c0: 0f 59 cf                     	mulps	xmm1, xmm7
     1c3: 0f 10 3c 24                  	movups	xmm7, xmmword ptr [esp]
     1c7: 0f 58 c8                     	addps	xmm1, xmm0
     1ca: 0f 28 c7                     	movaps	xmm0, xmm7
     1cd: 0f c6 c7 aa                  	shufps	xmm0, xmm7, 0xaa        # xmm0 = xmm0[2,2],xmm7[2,2]
     1d1: 0f 59 c6                     	mulps	xmm0, xmm6
     1d4: 0f 58 c1                     	addps	xmm0, xmm1
     1d7: 0f c6 ff ff                  	shufps	xmm7, xmm7, 0xff        # xmm7 = xmm7[3,3,3,3]
     1db: 0f 59 fb                     	mulps	xmm7, xmm3
     1de: 0f 58 f8                     	addps	xmm7, xmm0
     1e1: 8b 5c 24 7c                  	mov	ebx, dword ptr [esp + 0x7c]
     1e5: 85 d2                        	test	edx, edx
     1e7: 0f 84 ec 00 00 00            	je	0x2d9 <_sse_Vec3ProjectArray@36+0x2d9>
     1ed: 0f 10 2a                     	movups	xmm5, xmmword ptr [edx]
     1f0: 0f 11 3c 24                  	movups	xmmword ptr [esp], xmm7
     1f4: 0f 10 7a 10                  	movups	xmm7, xmmword ptr [edx + 0x10]
     1f8: 0f 10 72 20                  	movups	xmm6, xmmword ptr [edx + 0x20]
     1fc: 0f 10 5a 30                  	movups	xmm3, xmmword ptr [edx + 0x30]
     200: 0f 11 5c 24 48               	movups	xmmword ptr [esp + 0x48], xmm3
     205: 0f 10 44 24 28               	movups	xmm0, xmmword ptr [esp + 0x28]
     20a: 0f 28 d0                     	movaps	xmm2, xmm0
     20d: 0f c6 d0 00                  	shufps	xmm2, xmm0, 0x0         # xmm2 = xmm2[0,0],xmm0[0,0]
     211: 0f 59 d5                     	mulps	xmm2, xmm5
     214: 0f 28 c8                     	movaps	xmm1, xmm0
     217: 0f c6 c8 55                  	shufps	xmm1, xmm0, 0x55        # xmm1 = xmm1[1,1],xmm0[1,1]
     21b: 0f 59 cf                     	mulps	xmm1, xmm7
     21e: 0f 58 ca                     	addps	xmm1, xmm2
     221: 0f 28 d0                     	movaps	xmm2, xmm0
     224: 0f c6 d0 aa                  	shufps	xmm2, xmm0, 0xaa        # xmm2 = xmm2[2,2],xmm0[2,2]
     228: 0f 59 d6                     	mulps	xmm2, xmm6
     22b: 0f 58 d1                     	addps	xmm2, xmm1
     22e: 0f c6 c0 ff                  	shufps	xmm0, xmm0, 0xff        # xmm0 = xmm0[3,3,3,3]
     232: 0f 59 c3                     	mulps	xmm0, xmm3
     235: 0f 58 c2                     	addps	xmm0, xmm2
     238: 0f 11 44 24 28               	movups	xmmword ptr [esp + 0x28], xmm0
     23d: 0f 10 5c 24 18               	movups	xmm3, xmmword ptr [esp + 0x18]
     242: 0f 28 c3                     	movaps	xmm0, xmm3
     245: 0f c6 c3 00                  	shufps	xmm0, xmm3, 0x0         # xmm0 = xmm0[0,0],xmm3[0,0]
     249: 0f 59 c5                     	mulps	xmm0, xmm5
     24c: 0f 28 cb                     	movaps	xmm1, xmm3
     24f: 0f c6 cb 55                  	shufps	xmm1, xmm3, 0x55        # xmm1 = xmm1[1,1],xmm3[1,1]
     253: 0f 59 cf                     	mulps	xmm1, xmm7
     256: 0f 58 c8                     	addps	xmm1, xmm0
     259: 0f 28 c3                     	movaps	xmm0, xmm3
     25c: 0f c6 c3 aa                  	shufps	xmm0, xmm3, 0xaa        # xmm0 = xmm0[2,2],xmm3[2,2]
     260: 0f 59 c6                     	mulps	xmm0, xmm6
     263: 0f 58 c1                     	addps	xmm0, xmm1
     266: 0f c6 db ff                  	shufps	xmm3, xmm3, 0xff        # xmm3 = xmm3[3,3,3,3]
     26a: 0f 10 54 24 48               	movups	xmm2, xmmword ptr [esp + 0x48]
     26f: 0f 59 da                     	mulps	xmm3, xmm2
     272: 0f 58 d8                     	addps	xmm3, xmm0
     275: 0f 28 c4                     	movaps	xmm0, xmm4
     278: 0f c6 c4 00                  	shufps	xmm0, xmm4, 0x0         # xmm0 = xmm0[0,0],xmm4[0,0]
     27c: 0f 59 c5                     	mulps	xmm0, xmm5
     27f: 0f 28 cc                     	movaps	xmm1, xmm4
     282: 0f c6 cc 55                  	shufps	xmm1, xmm4, 0x55        # xmm1 = xmm1[1,1],xmm4[1,1]
     286: 0f 59 cf                     	mulps	xmm1, xmm7
     289: 0f 58 c8                     	addps	xmm1, xmm0
     28c: 0f 28 c4                     	movaps	xmm0, xmm4
     28f: 0f c6 c4 aa                  	shufps	xmm0, xmm4, 0xaa        # xmm0 = xmm0[2,2],xmm4[2,2]
     293: 0f 59 c6                     	mulps	xmm0, xmm6
     296: 0f 58 c1                     	addps	xmm0, xmm1
     299: 0f c6 e4 ff                  	shufps	xmm4, xmm4, 0xff        # xmm4 = xmm4[3,3,3,3]
     29d: 0f 59 e2                     	mulps	xmm4, xmm2
     2a0: 0f 58 e0                     	addps	xmm4, xmm0
     2a3: 0f 10 04 24                  	movups	xmm0, xmmword ptr [esp]
     2a7: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     2ab: 0f 59 c5                     	mulps	xmm0, xmm5
     2ae: 0f 10 0c 24                  	movups	xmm1, xmmword ptr [esp]
     2b2: 0f c6 c9 55                  	shufps	xmm1, xmm1, 0x55        # xmm1 = xmm1[1,1,1,1]
     2b6: 0f 59 cf                     	mulps	xmm1, xmm7
     2b9: 0f 10 3c 24                  	movups	xmm7, xmmword ptr [esp]
     2bd: 0f 58 c8                     	addps	xmm1, xmm0
     2c0: 0f 28 c7                     	movaps	xmm0, xmm7
     2c3: 0f c6 c7 aa                  	shufps	xmm0, xmm7, 0xaa        # xmm0 = xmm0[2,2],xmm7[2,2]
     2c7: 0f 59 c6                     	mulps	xmm0, xmm6
     2ca: 0f 58 c1                     	addps	xmm0, xmm1
     2cd: 0f c6 ff ff                  	shufps	xmm7, xmm7, 0xff        # xmm7 = xmm7[3,3,3,3]
     2d1: 0f 59 fa                     	mulps	xmm7, xmm2
     2d4: 0f 58 f8                     	addps	xmm7, xmm0
     2d7: eb 05                        	jmp	0x2de <_sse_Vec3ProjectArray@36+0x2de>
     2d9: 0f 10 5c 24 18               	movups	xmm3, xmmword ptr [esp + 0x18]
     2de: 0f 28 ef                     	movaps	xmm5, xmm7
     2e1: 8b 54 24 78                  	mov	edx, dword ptr [esp + 0x78]
     2e5: 8b 74 24 74                  	mov	esi, dword ptr [esp + 0x74]
     2e9: 8b 7c 24 70                  	mov	edi, dword ptr [esp + 0x70]
     2ed: 85 db                        	test	ebx, ebx
     2ef: 0f 84 ec 00 00 00            	je	0x3e1 <_sse_Vec3ProjectArray@36+0x3e1>
     2f5: bd 00 00 00 3f               	mov	ebp, 0x3f000000
     2fa: 66 0f 6e d5                  	movd	xmm2, ebp
     2fe: 0f c6 d2 00                  	shufps	xmm2, xmm2, 0x0         # xmm2 = xmm2[0,0,0,0]
     302: f2 0f 10 03                  	movsd	xmm0, qword ptr [ebx]   # xmm0 = mem[0],zero
     306: f2 0f 10 4b 08               	movsd	xmm1, qword ptr [ebx + 0x8] # xmm1 = mem[0],zero
     30b: 0f 5b c0                     	cvtdq2ps	xmm0, xmm0
     30e: 0f 11 44 24 18               	movups	xmmword ptr [esp + 0x18], xmm0
     313: 0f 5b c1                     	cvtdq2ps	xmm0, xmm1
     316: 0f 11 44 24 48               	movups	xmmword ptr [esp + 0x48], xmm0
     31b: f3 0f 10 43 10               	movss	xmm0, dword ptr [ebx + 0x10] # xmm0 = mem[0],zero,zero,zero
     320: f3 0f 10 4b 14               	movss	xmm1, dword ptr [ebx + 0x14] # xmm1 = mem[0],zero,zero,zero
     325: f3 0f 11 44 24 14            	movss	dword ptr [esp + 0x14], xmm0
     32b: f3 0f 5c c8                  	subss	xmm1, xmm0
     32f: f3 0f 11 4c 24 10            	movss	dword ptr [esp + 0x10], xmm1
     335: 0f c6 d2 00                  	shufps	xmm2, xmm2, 0x0         # xmm2 = xmm2[0,0,0,0]
     339: 0f 11 14 24                  	movups	xmmword ptr [esp], xmm2
     33d: 83 c6 08                     	add	esi, 0x8
     340: 8d 58 08                     	lea	ebx, [eax + 0x8]
     343: 0f 28 f3                     	movaps	xmm6, xmm3
     346: 0f 28 fc                     	movaps	xmm7, xmm4
     349: 0f 10 54 24 28               	movups	xmm2, xmmword ptr [esp + 0x28]
     34e: 0f 10 4c 24 38               	movups	xmm1, xmmword ptr [esp + 0x38]
     353: 66 66 66 66 2e 0f 1f 84 00 00 00 00 00       	nop	word ptr cs:[eax + eax]
     360: f3 0f 10 66 f8               	movss	xmm4, dword ptr [esi - 0x8] # xmm4 = mem[0],zero,zero,zero
     365: f3 0f 10 5e fc               	movss	xmm3, dword ptr [esi - 0x4] # xmm3 = mem[0],zero,zero,zero
     36a: 0f c6 e4 00                  	shufps	xmm4, xmm4, 0x0         # xmm4 = xmm4[0,0,0,0]
     36e: f3 0f 10 06                  	movss	xmm0, dword ptr [esi]   # xmm0 = mem[0],zero,zero,zero
     372: 0f c6 db 00                  	shufps	xmm3, xmm3, 0x0         # xmm3 = xmm3[0,0,0,0]
     376: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     37a: 0f 59 de                     	mulps	xmm3, xmm6
     37d: 0f 59 e2                     	mulps	xmm4, xmm2
     380: 0f 58 e3                     	addps	xmm4, xmm3
     383: 0f 59 c7                     	mulps	xmm0, xmm7
     386: 0f 58 c4                     	addps	xmm0, xmm4
     389: 0f 58 c5                     	addps	xmm0, xmm5
     38c: 0f 28 d8                     	movaps	xmm3, xmm0
     38f: 0f c6 d8 ff                  	shufps	xmm3, xmm0, 0xff        # xmm3 = xmm3[3,3],xmm0[3,3]
     393: 0f 5e c3                     	divps	xmm0, xmm3
     396: 0f 28 d9                     	movaps	xmm3, xmm1
     399: 0f 58 d8                     	addps	xmm3, xmm0
     39c: 0f 28 e1                     	movaps	xmm4, xmm1
     39f: 0f 5c e0                     	subps	xmm4, xmm0
     3a2: 0f c6 e3 01                  	shufps	xmm4, xmm3, 0x1         # xmm4 = xmm4[1,0],xmm3[0,0]
     3a6: 0f c6 e3 e2                  	shufps	xmm4, xmm3, 0xe2        # xmm4 = xmm4[2,0],xmm3[2,3]
     3aa: 0f 10 5c 24 48               	movups	xmm3, xmmword ptr [esp + 0x48]
     3af: 0f 59 e3                     	mulps	xmm4, xmm3
     3b2: 0f 10 1c 24                  	movups	xmm3, xmmword ptr [esp]
     3b6: 0f 59 e3                     	mulps	xmm4, xmm3
     3b9: 0f 10 5c 24 18               	movups	xmm3, xmmword ptr [esp + 0x18]
     3be: 0f 58 e3                     	addps	xmm4, xmm3
     3c1: 0f 13 63 f8                  	movlps	qword ptr [ebx - 0x8], xmm4
     3c5: 0f 12 c0                     	movhlps	xmm0, xmm0              # xmm0 = xmm0[1,1]
     3c8: f3 0f 59 44 24 10            	mulss	xmm0, dword ptr [esp + 0x10]
     3ce: f3 0f 58 44 24 14            	addss	xmm0, dword ptr [esp + 0x14]
     3d4: f3 0f 11 03                  	movss	dword ptr [ebx], xmm0
     3d8: 01 d6                        	add	esi, edx
     3da: 01 fb                        	add	ebx, edi
     3dc: 49                           	dec	ecx
     3dd: 75 81                        	jne	0x360 <_sse_Vec3ProjectArray@36+0x360>
     3df: eb 57                        	jmp	0x438 <_sse_Vec3ProjectArray@36+0x438>
     3e1: 83 c6 08                     	add	esi, 0x8
     3e4: 8d 58 08                     	lea	ebx, [eax + 0x8]
     3e7: 0f 10 74 24 28               	movups	xmm6, xmmword ptr [esp + 0x28]
     3ec: 0f 1f 40 00                  	nop	dword ptr [eax]
     3f0: f3 0f 10 4e f8               	movss	xmm1, dword ptr [esi - 0x8] # xmm1 = mem[0],zero,zero,zero
     3f5: f3 0f 10 56 fc               	movss	xmm2, dword ptr [esi - 0x4] # xmm2 = mem[0],zero,zero,zero
     3fa: 0f c6 c9 00                  	shufps	xmm1, xmm1, 0x0         # xmm1 = xmm1[0,0,0,0]
     3fe: 0f c6 d2 00                  	shufps	xmm2, xmm2, 0x0         # xmm2 = xmm2[0,0,0,0]
     402: f3 0f 10 06                  	movss	xmm0, dword ptr [esi]   # xmm0 = mem[0],zero,zero,zero
     406: 0f c6 c0 00                  	shufps	xmm0, xmm0, 0x0         # xmm0 = xmm0[0,0,0,0]
     40a: 0f 59 d3                     	mulps	xmm2, xmm3
     40d: 0f 59 ce                     	mulps	xmm1, xmm6
     410: 0f 58 ca                     	addps	xmm1, xmm2
     413: 0f 59 c4                     	mulps	xmm0, xmm4
     416: 0f 58 c1                     	addps	xmm0, xmm1
     419: 0f 58 c5                     	addps	xmm0, xmm5
     41c: 0f 28 c8                     	movaps	xmm1, xmm0
     41f: 0f c6 c8 ff                  	shufps	xmm1, xmm0, 0xff        # xmm1 = xmm1[3,3],xmm0[3,3]
     423: 0f 5e c1                     	divps	xmm0, xmm1
     426: 0f 13 43 f8                  	movlps	qword ptr [ebx - 0x8], xmm0
     42a: 0f 12 c0                     	movhlps	xmm0, xmm0              # xmm0 = xmm0[1,1]
     42d: f3 0f 11 03                  	movss	dword ptr [ebx], xmm0
     431: 01 d6                        	add	esi, edx
     433: 01 fb                        	add	ebx, edi
     435: 49                           	dec	ecx
     436: 75 b8                        	jne	0x3f0 <_sse_Vec3ProjectArray@36+0x3f0>
     438: 83 c4 58                     	add	esp, 0x58
     43b: 5e                           	pop	esi
     43c: 5f                           	pop	edi
     43d: 5b                           	pop	ebx
     43e: 5d                           	pop	ebp
     43f: c2 24 00                     	ret	0x24
