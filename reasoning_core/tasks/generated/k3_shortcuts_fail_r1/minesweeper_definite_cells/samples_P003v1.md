## Level 0
### Example 1
Prompt:
A partially revealed Minesweeper board has 4 rows and 4 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
? ? ? 1
2 ? ? 1
1 1 1 0
0 0 0 0

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (0,2),(1,1) Safe: (1,2)

### Example 2
Prompt:
A partially revealed Minesweeper board has 4 rows and 4 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
0 0 0 0
1 1 1 1
? 1 ? ?
1 1 ? ?

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (2,0),(2,3) Safe: (2,2),(3,2)

## Level 2
### Example 1
Prompt:
A partially revealed Minesweeper board has 6 rows and 5 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
0 1 ? 2 ?
0 1 ? ? ?
0 ? 1 2 ?
0 ? 0 1 1
1 2 1 1 0
? 2 ? 1 0

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (2,4),(5,0),(5,2) Safe: (1,4),(2,1),(3,1)

### Example 2
Prompt:
A partially revealed Minesweeper board has 6 rows and 5 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
0 0 0 0 0
2 2 1 1 1
? ? 1 ? ?
2 3 2 ? ?
0 1 ? 2 1
0 ? 1 ? ?

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (2,0),(2,1),(2,4),(4,2) Safe: (2,3),(3,3),(5,1),(5,3)

## Level 5
### Example 1
Prompt:
A partially revealed Minesweeper board has 9 rows and 6 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
1 ? ? 1 ? 0
2 ? 3 2 ? 1
1 ? 1 1 ? 1
? 2 1 1 1 1
? 1 0 0 ? 0
1 1 ? ? 1 ?
0 0 0 1 ? ?
1 1 1 ? 2 ?
1 ? 1 ? ? 1

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (0,1),(0,2),(2,1),(2,4),(4,0),(6,4),(8,1) Safe: (0,4),(1,1),(1,4),(3,0),(4,4),(5,2),(5,3),(5,5),(6,5),(7,3),(8,3)

### Example 2
Prompt:
A partially revealed Minesweeper board has 9 rows and 6 columns. Cells showing a number 0-8 are revealed: the number is the count of mines among that cell's 8 neighbors (all adjacent cells in the 8 directions that exist on the board, including diagonals). Cells shown as '?' are hidden.

Grid (rows top to bottom, columns left to right; the top-left cell is (0,0)):
2 ? 1 ? 0 0
? 2 1 0 ? 0
? 1 ? ? 1 1
1 ? 1 ? ? ?
1 ? 1 2 ? 2
1 1 2 3 ? 3
0 0 1 ? ? ?
? 0 1 2 3 ?
0 0 ? 0 0 0

A placement of mines (chosen anywhere among the hidden '?' cells) is CONSISTENT if, for every revealed cell, the number shown equals how many of its 8 neighbors are mines.

Considering only the hidden '?' cells:
- a cell is DEFINITELY MINED if it is a mine in every consistent placement;
- a cell is PROVABLY SAFE if it is NOT a mine in every consistent placement (clicking it would be safe);
- any other hidden cell, whose mine status differs across consistent placements, is ambiguous and must not be listed.

List (1) every DEFINITELY MINED hidden cell and (2) every PROVABLY SAFE hidden cell. Write each coordinate as (row,col); sort each list by row then column, comma-separated, using exactly this format, e.g.
Mined: (0,1),(2,3) Safe: (1,1)
Write None for an empty list, e.g.  Mined: None Safe: (0,2),(3,1)
Answer: Mined: (0,1),(1,0),(3,4),(4,1),(6,3),(6,4),(6,5) Safe: (0,3),(1,4),(2,0),(2,2),(2,3),(3,1),(3,3),(3,5),(7,0),(7,5),(8,2)
