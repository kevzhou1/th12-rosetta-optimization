.intel_syntax noprefix
.code32
.text
decide:
  inc  byte ptr [ebp + 0x14]          # keep the game's own counter behaving as before
  mov  eax, dword ptr [0x11111111]    # acc
  add  eax, 2                         # N (frames rendered ...)
  cmp  eax, 3                         # M (... out of every M)
  jb   skip
  sub  eax, 3                         # M
  mov  dword ptr [0x11111111], eax    # acc
  mov  ecx, dword ptr [0x22222222]    # ticks skipped since last render
  mov  dword ptr [0x33333333], ecx    # hand to FPS meter
  mov  dword ptr [0x22222222], 0
  .byte 0xe9
  .long 0x44444444                    # jmp render (0x450500)
skip:
  mov  dword ptr [0x11111111], eax
  inc  dword ptr [0x22222222]
  .byte 0xe9
  .long 0x55555555                    # jmp skip (0x450566)
meter:
  mov  ecx, dword ptr [0x33333333]    # replaces movzx ecx, byte ptr [0x4ceace] (7 bytes)
  nop
