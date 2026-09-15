# Level 0
## Example 1
Prompt:
An 4x4 grid holds opaque cells (#) and light sources (A: source A). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
. . . A
# . . .
. # . .
. . . .

A new opaque cell is inserted at (0,1).

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(0,0),(0,1)];A:[(0,2),(0,3),(1,3),(2,3),(3,3)]

## Example 2
Prompt:
An 4x4 grid holds opaque cells (#) and light sources (A: source A). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
. . . .
. # . .
# A . .
. . . .

A new opaque cell is inserted at (2,2).

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(2,2),(2,3)];A:[(2,1),(3,1)]

# Level 2
## Example 1
Prompt:
An 5x5 grid holds opaque cells (#) and light sources (A: source A, B: source B). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
# # . . #
# . . A B
. . . . .
. . . . .
. . . . .

A new opaque cell is inserted at (2,3).

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A B, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(2,3),(3,3),(4,3)];A:[(0,3),(1,1),(1,2),(1,3),(1,4)];B:[(1,1),(1,2),(1,3),(1,4),(2,4),(3,4),(4,4)]

## Example 2
Prompt:
An 5x6 grid holds opaque cells (#) and light sources (A: source A, B: source B). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
. . . . A .
. . . . . .
. B . . . .
. # . # . .
# . . # . .

A new opaque cell is inserted at (3,4).

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A B, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(3,4),(4,4)];A:[(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(1,4),(2,4)];B:[(0,1),(1,1),(2,0),(2,1),(2,2),(2,3),(2,4),(2,5)]

# Level 5
## Example 1
Prompt:
An 9x9 grid holds opaque cells (#) and light sources (A: source A, B: source B, C: source C). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
. . . A . . . . .
. . . . . # # . .
. # . . . . . . .
. . # # . . # . .
. . # . . . . . .
. . B . . . . . .
. . . . . . . . .
. . . . . . . . .
. C . . . . . . .

The opaque cell at (2,1) is removed.

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A B C, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(1,1),(2,1)];A:[(0,0),(0,1),(0,2),(0,3),(0,4),(0,5),(0,6),(0,7),(0,8),(1,3),(2,3)];B:[(5,0),(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(6,2),(7,2),(8,2)];C:[(0,1),(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,0),(8,1),(8,2),(8,3),(8,4),(8,5),(8,6),(8,7),(8,8)]

## Example 2
Prompt:
An 8x9 grid holds opaque cells (#) and light sources (A: source A, B: source B, C: source C). A source lights its own cell and every cell in a straight line in each of the four cardinal directions (up, down, left, right) from it, stopping when it reaches an opaque cell or the grid edge; that opaque cell and everything beyond it in that direction stay dark. Cells are referenced (row,column), 0-indexed.

Grid before the change:
. . . . . . # . .
. A . . . . . . .
. . . . . . . . #
. # . . . . . . .
. . # . # . . . .
. . . . . B . . .
. . . . . . . # .
C . # . . . . . .

A new opaque cell is inserted at (1,4).

Report (1) the set of cells whose lit status flips between lit and dark because of this change and (2) for each source in order A B C, its covered set (the cells it lights) in the after configuration. Sort every coordinate list lexicographically by (row,column), and list each set's cells also sorted lexicographically.

Answer as one line in the format flipped:[(r,c),(r,c),...];A:[(r,c),...];B:[(r,c),...] .

Answer:
flipped:[(1,4),(1,6),(1,7),(1,8)];A:[(0,1),(1,0),(1,1),(1,2),(1,3),(2,1)];B:[(0,5),(1,5),(2,5),(3,5),(4,5),(5,0),(5,1),(5,2),(5,3),(5,4),(5,5),(5,6),(5,7),(5,8),(6,5),(7,5)];C:[(0,0),(1,0),(2,0),(3,0),(4,0),(5,0),(6,0),(7,0),(7,1)]

