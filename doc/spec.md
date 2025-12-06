# JOKOR SPECIFICATION

Meet the JOKOR.

## Features

- 8-bit data width
- 16-bit address bus (64k of accessable memory)
- Memory banking
- Device communication through built-in instructions

## Instruction Layout

Instruction format is `AAAAAA BC` `DDDD EEEE` `FFFFFFFF?` `GGGGGGGG?` where:

- `AAAAAA` is the instruction operand code.

- `BC` defines immediate/addressing mode flags.

- If `BC` is `00`, no immediate is used. `DDDD` defines the first register argument. `EEEE` defines the second register argument. If there is only one register argument, `EEEE` is unused. `FFFFFFFF` and `GGGGGGGG` are unused.

- If `BC` is `01`, an 8-bit immediate follows. `DDDD` defines the register argument. `FFFFFFFF` is the 8-bit immediate. `GGGGGGGG` is unused.

- If `BC` is `10`, a 16-bit immediate follows. `DDDD EEEE` defines a register pair argument as `DDDD:EEEE (H:L)`. The immediate is in `FFFFFFFF GGGGGGGG` (little-endian). 

- If `BC` is `11`, an absolute 16-bit memory address follows. `DDDD` defines a register argument.  `FFFFFFFF GGGGGGGG` defines a 16-bit memory address.


### Instructions

See inst.txt for the list of instructions.

## Registers

There are four 8-bit general purpose registers:

```
A: General purpose / accumulator
B: General purpose
C: General purpose
D: General purpose
X: Low address / general purpose
Y: High address / general purpose
```

There are five memory-mapped registers (see [Memory Layout](#Memory%20Layout))

```
F: Flags
STS: Status register
Z: Zero register
PC: Program Counter (read-only)
SP: Stack Pointer
MB: Memory Bank
```

### Flags Register

The bytes of the Flags register is defined as follows:

```
0: Carry
1: Zero
2: Negative
3: Overflow
5-7: Undefined (reserved for future use)
```

### Status Register

The bytes of the Status register is defined as follows:

```
0: Error
1: Halted
2-7: Undefined (reserved for future use)
```

## Memory Layout

Total memory: `64Kib`

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
