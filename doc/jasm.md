# JASM REFERENCE

`JASM` (or `J-ASM`) is a custom assembly language.

It has a custom assembler that produces binaries for the JOKOR architecture.

> Since the JOKOR only has 16 built-in instructions (see the spec), many of these instructions are actually built-in assembler macros. These macros are transparent to the programmer, but may trash the F or XY registers. If you are unsure, see the instruction's definition below. For more information, see the [list of macros](#macros).

## All Instructions (including built-in macros)

### LOAD

Opcode: `0x0`

Definition: `LOAD reg, imm16/XY -> reg = [imm16 or XY]`

Load the byte at address imm16 or in register pair XY into reg.
Usage: `LOAD A, 0xAAAA`, `LOAD A, XY`

---

### MOVE

Opcode: `0x1`

Definition:` MOVE reg, imm8/reg -> reg = (imm8 or reg)`

Move a value from an 8-bit immediate or another register into reg.

Usage: `MOVE B, 0x42`, `MOVE A, B`

---

### STORE

Opcode: `0x2`

Definition: `STORE imm16/XY, reg -> [imm16 or XY] = reg`

Store the value in reg into RAM at address imm16 or in register pair XY.

Usage: `STORE 0x1234, A`, ` STORE XY, B`

---

### PUSH

Opcode: `0x3`

Definition: `PUSH reg/imm8 -> push(reg or imm8)`

Push a value from reg or an 8-bit immediate onto the stack.

Usage: `PUSH A`, `PUSH 0x7F`

---

### POP

Opcode: `0x4`

Definition: `POP reg -> reg = pop()`

Pop the top value from the stack into reg.

Usage: `POP A`

---

### ADD

Opcode: `0x5`

Definition: `ADD reg, reg/imm8 -> reg = reg + (reg or imm8)`

Add a register or 8-bit immediate to reg. Updates flags as specified.

Usage: `ADD A, B`, `ADD A, 0x10`

---

### SUB

Opcode: `0x6`

Definition: `SUB reg, reg/imm8 -> reg = reg - (reg or imm8)`

Subtract a register or 8-bit immediate from reg. Updates flags as specified.

Usage:` SUB A, B`, `SUB A, 0x05`

---

### SHL

Opcode: `0x7`

Definition: `SHL reg, reg/imm8 -> reg = reg << (reg or imm8)`

Logical shift left of reg by the amount specified in a register or immediate.

Usage: `SHL A, 1`, `SHL B, C`

---

### SHR

Opcode: `0x8`

Definition: `SHR reg, reg/imm8 -> reg = reg >> (reg or imm8)`

Logical shift right of reg by the amount specified in a register or immediate.

Usage: `SHR A, 1`, `SHR B, C`

---

### AND

Opcode: `0x9`

Definition: `AND reg, reg/imm8 -> reg = reg & (reg or imm8)`

Bitwise AND between reg and another register or immediate value.

Usage: `AND A, B`, `AND B, 0x0F`

---

### OR

Opcode: `0xA`

Definition: `OR reg, reg/imm8 -> reg = reg | (reg or imm8)`

Bitwise OR between reg and another register or immediate value.

Usage: `OR A, B`, `OR B, 0xF0`

---

### NOR

Opcode: `0xB`

Definition: `NOR reg, reg/imm8 -> reg = ~(reg | (reg or imm8))`

Bitwise NOR between reg and another register or immediate value.

Usage: `NOR A, B`, `NOR B, 0xFF`

---

### INB

Opcode: `0xC`

Definition: `INB reg, port(reg/imm8) -> reg = IO[(reg or imm8)]`

Read an 8-bit value from an I/O port into reg.

Usage: `INB A, 0x10`, `INB B, C`

---

### OUTB

Opcode: `0xD`

Definition: `OUTB port(reg/imm8), reg -> IO[(reg or imm8)] = reg`

Write the value in reg to an I/O port.

Usage: `OUTB 0x10, A`, `OUTB B, C`

---

### CMP

Opcode: `0xE`

Definition: `CMP reg, reg/imm8 -> flags = reg - (reg or imm8)`

Compare reg with another register or 8-bit immediate. Updates flags (Zero, Carry, Negative, Overflow). Does not store result in reg.

Usage: `CMP A, B`, `CMP A, 0x10`

---

### JNZ

Opcode: `0xF`

Definition: `JNZ imm16/reg -> if (Z==0) PC = (imm16 or regpair)`

Jump to a 16-bit immediate address or the address in a register pair if the Zero flag is not set.

Usage: `JNZ 0x1234`, `JNZ XY`

### Base CPU instructions:

```
LOAD reg, imm16/XY -> reg = [imm16 or XY]
MOVE reg, imm8/reg -> reg = (imm8 or reg)
STORE imm16/XY, reg -> [imm16 or XY] = reg
PUSH reg/imm8 -> push(reg or imm8)
POP reg -> reg = pop()
ADD^ reg, reg/imm8 -> reg = reg + (reg or imm8)
SUB* reg, reg/imm8 -> reg = reg - (reg or imm8)
SHL reg, reg/imm8 -> reg = reg << (reg or imm8)
SHR reg, reg/imm8 -> reg = reg >> (reg or imm8)
AND reg, reg/imm8 -> reg = reg & (reg or imm8)
OR  reg, reg/imm8 -> reg = reg | (reg or imm8)
NOR reg, reg/imm8 -> reg = ~(reg | (reg or imm8))
INB reg, port(reg/imm8) -> reg = IO[(reg or imm8)]
OUTB port(reg/imm8), reg  -> IO[(reg or imm8)] = reg
CMP* reg, reg/imm8 -> flags = reg - (reg or imm8)
JNZ imm16/reg -> if (Z==0) PC = (imm16 or regpair)

^ This instruction modifies the Carry and Overflow flags. In the event of an overflow, the result will wrap around modulo 256.
* This instruction modifies the Zero flag.
```
