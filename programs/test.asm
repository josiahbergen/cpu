start:
    ; Initialize: fib(0) = 0, fib(1) = 1
    MOVE A, 0x00      ; A = fib(n-2) = 0
    MOVE B, 0x01      ; B = fib(n-1) = 1
    
    ; Store first two Fibonacci numbers
    MOVE X, 0x00      ; X = low byte of address
    MOVE Y, 0xC0      ; Y = high byte (0xC000)
    STORE XY, A       ; Store fib(0) = 0 at 0xC000
    ADD X, 1          ; Increment address
    STORE XY, B       ; Store fib(1) = 1 at 0xC001
    
    ; Initialize loop counter (compute 10 more numbers)
    MOVE X, 0x0A      ; X = loop counter (10 iterations)
    STORE 0xFFF0, X   ; Store counter in scratch memory
    
    ; Initialize address offset
    MOVE X, 0x02      ; X = address offset (start at position 2)
    STORE 0xFFF1, X   ; Store offset in scratch memory
    
    ; Restore A and B for Fibonacci computation
    MOVE A, 0x00      ; A = fib(n-2) = 0
    MOVE B, 0x01      ; B = fib(n-1) = 1
    
loop:
    ; Compute fib(n) = fib(n-2) + fib(n-1)
    ; A = fib(n-2), B = fib(n-1)
    MOVE X, A         ; X = fib(n-2)
    ADD X, B          ; X = fib(n-2) + fib(n-1) = fib(n)
    
    ; Store fib(n) at address 0xC000 + offset
    STORE 0xFFF2, X   ; Save fib(n) temporarily
    LOAD X, 0xFFF1    ; Load offset
    MOVE Y, 0xC0      ; Y = high byte
    LOAD A, 0xFFF2    ; Load fib(n) into A temporarily
    STORE XY, A       ; Store fib(n) at address
    ADD X, 1          ; Increment offset
    STORE 0xFFF1, X   ; Save offset back
    
    ; Update: fib(n-2) = fib(n-1), fib(n-1) = fib(n)
    LOAD X, 0xFFF2    ; Load fib(n)
    MOVE A, B         ; A = fib(n-1) (new fib(n-2))
    MOVE B, X         ; B = fib(n) (new fib(n-1))
    
    ; Decrement loop counter
    LOAD X, 0xFFF0    ; Load counter
    SUB X, 1          ; Decrement counter
    STORE 0xFFF0, X   ; Save counter back
    
    ; Check if counter is zero
    CMP X, 0x00
    JNZ loop          ; Continue if not zero
    
end:
