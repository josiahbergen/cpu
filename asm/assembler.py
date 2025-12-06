"""
Core assembly logic: label resolution and binary generation.
"""

from lark import Token
from instructions import (
    REGISTERS,
    validate_instruction_semantics, get_instruction_size
)


def resolve_labels(tree, logger):
    """
    Pass 1: Resolve all labels and calculate their addresses.
    Returns a dictionary mapping label names to addresses.
    """
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
            validate_instruction_semantics(node, logger)
            mnemonic = node.children[0].value.upper()

            # safely get operands
            if len(node.children) > 1 and node.children[1].data == "operand_list":
                operands = node.children[1].children
            else:
                operands = []

            # get instruction size
            size = get_instruction_size(mnemonic, operands)
            if size is None:
                logger.error(f"Bad instruction: {mnemonic} on line {node.children[0].line}")
                exit(1)
            pc += size
            logger.debug(f"Instruction {mnemonic} at PC={pc-size}, size={size}")

    return labels


def parse_number(value):
    # turn number string into an integer
    value = value.strip()

    if value.lower().startswith("0x"):
        # hex
        return int(value, 16)
    elif value.lower().startswith("b"):
        # binary
        return int(value[1:], 2)
    else:
        # decimal
        return int(value, 10)


def encode_register(reg_name, logger=None):
    """Encode a register name to its numeric value."""
    reg_val = REGISTERS.get(reg_name.upper())
    if reg_val is None:
        if logger:
            logger.error(f"Unknown register: {reg_name}")
        else:
            raise ValueError(f"Unknown register: {reg_name}")
        exit(1)
    return reg_val


def encode_register_pair(pair_str, logger=None):
    # split register pair string into two registers
    parts = pair_str.split(":")
    if len(parts) != 2:
        return None, None
    # encode each register
    reg1 = encode_register(parts[0].strip(), logger)
    reg2 = encode_register(parts[1].strip(), logger)
    return reg1, reg2


def generate_binary(tree, labels, logger):
    return bytearray()