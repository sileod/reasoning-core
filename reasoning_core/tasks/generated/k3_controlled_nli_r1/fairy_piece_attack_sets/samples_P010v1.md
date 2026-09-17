## Level 0 example 1

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), a threeleaper (leaper) stands on b5.
Other pieces on the board: b6 (enemy), e5 (friendly), g4 (friendly).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the threeleaper can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

b2,b8

## Level 0 example 2

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), a queen (rider) stands on b7.
Other pieces on the board: a2 (friendly), b8 (friendly), e5 (enemy).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the queen can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

a6,a7,a8,b1,b2,b3,b4,b5,b6,c6,c7,c8,d5,d7,e4,e7,f3,f7,g2,g7,h1,h7

## Level 2 example 1

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), a queen (rider) stands on d8.
Other pieces on the board: a3 (friendly), b3 (friendly), b4 (friendly), d1 (friendly), d4 (friendly), d7 (friendly), f6 (enemy), f8 (friendly), g3 (enemy).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the queen can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

a5,a8,b6,b8,c7,c8,e7,e8,f6

## Level 2 example 2

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), a zebra (leaper) stands on g5.
Other pieces on the board: d1 (friendly), e2 (enemy), e4 (enemy), e5 (friendly), e6 (friendly), f2 (enemy), g4 (enemy), h5 (friendly), h6 (friendly).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the zebra can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

d3,d7,e2,e8

## Level 5 example 1

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), a rook (rider) stands on d2.
Other pieces on the board: a4 (enemy), b2 (enemy), b7 (enemy), c5 (enemy), c6 (enemy), d4 (enemy), d6 (enemy), d8 (enemy), e1 (friendly), e2 (friendly), e3 (friendly), e6 (friendly), f5 (friendly), f6 (friendly), g8 (enemy), h1 (friendly), h2 (enemy), h5 (friendly).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the rook can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

b2,c2,d1,d3,d4

## Level 5 example 2

### Prompt

On this otherwise empty 8x8 chessboard (files a-h, ranks 1-8), an alfil (leaper) stands on g1.
Other pieces on the board: a1 (enemy), a2 (friendly), a5 (friendly), b1 (enemy), b2 (friendly), b5 (enemy), b8 (enemy), c6 (friendly), c7 (friendly), d3 (friendly), d5 (friendly), e8 (friendly), f1 (enemy), f2 (enemy), f3 (enemy), g3 (enemy), g5 (enemy), h4 (enemy).

Rules for fairy pieces:
- A leaper jumps by fixed offsets (e.g. a camel moves by 3+1) and is never blocked.
- A rider slides along rays (like rook/bishop) until it would leave the board; it stops
  before a friendly piece, or captures an enemy piece and stops there.
- A hopper moves along a ray exactly like a rider while traveling, but instead of
  stopping on the first piece, it must jump over exactly one piece (the screen) of
  either colour and land on the square immediately beyond it: that square must be
  empty, or hold an enemy piece which is captured. If there is no screen on a ray
  the hopper cannot move along that ray.
- A locust moves along a ray, captures by jumping over exactly one enemy piece
  (the first piece on the ray) and must land on the square immediately beyond it,
  which must be empty. A locust captures no other way and only captures; a ray
  whose first piece is absent or friendly gives no move.

List every square the alfil can move to, including capture squares, as a comma-separated list of algebraic coordinates in ascending alphabetical order (file letter first, then rank, e.g. a1, b3, c4). Give only the list.

### Answer

f2,h2
