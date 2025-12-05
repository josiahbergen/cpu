# JOKOR SPECIFICATION

Meet the JOKOR.

## Features

- 8-bit data width
- 16-bit address bus (64k of accessable memory)
- Memory banking
- Device communication through built-in instructions

## Instruction Layout

Instruction format is `XXXX  Y  ZZZ` where:

- XXXX is the instruction operand code.
- Y defines whether to use immediate or register value
- ZZZ defines the register referenced in the first operand (if applicable)

If there is a second reg operand, it is contained in the first three bits of the second instruction byte.

> There is never more than one choice between imm/reg per instruction. The opcode will encode if whether this choice affects the first or second operand.

```
operation, reg        ->  one byte. register is encoded within.
operation, imm8       ->  two bytes. imm8 is the byte after the instruction byte.
operation, reg, imm8  ->  two bytes. reg is encoded within the first byte, imm8 is the second.
operation, reg, reg   ->  two bytes. reg is encoded within the first byte and the first three bits of the second.
operation, reg, imm16 ->  three bytes. reg is encoded within the first byte and the imm16 is the next two.
operation, imm16, reg ->  three bytes. reg is encoded within the first byte and the imm16 is the next two.
operation, reg, reg/reg ->  three bytes. reg is encoded within the first byte and reg/reg is the first six bytes of the second.

```

## Instruction Set

```
0x0: LOAD reg, imm16/XY -> reg = [imm16 or XY]
Load the byte at address imm16 or at address in register pair XY into reg.

0x1: MOVE reg, imm8/reg -> reg = (imm8 or reg)
Move the value from imm8 or another register into reg.

0x2: STORE imm16/XY, reg -> [imm16 or XY] = reg
Store the value in reg into RAM at address imm16 or at address in register pair XY.

0x3: PUSH reg/imm8 -> push(reg or imm8)
Push the value in reg or an 8-bit immediate onto the stack.

0x4: POP reg -> reg = pop()
Pop the top of the stack into reg.

0x5: ADD reg, reg/imm8 -> reg = reg + (reg or imm8)
Add a register or 8-bit immediate to reg. Result stored in reg.
This instruction modifies the Carry and Overflow flags.
In the event of an overflow, the result will wrap around modulo 256

0x6: SUB reg, reg/imm8 -> reg = reg - (reg or imm8)
Subtract a register or 8-bit immediate from reg. Result stored in reg.
This instruction modifies the Zero flag.

0x7: SHL reg, reg/imm8 -> reg = reg << (reg or imm8)
Logical shift reg left by the amount in reg or imm8.

0x8: SHR reg, reg/imm8 -> reg = reg >> (reg or imm8)
Logical shift reg right by the amount in reg or imm8.

0x9: AND reg, reg/imm8 -> reg = reg & (reg or imm8)
Bitwise AND reg with reg or imm8. Result stored in reg.

0xA: OR  reg, reg/imm8 -> reg = reg | (reg or imm8)
Bitwise OR reg with reg or imm8. Result stored in reg.

0xB: NOR reg, reg/imm8 -> reg = ~(reg | (reg or imm8))
Bitwise NOR reg with reg or imm8. Result stored in reg.

0xC: INB reg, port(reg/imm8) -> reg = IO[(reg or imm8)]
Read an 8-bit value from an I/O port into reg.

0xD: OUTB port(reg/imm8), reg  -> IO[(reg or imm8)] = reg
Write reg to an I/O port.

0xE: CMP reg, reg/imm8 -> flags = reg - (reg or imm8)
Compare reg with reg or imm8. Updates flags only.

0xF: JNZ imm16/XY -> if (Z==0) PC = (imm16 or regpair)
Jump to imm16 or the address in  if zero flag is not set.
```

## Registers

There are four 8-bit general purpose registers:

    A: General purpose / accumulator
    B: General purpose
    X: Low address / general purpose
    Y: High address / general purpose

There are five memory-mapped registers (see [Memory Layout](#Memory%20Layout))

```
F: Flags
Z: Zero register
PC: Program Counter (read-only)
SP: Stack Pointer
MB: Memory Bank
```

### Flags Register

The Flags register is defined as follows:

```
0: Carry
1: Zero
2: Negative
3: Overflow
4-7: Undefined (reserved for future use)
```

## Memory Layout

The memory layout is as follows:

```
0x0000..0x7FFF (32 KiB): General Purpose ROM
0x8000..0xBFFF (16 KiB): General Purpose RAM (banked)
0xC000..0xFDFF (15 KiB): General Purpose RAM
0xFC00..0xFEFF (768 bytes): Stack (recommended)
0xFF00..0xFFF8 (249 bytes): Scratch Memory
0xFFF9..0xFFF9: Flags register (mapped)
0xFFFA..0xFFFA: Zero register (mapped)
0xFFFB..0xFFFB: Memory Bank register (mapped)
0xFFFC..0xFFFD: Stack Pointer (mapped, 16 bits little-endian)
0xFFFE..0xFFFF: Program Counter (mapped, 16 bits little-endian)
```

### Notes:

- `0x8000..0xBFFF` can be swapped using the MB register.
  MB = 0 indicates that the built-in RAM is in use.
- The stack grows downwards. It is recommended that SP = 0xFEFF.

## Ports

Ports can be used to interact with I/O devices.

### Special Ports

Port `0x00` can be used to interact with the status of the computer.
