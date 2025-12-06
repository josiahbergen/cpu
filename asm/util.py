import colorama
import sys

class Logger: 
    class Level:
        DEBUG = "debug"
        INFO = "info"
        ERROR = "error"

    def __init__(self, level):
        colorama.init()
        self.level = level
        self.debug_buffer = []
        self.debug_count = 0
        self.flush_interval = 100

    def debug(self, message):
        if self.level == self.Level.DEBUG:
            formatted_message = colorama.Fore.YELLOW + "[DEBUG] " + colorama.Fore.RESET + message
            self.debug_buffer.append(formatted_message)
            self.debug_count += 1
            
            if self.debug_count >= self.flush_interval:
                self.flush_debug()

    def flush_debug(self):
        if self.debug_buffer:
            for msg in self.debug_buffer:
                print(msg, flush=False)
            sys.stdout.flush()  # Flush stdout after all buffered messages
            self.debug_buffer.clear()
            self.debug_count = 0

    def small(self, message):
        print(colorama.Fore.BLACK + message + colorama.Fore.RESET)

    def info(self, message):
        print(colorama.Fore.RESET + message + colorama.Fore.RESET)

    def error(self, message):
        self.flush_debug()
        print(colorama.Fore.RED + "ERROR: " + message + colorama.Fore.RESET)

    def success(self, message):
        print(colorama.Back.GREEN + colorama.Fore.BLACK + message + colorama.Fore.RESET + colorama.Back.RESET)

    def title(self, message):
        print(colorama.Back.BLUE + colorama.Fore.BLACK + message + colorama.Fore.RESET + colorama.Back.RESET)


# EBNF-like grammar
GRAMMAR = r"""
    ?start: line*

    ?line: instr
         | label

    label: LABELNAME ":"

    instr: MNEMONIC operand_list?

    operand_list: operand ("," operand)*

    ?operand: REGISTER_PAIR
            | REGISTER
            | NUMBER
            | LABELNAME

    COMMENT: /;.*/

    # priorities for token matching
    # higher number = higher priority
    MNEMONIC.100: /(LOAD|STORE|MOVE|MOV|PUSH|POP|ADD|ADDC|SUB|SUBB|INC|DEC|SHL|SHR|AND|OR|NOR|NOT|XOR|INB|OUTB|CMP|SEC|CLC|CLZ|JMP|JZ|JNZ|JC|JNC|INT|HALT|NOP)\b/i
    REGISTER_PAIR.90: /(A|B|C|D|X|Y|SP|PC|Z|F|MB|STS):(A|B|C|D|X|Y|SP|PC|Z|F|MB|STS)/i
    REGISTER.80: /(A|B|C|D|X|Y|SP|PC|Z|F|MB|STS)\b/i
    NUMBER.20: /0[xX][0-9a-fA-F]+/i
          | /[bB][01]+/
          | /[0-9]+/
    LABELNAME.10: /[A-Za-z_][A-Za-z0-9_]*/

    %import common.WS
    %ignore WS
    %ignore COMMENT
"""
