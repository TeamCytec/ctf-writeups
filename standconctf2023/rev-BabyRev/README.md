# Rev - Baby Rev
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

We are given with an executable file. If we throw it into IDA, we see alot of Nim stuff which we can read through and try to understand. However, I solved this challenge slightly differently.

Opening the exe in IDA, we can see the Main function that looks like this:

```c
__int64 NimMainModule()
{

  keyHex__main_24 = 29i64;
  qword_7FF66FFA3CA8 = (__int64)&TM__V45tF8B8NBcxFcjfe7lhBw_2;
  v0 = __acrt_iob_func;
  encrypted_flag__main_34 = 29i64;
  qword_7FF66FFA3C98 = (__int64)&TM__V45tF8B8NBcxFcjfe7lhBw_4;
  v1 = __acrt_iob_func(1u);
  v17 = TM__V45tF8B8NBcxFcjfe7lhBw_7; // global variable that points to string "Enter key:"
  write__systemZio_276(v1, &v17); // print to stdout
```

As we can see, at the start of the function, 3 global variables are being referenced. One of them points to the string that is printed **"Enter key: "**.

The other two are some gibberish blob of text, but coincidentally, they are of the same length! What happens if we try to XOR them together for fun?

```py
from pwn import xor
blob1 = bytes.fromhex("1412257D2C390E2F01441138113C0077005701324567366A3D180C3F27")
blob2 = bytes.fromhex("47466433687A41617A716578657563363166786D37545A594B58624B5A")
print(xor(blob1, blob2))
# output: b'STANDCON{5t@tIcA11y_r3l3v@nt}'
```

