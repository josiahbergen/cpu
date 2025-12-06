# JOKOR SPECIFICATION

Meet the JOKOR.

## Features

- 8-bit data width
- 16-bit address bus (64k of accessable memory)
- Memory banking
- Device communication through built-in instructions

## Instruction Layout

Instruction format is `AAAAA BBB` `CCCC DDDD` `EEEE EEEE?` `FFFFFFFF?` where:

- `AAAAA` is the instruction operand code.

- `BBB` defines the addressing mode:

  - `000`: No operands. This instruction is 1 byte long. 
  - `001`: `CCCC` defines a single register argument. `DDDD EEEEEEEEE FFFFFFFF` are unused. This instruction is 2 bytes long.
  - `010`: `EEEEEEEE` defines an 8-bit immediate. `CCCC DDDD` and `FFFFFFFF` are unused. This instruction is 3 bytes long.
  - `011`: `CCCC` and `DDDD` define a first and second register argument, respectively. `EEEEEEEE FFFFFFFF` are unused. This instruction is 2 bytes long.
  - `100`: `CCCC` defines a register argument. `EEEEEEE` defines an 8-bit immediate. `DDDD` is unused. This instruction is 3 bytes long.
  - `101`: `CCCC` defines a single register argument. `EEEEEEEE FFFFFFFF` defines a memory location (little-endian). `DDDD` is unused. This instruction is 4 bytes long.
  - `110`: `CCCC` defines a single register argument. `EEEE EEEE` defines a register pair which is interpreted as a memory location (little-endian). This instruction is 3 bytes long. 
  - `111`: `CCCC DDDD` define a register pair. `EEEEEEEE FFFFFFFF` defines a 16-bit immediate. This instruction is 4 bytes long.

### Instructions

See the [Language Specification](doc/jasm.md) for details.

## Registers

There are four 8-bit general purpose registers:

```
ID  NAME  PURPOSE
0   A     General purpose / accumulator
1   B     General purpose
2   C     General purpose
3   D     General purpose
4   X     Low address / general purpose
5   Y     High address / general purpose
```

There are five memory-mapped registers (see Memory Layout below)

```
ID  NAME  PURPOSE
6   F     Flags
7   Z     Zero
8   PC    Program Counter (read-only)
9   SP    Stack Pointer
A   MB    Memory Bank
B   STS   Status
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


## Old

- If `BB` is `000`, no immediate is used. `CCCC` defines the first register argument. `DDDD` defines the second register argument. If there is only one register argument, `DDDD` is unused. `EEEEEEEE` and `FFFFFFFF` are unused.

- If `BB` is `001`, an 8-bit immediate follows. `CCCC` defines the register argument. `EEEEEEEE` is the 8-bit immediate. `FFFFFFFF` is unused.

- If `BB` is `10`, a 16-bit immediate follows. `CCCC DDDD` defines a register pair argument as `CCCC:DDDD (H:L)`. The immediate is in `EEEEEEEE FFFFFFFF` (little-endian). 

- If `BB` is `11`, `CCCC DDDD` defines a register pair argument as `CCCC:DDDD (H:L)`. The low four bits of `---EEEE` define a register pair representing an address.



0: REG
1: IMM8
2: REG, REG
3: REG, IMM8
4: REG, [IMM16]
5: REG, [REG:REG]
6: REG:REG, IMM16
