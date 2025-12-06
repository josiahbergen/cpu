
# Goals: 
# Load a binary file
# Emulate CPU instructions
# Provide debugging features (step, continue, breakpoints)

# TODO
# load the contents of test.bin as a bytearray()
# implement the CPU class with registers and memory

import array


class Instruction:
    def __init__(self, binary):
        self.binary = binary

    def parse(self):
        # parse the binary instruction into opcode and operands
        pass

    def execute(self, cpu):
        # execute the instruction on the given CPU state
        pass
        
class CPU:
    def __init__(self):
        # initialize CPU registers and state
        #8-bit GPRs
        self.reg = {
           'A': 0,
           'B': 0,
           'C': 0,
           'D': 0,
           'X': 0,  # low byte of XY
           'Y': 0,  # high byte of XY    
        }
        # Special registers 
        self.PC = 0
        self.SP = 0xFEFF
        self.F = 0 # flags register 
        self.STS = 0 # status register
        self.Z = 0 # zero register
        self.MB = 0 # memory buffer register
        
        #Full 64KB
        self.memory = bytearray(65536)
    
    def load_program(self, path):
        with open(path, "rb") as f:
            data = f.read()

            print(f"Loaded {len(data)} bytes from {path}")
            
            self.memory[0:len(data)] = data 
            self.PC = 0 
         
  
    def fetch_byte(self):
        b = self.memory[self.PC]
        self.PC = (self.PC + 1) & 0xFFFF
        return b
    
    def decode(self):
        
        first = self.fetch_byte()  

        opcode = first >> 2       # upper 6 bits
        mode   = first & 0b11     # lower 2 bits
        
        # Start empty. We'll fill in what each mode actually uses.
        reg1 = reg2 = None
        imm8 = None
        imm16 = None
        addr = None
        
        # This is the official decoding table.
        if mode == 0b00:
            # register–register
            d = self.fetch_byte()
            reg1 = d >> 4
            reg2 = d & 0xF
            return (opcode, mode, reg1, reg2)

        elif mode == 0b01:
            # register + immediate 8
            r = self.fetch_byte()
            reg1 = r >> 4
            imm8 = self.fetch_byte()
            return (opcode, mode, reg1, imm8)

        elif mode == 0b10:
            # register pair + immediate 16
            d = self.fetch_byte()
            reg1 = d >> 4
            reg2 = d & 0xF
            lo = self.fetch_byte()
            hi = self.fetch_byte()
            imm16 = (hi << 8) | lo
            return (opcode, mode, reg1, reg2, imm16)

        elif mode == 0b11:
            # register + absolute address
            r = self.fetch_byte()
            reg1 = r >> 4
            lo = self.fetch_byte()
            hi = self.fetch_byte()
            addr = (hi << 8) | lo
            return (opcode, mode, reg1, addr)
        
        def step(self):
            decoded = self.decode()
            opcode = decoded[0]

            handler = self.handlers.get(opcode)
            if handler is None:
                raise Exception(f"Unknown opcode {opcode}")

        return handler(*decoded)    
           

def main():
    cpu = CPU()
    cpu.load_program("binaries/test.bin")
    
if __name__ == "__main__":
    main()