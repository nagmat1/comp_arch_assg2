    go 100
100 ld 2 200 ; r2 has value of counter
    ldi 3 201 ; r3 points to first value
    ldi 1 0 ; r1 contains sum
103 add 1 *3 ; r1 = r1 + next array value
    inc 3
    dec 2
    st 1 1000
    bnz 2 103
    sys 1 16
16 dw 0
200 dw 5
    dw 3
    dw 2
    dw 0
    dw 8
    dw 100
    end