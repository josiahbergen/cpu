#!/usr/bin/env python3
"""
JASM v1.1 emulator — full 32-op implementation (opcodes 0..31).
Usage:
    python emulator.py [binary]
REPL commands:
    load <path>, step, cont, run, break <hex>, regs, mem <hexaddr> <len>, disasm [hexaddr], ports, quit
"""
import sys
from typing import Tuple, Optional

# -----------------------
# Constants / maps
# -----------------------
MEM_SIZE = 65536

REG_CODE_TO_NAME = {
    0x0: 'A', 0x1: 'B', 0x2: 'C', 0x3: 'D', 0x4: 'X', 0x5: 'Y'
}
REG_INDEX = ['A','B','C','D','X','Y']

# flags bits
FLAG_C = 0
FLAG_Z = 1
FLAG_N = 2
FLAG_V = 3

# status bits
STS_HALT = 1 << 1

# opcodes
OP_LOAD  = 0
OP_STORE = 1
OP_MOVE  = 2
OP_PUSH  = 3
OP_POP   = 4
OP_ADD   = 5
OP_ADDC  = 6
OP_SUB   = 7
OP_SUBB  = 8
OP_INC   = 9
OP_DEC   = 10
OP_SHL   = 11
OP_SHR   = 12
OP_AND   = 13
OP_OR    = 14
OP_NOR   = 15
OP_NOT   = 16
OP_XOR   = 17
OP_INB   = 18
OP_OUTB  = 19
OP_CMP   = 20
OP_SEC   = 21
OP_CLC   = 22
OP_CLZ   = 23
OP_JMP   = 24
OP_JZ    = 25
OP_JNZ   = 26
OP_JC    = 27
OP_JNC   = 28
OP_INT   = 29
OP_HALT  = 30
OP_NOP   = 31

# modes - ALL 8 addressing modes from spec
MODE_NO_OPERANDS = 0b000  # 0
MODE_SINGLE_REG  = 0b001  # 1
MODE_IMM8_ONLY   = 0b010  # 2
MODE_REG_REG     = 0b011  # 3
MODE_REG_IMM8    = 0b100  # 4
MODE_REG_ABS16   = 0b101  # 5
MODE_REG_PAIR16  = 0b110  # 6
MODE_ABS16_ONLY  = 0b111  # 7

def mask8(x): return x & 0xFF
def mask16(x): return x & 0xFFFF

