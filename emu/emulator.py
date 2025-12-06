
# Goals: 
# Load a binary file
# Emulate CPU instructions
# Provide debugging features (step, continue, breakpoints)

# TODO
# load the contents of test.bin as a bytearray()
# implement the CPU class with registers and memory

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
    
    def load_program(self, path, start=0x0000):
        with open(path, "rb") as f:
            data = f.read()
            
            self.memory[start:start+len(data)] = data 
            self.PC = start 
         
    def step(self):
        # fetch, decode, and execute the next instruction

        pass