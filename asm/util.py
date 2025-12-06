import colorama

class Logger: 
    class Level:
        DEBUG = "debug"
        INFO = "info"
        ERROR = "error"

    def __init__(self, level):
        colorama.init()
        self.level = level

    def debug(self, message):
        if self.level == self.Level.DEBUG:
            print(colorama.Fore.YELLOW + "[DEBUG] " + colorama.Fore.RESET + message)

    def small(self, message):
        print(colorama.Fore.BLACK + message + colorama.Fore.RESET)

    def info(self, message):
        print(colorama.Fore.RESET + message + colorama.Fore.RESET)

    def error(self, message):
        print(colorama.Fore.RED + message + colorama.Fore.RESET)

    def success(self, message):
        print(colorama.Back.GREEN + colorama.Fore.WHITE + message + colorama.Fore.RESET + colorama.Back.RESET)

    def title(self, message):
        print(colorama.Back.BLUE + colorama.Fore.BLACK + message + colorama.Fore.RESET + colorama.Back.RESET)


# EBNF-like Grammar

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
    MNEMONIC.100: /(LOAD|MOVE|MOV|STORE|PUSH|POP|ADD|SUB|SHL|SHR|AND|OR|NOR|INB|OUTB|CMP|JNZ|HLT)\b/i
    REGISTER_PAIR.90: /(A|B|C|D|X|Y|SP|PC|Z|F):(A|B|C|D|X|Y|SP|PC|Z|F)/i
    REGISTER.80: /(A|B|C|D|X|Y|SP|PC|Z|F)\b/i
    LABELNAME.10: /[A-Za-z_][A-Za-z0-9_]*/

    NUMBER: /0[xX][0-9a-fA-F]+/
          | /[bB][01]+/
          | /[0-9]+/

    %import common.WS
    %ignore WS
    %ignore COMMENT
"""


OPERAND_TYPES = {
    "name_operand": "name",
    "number_operand": "number"
}