# -----------------------
# CPU
# -----------------------
class CPU:
    def __init__(self):
        # GPRs 8-bit
        self.reg = {name:0 for name in REG_INDEX}  # A,B,C,D,X,Y
        # special
        self.PC = 0x0000
        self.SP = 0xFEFF
        self.F  = 0x00    # flags byte
        self.STS = 0x00
        self.Z   = 0x00
        self.MB  = 0x00
        # mem and I/O
        self.memory = bytearray(MEM_SIZE)
        self.ports = [0]*256
        # breakpoints
        self.breakpoints = set()
        # handlers map
        self.handlers = {}
        self._build_handlers()
        # halted state
        self.halted = False

    # ---------------- memory helpers ----------------
    def load_program(self, data: bytes, base: int=0x0000):
        n = len(data)
        if base + n > MEM_SIZE:
            raise ValueError("Program too large")
        self.memory[base:base+n] = data
        self.PC = base
        print(f"Loaded {n} bytes at 0x{base:04X}")

    def read_u8(self, addr:int) -> int:
        return self.memory[mask16(addr)]

    def write_u8(self, addr:int, val:int):
        self.memory[mask16(addr)] = mask8(val)

    def read_u16(self, addr:int) -> int:
        lo = self.read_u8(addr)
        hi = self.read_u8((addr+1) & 0xFFFF)
        return (hi<<8) | lo

    def write_u16(self, addr:int, val:int):
        self.write_u8(addr, val & 0xFF)
        self.write_u8((addr+1)&0xFFFF, (val>>8) & 0xFF)

    # ---------------- fetch / decode ----------------
    def fetch_byte(self) -> int:
        b = self.read_u8(self.PC)
        self.PC = mask16(self.PC + 1)
        return b

    def decode(self):
        first = self.fetch_byte()
        opcode = (first >> 3) & 0b11111
        mode = first & 0b111
        
        # Handle all 8 addressing modes according to spec
        match mode:
            case 0b000:  # MODE_NO_OPERANDS
                return (opcode, mode)
            
            case 0b001:  # MODE_SINGLE_REG
                byte2 = self.fetch_byte()
                reg_c = (byte2 >> 4) & 0x0F
                return (opcode, mode, reg_c)
            
            case 0b010:  # MODE_IMM8_ONLY
                self.fetch_byte()  # Skip unused byte
                imm8 = self.fetch_byte()
                return (opcode, mode, imm8)
            
            case 0b011:  # MODE_REG_REG
                byte2 = self.fetch_byte()
                reg_d = (byte2 >> 4) & 0x0F
                reg_s = byte2 & 0x0F
                return (opcode, mode, reg_d, reg_s)
            
            case 0b100:  # MODE_REG_IMM8
                byte2 = self.fetch_byte()
                reg_d = (byte2 >> 4) & 0x0F
                imm8 = self.fetch_byte()
                return (opcode, mode, reg_d, imm8)
            
            case 0b101:  # MODE_REG_ABS16
                byte2 = self.fetch_byte()
                reg_d = (byte2 >> 4) & 0x0F
                lo = self.fetch_byte()
                hi = self.fetch_byte()
                addr = (hi << 8) | lo
                return (opcode, mode, reg_d, addr)
            
            case 0b110:  # MODE_REG_PAIR16
                byte2 = self.fetch_byte()
                reg_d = (byte2 >> 4) & 0x0F
                reg_pair = byte2 & 0x0F
                return (opcode, mode, reg_d, reg_pair)
            
            case 0b111:  # MODE_ABS16_ONLY
                self.fetch_byte()  # Skip unused byte
                lo = self.fetch_byte()
                hi = self.fetch_byte()
                addr = (hi << 8) | lo
                return (opcode, mode, addr)
            
            case _:
                raise RuntimeError(f"Invalid mode {mode} at 0x{self.PC:04X}")

    # ---------------- reg helpers ----------------
    def reg_get(self, code:int) -> int:
        name = REG_CODE_TO_NAME.get(code)
        if name is None: return 0
        return self.reg[name] & 0xFF

    def reg_set(self, code:int, value:int):
        name = REG_CODE_TO_NAME.get(code)
        if name is None: return
        self.reg[name] = mask8(value)

    # ---------------- flags helpers ----------------
    def set_flag(self, bit:int, v:bool):
        if v:
            self.F |= (1<<bit)
        else:
            self.F &= ~(1<<bit)

    def get_flag(self, bit:int) -> int:
        return 1 if ((self.F >> bit) & 1) else 0

    def update_ZN_from8(self, value:int):
        v = mask8(value)
        self.set_flag(FLAG_Z, v == 0)
        self.set_flag(FLAG_N, (v & 0x80) != 0)

    # ---------------- stack ----------------
    def push8(self, val:int):
        self.SP = mask16(self.SP - 1)
        self.write_u8(self.SP, val)

    def pop8(self) -> int:
        val = self.read_u8(self.SP)
        self.SP = mask16(self.SP + 1)
        return val

    # ---------------- build handler table ----------------
    def _build_handlers(self):
        h = self.handlers
        h[OP_LOAD]  = self.handle_load
        h[OP_STORE] = self.handle_store
        h[OP_MOVE]  = self.handle_move
        h[OP_PUSH]  = self.handle_push
        h[OP_POP]   = self.handle_pop
        h[OP_ADD]   = self.handle_add
        h[OP_ADDC]  = self.handle_addc
        h[OP_SUB]   = self.handle_sub
        h[OP_SUBB]  = self.handle_subb
        h[OP_INC]   = self.handle_inc
        h[OP_DEC]   = self.handle_dec
        h[OP_SHL]   = self.handle_shl
        h[OP_SHR]   = self.handle_shr
        h[OP_AND]   = self.handle_and
        h[OP_OR]    = self.handle_or
        h[OP_NOR]   = self.handle_nor
        h[OP_NOT]   = self.handle_not
        h[OP_XOR]   = self.handle_xor
        h[OP_INB]   = self.handle_inb
        h[OP_OUTB]  = self.handle_outb
        h[OP_CMP]   = self.handle_cmp
        h[OP_SEC]   = lambda dec: self.set_flag(FLAG_C, True)
        h[OP_CLC]   = lambda dec: self.set_flag(FLAG_C, False)
        h[OP_CLZ]   = lambda dec: self.set_flag(FLAG_Z, False)
        h[OP_JMP]   = self.handle_jmp
        h[OP_JZ]    = self.handle_jz
        h[OP_JNZ]   = self.handle_jnz
        h[OP_JC]    = self.handle_jc
        h[OP_JNC]   = self.handle_jnc
        h[OP_INT]   = self.handle_int
        h[OP_HALT]  = self.handle_halt
        h[OP_NOP]   = lambda dec: None

    # ---------------- arithmetic primitives ----------------
    def _add_core(self, a:int, b:int) -> Tuple[int,int,int]:
        res = a + b
        carry = 1 if res > 0xFF else 0
        r8 = mask8(res)
        v = 1 if (((a ^ b) & 0x80) == 0 and ((a ^ r8) & 0x80) != 0) else 0
        return r8, carry, v

    def _sub_core(self, a:int, b:int) -> Tuple[int,int,int]:
        res = (a - b) & 0xFF
        borrow = 1 if a < b else 0
        v = 1 if (((a ^ b) & 0x80) != 0 and ((a ^ res) & 0x80) != 0) else 0
        return res, borrow, v

    # ---------------- instruction handlers ----------------

    def handle_load(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b101:  # MODE_REG_ABS16
                _, _, reg_d, addr = decoded
                val = self.read_u8(addr)
                self.reg_set(reg_d, val)
                self.update_ZN_from8(val)
            case 0b110:  # MODE_REG_PAIR16
                _, _, reg_d, reg_pair = decoded
                hi = self.reg_get(reg_pair)
                lo = self.reg_get((reg_pair + 1) & 0x0F)
                addr = (hi << 8) | lo
                val = self.read_u8(addr)
                self.reg_set(reg_d, val)
                self.update_ZN_from8(val)
            case _:
                raise RuntimeError("LOAD requires MODE_REG_ABS16 or MODE_REG_PAIR16")

    def handle_store(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b101:  # MODE_REG_ABS16
                _, _, reg_s, addr = decoded
                val = self.reg_get(reg_s)
                self.write_u8(addr, val)
            case 0b110:  # MODE_REG_PAIR16
                _, _, reg_s, reg_pair = decoded
                hi = self.reg_get(reg_pair)
                lo = self.reg_get((reg_pair + 1) & 0x0F)
                addr = (hi << 8) | lo
                val = self.reg_get(reg_s)
                self.write_u8(addr, val)
            case _:
                raise RuntimeError("STORE requires MODE_REG_ABS16 or MODE_REG_PAIR16")

    def handle_move(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                self.reg_set(reg_d, imm8)
                self.update_ZN_from8(imm8)
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                v = self.reg_get(reg_s)
                self.reg_set(reg_d, v)
                self.update_ZN_from8(v)
            case _:
                raise RuntimeError("MOVE supports MODE_REG_IMM8 or MODE_REG_REG")

    def handle_push(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b010:  # MODE_IMM8_ONLY
                _, _, imm8 = decoded
                self.push8(imm8)
            case 0b001:  # MODE_SINGLE_REG
                _, _, reg_s = decoded
                v = self.reg_get(reg_s)
                self.push8(v)
            case _:
                raise RuntimeError("PUSH supports MODE_IMM8_ONLY or MODE_SINGLE_REG")

    def handle_pop(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b001:  # MODE_SINGLE_REG
                _, _, reg_d = decoded
                v = self.pop8()
                self.reg_set(reg_d, v)
                self.update_ZN_from8(v)
            case _:
                raise RuntimeError("POP expects MODE_SINGLE_REG")

    def handle_add(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                a = self.reg_get(reg_d); b = imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                a = self.reg_get(reg_d); b = self.reg_get(reg_s)
            case _:
                raise RuntimeError("ADD supports MODE_REG_IMM8 or MODE_REG_REG")
        
        r, carry, v = self._add_core(a, b)
        self.reg_set(reg_d, r)
        self.set_flag(FLAG_C, carry)
        self.set_flag(FLAG_V, v)
        self.update_ZN_from8(r)

    def handle_addc(self, decoded):
        c = self.get_flag(FLAG_C)
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                a = self.reg_get(reg_d); b = imm8 + c
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                a = self.reg_get(reg_d); b = self.reg_get(reg_s) + c
            case _:
                raise RuntimeError("ADDC supports MODE_REG_IMM8 or MODE_REG_REG")
        
        r, carry, v = self._add_core(a, b)
        self.reg_set(reg_d, r)
        self.set_flag(FLAG_C, carry)
        self.set_flag(FLAG_V, v)
        self.update_ZN_from8(r)

    def handle_sub(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                a = self.reg_get(reg_d); b = imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                a = self.reg_get(reg_d); b = self.reg_get(reg_s)
            case _:
                raise RuntimeError("SUB supports MODE_REG_IMM8 or MODE_REG_REG")
        
        r, borrow, v = self._sub_core(a, b)
        self.reg_set(reg_d, r)
        self.set_flag(FLAG_C, borrow)
        self.set_flag(FLAG_V, v)
        self.update_ZN_from8(r)

    def handle_subb(self, decoded):
        bi = self.get_flag(FLAG_C)
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                a = self.reg_get(reg_d); b = imm8 + bi
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                a = self.reg_get(reg_d); b = self.reg_get(reg_s) + bi
            case _:
                raise RuntimeError("SUBB supports MODE_REG_IMM8 or MODE_REG_REG")
        
        r, borrow, v = self._sub_core(a, b)
        self.reg_set(reg_d, r)
        self.set_flag(FLAG_C, borrow)
        self.set_flag(FLAG_V, v)
        self.update_ZN_from8(r)

    def handle_inc(self, decoded):
        _, mode, *rest = decoded
        if mode != MODE_SINGLE_REG:
            raise RuntimeError("INC expects MODE_SINGLE_REG")
        _, _, reg_d = decoded
        v = mask8(self.reg_get(reg_d) + 1)
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_dec(self, decoded):
        _, mode, *rest = decoded
        if mode != MODE_SINGLE_REG:
            raise RuntimeError("DEC expects MODE_SINGLE_REG")
        _, _, reg_d = decoded
        v = mask8(self.reg_get(reg_d) - 1)
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_shl(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                cnt = imm8 & 7
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                cnt = self.reg_get(reg_s) & 7
            case _:
                raise RuntimeError("SHL supports MODE_REG_IMM8 or MODE_REG_REG")
        
        v = mask8(self.reg_get(reg_d) << cnt)
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_shr(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                cnt = imm8 & 7
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                cnt = self.reg_get(reg_s) & 7
            case _:
                raise RuntimeError("SHR supports MODE_REG_IMM8 or MODE_REG_REG")
        
        v = (self.reg_get(reg_d) >> cnt) & 0xFF
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_and(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                v = self.reg_get(reg_d) & imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                v = self.reg_get(reg_d) & self.reg_get(reg_s)
            case _:
                raise RuntimeError("AND supports MODE_REG_IMM8 or MODE_REG_REG")
        
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_or(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                v = self.reg_get(reg_d) | imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                v = self.reg_get(reg_d) | self.reg_get(reg_s)
            case _:
                raise RuntimeError("OR supports MODE_REG_IMM8 or MODE_REG_REG")
        
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_nor(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                v = (~(self.reg_get(reg_d) | imm8)) & 0xFF
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                v = (~(self.reg_get(reg_d) | self.reg_get(reg_s))) & 0xFF
            case _:
                raise RuntimeError("NOR supports MODE_REG_IMM8 or MODE_REG_REG")
        
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_not(self, decoded):
        _, mode, *rest = decoded
        if mode != MODE_SINGLE_REG:
            raise RuntimeError("NOT expects MODE_SINGLE_REG")
        _, _, reg_d = decoded
        v = (~self.reg_get(reg_d)) & 0xFF
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_xor(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                v = self.reg_get(reg_d) ^ imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                v = self.reg_get(reg_d) ^ self.reg_get(reg_s)
            case _:
                raise RuntimeError("XOR supports MODE_REG_IMM8 or MODE_REG_REG")
        
        self.reg_set(reg_d, v)
        self.update_ZN_from8(v)

    def handle_inb(self, decoded):
        _, mode, *rest = decoded
        reg_d = None
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                port = imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                port = self.reg_get(reg_s)
            case _:
                raise RuntimeError("INB supports MODE_REG_IMM8 or MODE_REG_REG")
        
        val = self.ports[port & 0xFF]
        self.reg_set(reg_d, val)
        self.update_ZN_from8(val)

    def handle_outb(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                val = self.reg_get(reg_d)
                self.ports[imm8 & 0xFF] = val
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                port = self.reg_get(reg_d)
                val = self.reg_get(reg_s)
                self.ports[port & 0xFF] = val
            case _:
                raise RuntimeError("OUTB supports MODE_REG_IMM8 or MODE_REG_REG")

    def handle_cmp(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b100:  # MODE_REG_IMM8
                _, _, reg_d, imm8 = decoded
                a = self.reg_get(reg_d); b = imm8
            case 0b011:  # MODE_REG_REG
                _, _, reg_d, reg_s = decoded
                a = self.reg_get(reg_d); b = self.reg_get(reg_s)
            case _:
                raise RuntimeError("CMP supports MODE_REG_IMM8 or MODE_REG_REG")
        
        res = (a - b) & 0xFF
        self.set_flag(FLAG_Z, res == 0)
        self.set_flag(FLAG_N, (res & 0x80) != 0)
        self.set_flag(FLAG_C, a < b)

    def handle_jmp(self, decoded):
        _, mode, *rest = decoded
        match mode:
            case 0b111:  # MODE_ABS16_ONLY
                _, _, addr = decoded
                self.PC = addr
            case 0b110:  # MODE_REG_PAIR16
                _, _, reg_d, reg_pair = decoded
                hi = self.reg_get(reg_pair)
                lo = self.reg_get((reg_pair + 1) & 0x0F)
                self.PC = (hi << 8) | lo
            case _:
                raise RuntimeError("JMP expects MODE_ABS16_ONLY or MODE_REG_PAIR16")

    def _conditional_jump(self, decoded, cond:bool):
        if cond:
            self.handle_jmp(decoded)

    def handle_jz(self, decoded):  
        self._conditional_jump(decoded, self.get_flag(FLAG_Z) == 1)
    
    def handle_jnz(self, decoded): 
        self._conditional_jump(decoded, self.get_flag(FLAG_Z) == 0)
    
    def handle_jc(self, decoded):  
        self._conditional_jump(decoded, self.get_flag(FLAG_C) == 1)
    
    def handle_jnc(self, decoded): 
        self._conditional_jump(decoded, self.get_flag(FLAG_C) == 0)

    def handle_int(self, decoded):
        _, mode, *rest = decoded
        if mode != MODE_IMM8_ONLY:
            raise RuntimeError("INT expects MODE_IMM8_ONLY")
        _, _, imm8 = decoded
        print(f"[INT {imm8}] (stub)")
        self.STS |= 1

    def handle_halt(self, decoded):
        self.halted = True
        self.STS |= STS_HALT
        print("HALT: CPU halted")

    # ---------------- execute one ----------------
    def step(self) -> Optional[str]:
        if self.halted:
            return 'halted'
        if self.PC in self.breakpoints:
            return f"breakpoint 0x{self.PC:04X}"
        saved = self.PC
        decoded = self.decode()
        opcode = decoded[0]
        handler = self.handlers.get(opcode)
        if handler is None:
            raise RuntimeError(f"Unknown opcode 0x{opcode:02X} at 0x{saved:04X}")
        return handler(decoded)

    # ---------------- disasm helper ----------------
    def disasm_at(self, addr:int) -> str:
        b0 = self.read_u8(addr)
        opcode = (b0>>3) & 0b11111
        mode = b0 & 0b111
        return f"0x{addr:04X}: OP=0x{opcode:02X} MODE={mode}"

    # ---------------- REPL ----------------
    def repl(self):
        print("Type help for a list of commands.")
        while True:
            try:
                cmd = input("(emu) ").strip().split()
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nbye")
                break

            if not cmd: 
                continue
            
            c = cmd[0].lower()
            try:
                match c:
                    case "load":
                        if len(cmd) < 2:
                            print("usage: load <path>")
                            continue
                        with open(cmd[1], "rb") as fh:
                            self.load_program(fh.read())
                    
                    case "step":
                        res = self.step()
                        if res: 
                            print(res)
                    
                    case "cont":
                        while True:
                            res = self.step()
                            if res:
                                print(res)
                                break
                    
                    case "run":
                        while True:
                            res = self.step()
                            if res:
                                print(res)
                                break
                    
                    case "break":
                        if len(cmd) < 2:
                            print("usage: break <hex>")
                            continue
                        addr = int(cmd[1], 16)
                        self.breakpoints.add(addr)
                        print(f"breakpoint set @ 0x{addr:04X}")
                    
                    case "regs":
                        print(f"PC: 0x{self.PC:04X} SP: 0x{self.SP:04X} F: 0x{self.F:02X} STS: 0x{self.STS:02X}")
                        for k in REG_INDEX:
                            print(f"{k}: 0x{self.reg[k]:02X} ", end="")
                        print()
                    
                    case "mem":
                        if len(cmd) < 3:
                            print("usage: mem <hexaddr> <len>")
                            continue
                        addr = int(cmd[1], 16)
                        ln = int(cmd[2])
                        chunk = bytes(self.memory[addr:addr+ln])
                        for i in range(0, len(chunk), 16):
                            print(f"0x{addr+i:04X} | ", end="")
                            for j in range(16):
                                if i+j < len(chunk):
                                    print(f"{chunk[i+j]:02x} ", end="")
                                else:
                                    print("   ", end="")
                            print()
                    
                    case "disasm":
                        if len(cmd) < 2:
                            print(self.disasm_at(self.PC))
                        else:
                            addr = int(cmd[1], 16)
                            print(self.disasm_at(addr))
                    
                    case "ports":
                        print("ports (nonzero):")
                        for i, v in enumerate(self.ports):
                            if v != 0:
                                print(f" {i:02X}: {v:02X}")
                    
                    case "quit":
                        print("bye")
                        break
                    
                    case "help":
                        print("help: Display this help message")
                        print("load <path>: Load a binary file into memory")
                        print("step: Execute one instruction")
                        print("cont: Continue execution until a breakpoint or halt")
                        print("run: Run until halt")
                        print("break <hex>: Set a breakpoint at address")
                        print("regs: Display register values")
                        print("mem <hex> <len>: Display memory contents")
                        print("disasm [addr]: Disassemble instruction at address (or PC)")
                        print("ports: Display non-zero port values")
                        print("quit: Exit the emulator")
                    
                    case _:
                        print("unknown command", c)
            
            except Exception as e:
                print("Error:", e)

# ---------------- main ----------------
def main():
    cpu = CPU()
    if len(sys.argv) > 1:
        path = sys.argv[1]
        with open(path, "rb") as fh:
            cpu.load_program(fh.read())
    cpu.repl()

if __name__ == "__main__":
    main()