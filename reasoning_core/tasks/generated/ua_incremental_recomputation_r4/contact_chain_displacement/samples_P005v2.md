## Level 0
### Prompt
A horizontal chain of 2 ordered rigid bodies sits left to right, indexed 0 (far left) through 1. The initial gap between body i and the body to its right is G_i (i = 0 .. 0). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 4 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [0]
Stops: body 0 stop 2
P = 4

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 2 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 1/2,1/2,S0

### Prompt
A horizontal chain of 2 ordered rigid bodies sits left to right, indexed 0 (far left) through 1. The initial gap between body i and the body to its right is G_i (i = 0 .. 0). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 6 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [0]
Stops: none
P = 6

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 2 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 1,1

## Level 2
### Prompt
A horizontal chain of 4 ordered rigid bodies sits left to right, indexed 0 (far left) through 3. The initial gap between body i and the body to its right is G_i (i = 0 .. 2). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 12 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [4, 3, 1]
Stops: body 0 stop 6; body 1 stop 1
P = 12

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 4 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 5/12,1/12,0,0,S1

### Prompt
A horizontal chain of 4 ordered rigid bodies sits left to right, indexed 0 (far left) through 3. The initial gap between body i and the body to its right is G_i (i = 0 .. 2). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 7 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [3, 5, 5]
Stops: none
P = 7

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 4 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 1,4/7,0,0

## Level 5
### Prompt
A horizontal chain of 7 ordered rigid bodies sits left to right, indexed 0 (far left) through 6. The initial gap between body i and the body to its right is G_i (i = 0 .. 5). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 10 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [1, 3, 6, 0, 1, 8]
Stops: body 0 stop 12; body 1 stop 4; body 2 stop 2; body 3 stop 5; body 4 stop 0; body 6 stop 4
P = 10

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 7 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 1/2,2/5,1/10,0,0,0,0,S1

### Prompt
A horizontal chain of 7 ordered rigid bodies sits left to right, indexed 0 (far left) through 6. The initial gap between body i and the body to its right is G_i (i = 0 .. 5). Each body may carry a fixed stop S_i, the greatest distance in units it may move right before wedging; a body without a listed stop is free to move as far as it is pushed.

A plane pushes the left face of body 0 by a total distance P = 12 (quasistatic gap-closing cascade): the gap to a body's right must fully close before motion transmits to the next body, and a body that reaches its stop wedges there and blocks the plane. If the plane is blocked before traveling the full P, it stops at the blocking body.

Gaps G_i (left to right): [5, 0, 8, 2, 4, 1]
Stops: body 1 stop 0; body 2 stop 9; body 4 stop 6; body 6 stop 10
P = 12

For each body i in index order, output its net displacement as a reduced fraction of P, i.e. moves_i / P. If the plane was blocked, append the stop label of the blocking body, written S_k for block at body k, as a final extra element; if unblocked, list only the 7 fractions.
Answer as comma-separated values, e.g. "1,1/2" (two bodies, displacements P and P/2, unblocked) or "1,0,S1" (two bodies, blocked at body 1).

Answer: 5/12,0,0,0,0,0,0,S1
