loop:
  sub $1 $2 $3
  j loop

jal T
addi $1, $1, 1
sll $1 $1 4
T: sub $1 $2 $3
