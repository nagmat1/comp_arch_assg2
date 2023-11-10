; sum an array
       go   0
0      ld  2 .count     ; r2 has value of counter
       ldi 3 .val1     ; r3 points to first value
       ldi 4 .val2
       ldi 5 .val3       ; r1 contains sum
.loop  ldi 1 0
       add 1 *3      ; r1 = r1 + next array value
       add 1 *4
       st 1 5
       inc 3
       inc 4
       inc 5
       dec 2
       bnz 2 .loop
.count dw   4
.val1  dw   1
       dw   2
       dw   3
       dw   4
.val2  dw   6
       dw   7
       dw   8
       dw   9
.val3  dw   0
       dw   0
       dw   0
       dw   0