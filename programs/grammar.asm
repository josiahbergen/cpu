start:
    LOAD A, 0x1000
    LOAD B, 0x1001
    LOAD C, A:B

    STORE 0x2000, C
    STORE A:B, B
    HLT