import argparse
import colorama as c
import os

from util import Logger, GRAMMAR
from lark import Lark, Token

# JASM assembler written in Python.
# Usage: python asm.py <file> [-o <output file>] [-d <debug>] 

logger = None

OPCODES = {
    "LOAD": 0x0,
    "MOVE": 0x1,
    "STORE": 0x2,
    "PUSH": 0x3,
    "POP": 0x4,
    "ADD": 0x5,
    "SUB": 0x6,
    "SHL": 0x7,
    "SHR": 0x8,
    "AND": 0x9,
    "OR": 0xA,
    "NOR": 0xB,
    "INB": 0xC,
    "OUTB": 0xD,
    "CMP": 0xE,
    "JNZ": 0xF,
}

REGISTERS = {
    "A": 0x0,
    "B": 0x1,
    "X": 0x2,
    "Y": 0x3,
    "SP": 0x4,
    "PC": 0x5,
    "Z": 0x6,
    "F": 0x7
}

OPERAND_TYPES = {
    "LABELNAME": 0,
    "NUMBER": 1,
    "REGISTER": 2,
    "REGISTER_PAIR": 3,
}

OPERAND_TYPE_TO_STRING = {
    OPERAND_TYPES["LABELNAME"]: "LABELNAME",
    OPERAND_TYPES["NUMBER"]: "NUMBER",
    OPERAND_TYPES["REGISTER"]: "REGISTER",
    OPERAND_TYPES["REGISTER_PAIR"]: "REGISTER_PAIR"
}

def parse(file):
    logger.debug("Parsing...")
    try:
        parser = Lark(GRAMMAR)
        tree = parser.parse(open(file).read())
    except Exception as e:
        logger.error(f"Syntax error: {e}")
        exit(1)

    return tree


def validate_instruction_semantics(node):

    def validate_num_operands(required_num, actual_num, mnemonic, current_line, ):
        if actual_num != required_num:
            logger.error(f"{mnemonic} instruction requires {required_num} operands. Got {actual_num} on line {current_line}.")
            exit(1)

    def validate_operand_type(operand_type, operand_index, expected_types, mnemonic, current_line):
        if operand_type not in expected_types:
            logger.error(
                f"{mnemonic} instruction requires "
                f"{', '.join(OPERAND_TYPE_TO_STRING[t] for t in expected_types)} "
                f"as operand {operand_index + 1}. Got {OPERAND_TYPE_TO_STRING[operand_type]} "
                f"on line {current_line}."
            )
            exit(1)

    mnemonic = node.children[0].value
    line = node.children[0].line

    # Handle optional operand_list
    if len(node.children) > 1 and node.children[1].data == "operand_list":
        operands = node.children[1].children
    else:
        operands = []
    optypes = [OPERAND_TYPES[op.type] for op in operands]

    match (mnemonic):
        case "LOAD":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["NUMBER"], OPERAND_TYPES["REGISTER"]], mnemonic, line)
        case "MOVE":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "STORE":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["NUMBER"], OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
        case "PUSH":
            validate_num_operands(1, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "POP":
            validate_num_operands(1, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
        case "ADD":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "SUB":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "SHL":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "SHR":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "AND":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "OR":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "NOR":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "INB":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "OUTB":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
        case "CMP":
            validate_num_operands(2, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["REGISTER"]], mnemonic, line)
            validate_operand_type(optypes[1], 1, [OPERAND_TYPES["REGISTER"], OPERAND_TYPES["NUMBER"]], mnemonic, line)
        case "JNZ":
            validate_num_operands(1, len(optypes), mnemonic, line)
            validate_operand_type(optypes[0], 0, [OPERAND_TYPES["LABELNAME"], OPERAND_TYPES["NUMBER"], OPERAND_TYPES["REGISTER"]], mnemonic, line)
        case _:
            logger.error(f"Unknown instruction: {mnemonic}")
            exit(1)

    logger.debug(f"Validated instruction semantics for {mnemonic} (line {line}).")


def get_instruction_size(mnemonic, operands):
    optypes = [OPERAND_TYPES[op.type] for op in operands]

    match (mnemonic):
        case "LOAD":
            return 3
        case "MOVE":
            return 2
        case "STORE":
            return 3
        case "PUSH":
            if optypes[0] == OPERAND_TYPES["NUMBER"]:
                return 2
            return 1
        case "POP":
            return 1
        case "ADD":
            return 2
        case "SUB":
            return 2
        case "SHL":
            return 2
        case "SHR":
            return 2
        case "AND":
            return 2
        case "OR":
            return 2
        case "NOR":
            return 2
        case "INB":
            return 2
        case "OUTB":
            return 2
        case "CMP":
            return 2
        case "JNZ":
            if optypes[0] == OPERAND_TYPES["NUMBER"]:
                return 3
            return 2
        case _:
            logger.error(f"Unknown instruction: {mnemonic}")
            exit(1)


def assemble(file, output):

    # lexer and parser
    tree = parse(file)

    
    # pass 1: label resolution
    logger.debug("Resolving labels...")
    labels = {}
    pc = 0

    for node in tree.children:

        # Skip comments
        if isinstance(node, Token) and node.type == 'COMMENT':
            continue

        if node.data == "label":
            label_name = node.children[0].value

            if labels.get(label_name):
                logger.error(f"Label {label_name} already defined. Exiting...")
                exit(1)

            labels[label_name] = pc
            logger.debug(f"Found label: {label_name} (at {pc})")
            continue

        if node.data == "instr":
            validate_instruction_semantics(node)
            
            # Get instruction size
            mnemonic = node.children[0].value
            if len(node.children) > 1 and node.children[1].data == "operand_list":
                operands = node.children[1].children
            else:
                operands = []
            size = get_instruction_size(mnemonic, operands)
            pc += size

    # pass 2: instruction assembly
    logger.debug("Generating binary...")
    binary = bytearray()

    return binary

def main():

    c.init()

    argparser = argparse.ArgumentParser(description="JASM assembler")
    argparser.add_argument("file", nargs="?", default="", help="The file to assemble")
    argparser.add_argument("-o", "--output", default="a.bin", help="The output file")
    argparser.add_argument("-d", "--debug", action="store_true", help="Debug output")
    args = argparser.parse_args()

    # initialize logger
    global logger
    logger = Logger(Logger.Level.DEBUG if args.debug else Logger.Level.INFO)
    logger.title("JASM Assembler v1.0")
    logger.info("")

    # check if file is provided
    if not args.file:
        logger.error("No file(s) provided. Exiting...")
        exit(1)

    # check if file exists
    if not os.path.exists(args.file):
        logger.error(f"File {args.file} does not exist. Exiting...")
        exit(1)

    # check if file is an assembly file
    if not args.file.endswith(".asm"):
        logger.error(f"File {args.file} is not an assembly file. Exiting...")
        exit(1)
    
    logger.debug("Init looks good. Starting assembly...")

    # the magic
    assemble(args.file, args.output)

    if logger.level == Logger.Level.DEBUG:
        logger.info("")
    logger.info(f"Created binary file: {args.output}")

    exit(0)

if __name__ == "__main__":
    main()