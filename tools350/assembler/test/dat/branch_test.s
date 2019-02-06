loop:
  sub $1 $2 $3
  bne $1, $0, loop

bne $2, $1, T
addi $1, $1, 1
sll $1 $1 4
T: sub $1 $2 $3
