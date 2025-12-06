# JOKOR SPECIFICATION

---

Meet the JOKOR: A custom CPU architecture design with a custom everything.

## Features

- 32 instructions (8 addressing modes)
- 8-bit data width
- 16-bit address bus (64k of accessable memory)
- Memory banking
- Device communication through built-in CPU instructions

## Instruction Format

Instruction format is `AAAAA BBB` `CCCC DDDD` `EEEE EEEE*` `FFFFFFFF*` where:

`AAAAA` is the instruction operand code and `BBB` is the addressing mode.

`BBB` also defines what `CCCC`, `DDDD`, `EEEE EEEE`, and `FFFFFFFF` contain (or if they are utilized at all).

- `000`: No operands.
- `001`: `CCCC` defines a single register argument. `DDDD EEEEEEEEE FFFFFFFF` are unused.
- `010`: `EEEEEEEE` defines an 8-bit immediate. `CCCC DDDD` and `FFFFFFFF` are unused.
- `011`: `CCCC` and `DDDD` define a first and second register argument, respectively. `EEEEEEEE FFFFFFFF` are unused.
- `100`: `CCCC` defines a register argument. `EEEEEEE` defines an 8-bit immediate. `DDDD` is unused.
- `101`: `CCCC` defines a single register argument. `EEEEEEEE FFFFFFFF` defines a memory location. `DDDD` is unused.
- `110`: `CCCC` defines a single register argument. `EEEE EEEE` defines a register pair which is interpreted as a memory location.
- `111`: `CCCC DDDD` define a register pair. `EEEEEEEE FFFFFFFF` defines a 16-bit immediate.

_\*These bytes are not in all instructions. See the table below._

_NOTE: All 16-bit values are little-endian: `LLLLLLLL HHHHHHHH` if represented as an immediate, `L:H` if represented as a register pair._

`BBB` also defines how many bytes an instruction takes up in memory:

| Value | Length | Type           | Description                                 |
| ----- | ------ | -------------- | ------------------------------------------- |
| 000   | 1      | No operands    | _Really?_                                   |
| 001   | 2      | REG            | Register                                    |
| 010   | 3      | IMM8           | 8-bit Immediate                             |
| 011   | 2      | REG, REG       | Register / Register                         |
| 100   | 3      | REG, IMM8      | Register / 8-bit Immediate                  |
| 101   | 4      | REG, [IMM16]   | Register / Address as 16-bit Immediate      |
| 110   | 3      | REG, [REG:REG] | Register / Address as Register Pair         |
| 111   | 4      | REG:REG, IMM16 | Register Pair / Address as 16-bit Immediate |

## Instruction Set

See the [Language Specification](jasm.md) for more details.

## Registers

There are six 8-bit general purpose registers:

| Index | Name | Purpose                        |
| ----- | ---- | ------------------------------ |
| 0     | A    | General purpose / accumulator  |
| 1     | B    | General purpose                |
| 2     | C    | General purpose                |
| 3     | D    | General purpose                |
| 4     | X    | Low address / general purpose  |
| 5     | Y    | High address / general purpose |

There are five memory-mapped registers (see Memory Layout below)

| Index | Name | Purpose                     |
| ----- | ---- | --------------------------- |
| 6     | F    | Flags                       |
| 7     | Z    | Zero                        |
| 8     | PC   | Program Counter (read-only) |
| 9     | SP   | Stack Pointer               |
| A     | MB   | Memory Bank                 |
| B     | STS  | Status                      |

### Flags Register

The bytes of the Flags register is defined as follows:

```
0: Carry
1: Zero
2: Negative
3: Overflow
5-7: (reserved for future use)
```

### Status Register

The bytes of the Status register is defined as follows:

```
0: Error
1: Halted
2-7: Undefined (reserved for future use)
```

## Memory Layout

Total addressable memory: `64Kib`

The memory layout is as follows:

| Range          | Size      | Purpose                                         |
| -------------- | --------- | ----------------------------------------------- |
| 0x0000..0x7FFF | 32 KiB    | General Purpose ROM                             |
| 0x8000..0xBFFF | 16 KiB    | General Purpose RAM (banked)*                   |
| 0xC000..0xFDFF | 15 KiB    | General Purpose RAM                             |
| 0xFC00..0xFEFF | 768 bytes | Stack (recommended)**                           |
| 0xFF00..0xFFF8 | 249 bytes | Scratch                                         |
| 0xFFF9..0xFFF9 | 1 byte    | Flags register(mapped)                          |
| 0xFFFA..0xFFFA | 1 byte    | Zero register(mapped)                           |
| 0xFFFB..0xFFFB | 1 byte    | Memory Bank register (mapped)                   |
| 0xFFFC..0xFFFD | 2 bytes   | Stack Pointer (mapped, 16 bits little-endian)   |
| 0xFFFE..0xFFFF | 2 bytes   | Program Counter (mapped, 16 bits little-endian) |

_\* This memory can be swapped using the MB register. MB = 0 indicates that the built-in RAM is in use. It is recommended that MB = 1 point to the built-in VRAM._

_\*\* The stack grows downwards. It is recommended that SP = 0xFEFF._

## Ports

Ports can be used to interact with I/O devices.