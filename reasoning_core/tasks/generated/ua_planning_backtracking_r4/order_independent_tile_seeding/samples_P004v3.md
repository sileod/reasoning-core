# order_independent_tile_seeding samples

Task: choose a smallest forcing seed of board cells (under per-edge glue
strengths and a temperature) so that every maximal legal attachment order
places exactly all board cells.

## Level 0

### Prompt

```
Tile-assembly growth runs on a 2 by 2 board whose 4 cells are numbered row-major from 0 (cell at row r, column c has index r*2+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 1, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 1.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 2 by 2 board. The target is that exactly all 4 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 2:2, 2:2, 1:2, 2:2
cell 1 (row 0, column 1): 1:1, 2:2, 1:2, 1:1
cell 2 (row 1, column 0): 2:1, 0:1, 1:1, 2:1
cell 3 (row 1, column 1): 1:1, 0:1, 1:1, 0:1

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 4 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 1

0,1

## Level 0

### Prompt

```
Tile-assembly growth runs on a 2 by 2 board whose 4 cells are numbered row-major from 0 (cell at row r, column c has index r*2+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 1, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 1.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 2 by 2 board. The target is that exactly all 4 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 1:2, 2:1, 0:2, 1:1
cell 1 (row 0, column 1): 2:1, 1:2, 0:1, 2:1
cell 2 (row 1, column 0): 1:1, 1:2, 1:1, 2:1
cell 3 (row 1, column 1): 0:1, 2:1, 1:2, 1:1

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 4 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 2

0

## Level 2

### Prompt

```
Tile-assembly growth runs on a 2 by 4 board whose 8 cells are numbered row-major from 0 (cell at row r, column c has index r*4+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 1, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 1.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 2 by 4 board. The target is that exactly all 8 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 3:2, 1:1, 1:2, 3:1
cell 1 (row 0, column 1): 0:2, 3:2, 0:2, 3:1
cell 2 (row 0, column 2): 3:1, 2:1, 1:2, 0:2
cell 3 (row 0, column 3): 2:2, 2:2, 3:1, 1:2
cell 4 (row 1, column 0): 1:1, 3:2, 0:2, 0:1
cell 5 (row 1, column 1): 1:1, 0:2, 2:2, 1:2
cell 6 (row 1, column 2): 0:1, 0:1, 2:2, 0:2
cell 7 (row 1, column 3): 1:1, 1:1, 0:1, 0:1

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 8 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 1

0,1,2,3,5

## Level 2

### Prompt

```
Tile-assembly growth runs on a 2 by 4 board whose 8 cells are numbered row-major from 0 (cell at row r, column c has index r*4+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 1, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 1.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 2 by 4 board. The target is that exactly all 8 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 2:2, 3:1, 0:1, 0:2
cell 1 (row 0, column 1): 1:1, 1:1, 2:2, 3:1
cell 2 (row 0, column 2): 0:2, 1:1, 0:1, 0:1
cell 3 (row 0, column 3): 2:1, 2:1, 3:2, 3:1
cell 4 (row 1, column 0): 0:1, 0:1, 2:1, 1:1
cell 5 (row 1, column 1): 2:2, 3:1, 0:2, 1:1
cell 6 (row 1, column 2): 2:1, 1:1, 0:2, 0:2
cell 7 (row 1, column 3): 0:1, 1:2, 1:1, 0:1

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 8 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 2

0,2,3,6,7

## Level 5

### Prompt

```
Tile-assembly growth runs on a 3 by 4 board whose 12 cells are numbered row-major from 0 (cell at row r, column c has index r*4+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 2, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 2.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 3 by 4 board. The target is that exactly all 12 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 3:1, 0:1, 1:1, 0:2
cell 1 (row 0, column 1): 0:2, 2:1, 3:1, 2:1
cell 2 (row 0, column 2): 2:2, 0:2, 1:1, 4:1
cell 3 (row 0, column 3): 4:2, 4:2, 3:2, 4:1
cell 4 (row 1, column 0): 0:2, 0:1, 2:1, 0:2
cell 5 (row 1, column 1): 1:1, 1:1, 3:2, 2:2
cell 6 (row 1, column 2): 4:1, 0:1, 3:1, 1:1
cell 7 (row 1, column 3): 3:1, 3:1, 4:2, 3:1
cell 8 (row 2, column 0): 4:1, 1:1, 0:2, 4:2
cell 9 (row 2, column 1): 0:1, 1:1, 0:1, 4:1
cell 10 (row 2, column 2): 2:1, 2:2, 1:1, 3:1
cell 11 (row 2, column 3): 2:1, 4:1, 2:1, 4:1

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 12 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 1

0,1,2,4,5,6,7,8,9,10,11

## Level 5

### Prompt

```
Tile-assembly growth runs on a 2 by 6 board whose 12 cells are numbered row-major from 0 (cell at row r, column c has index r*6+c).
Each cell holds its own tile; a tile's four edges (up, right, down, left) each carry a glue label with a strength. Seeding a cell places its tile from the start. At temperature 2, an unseeded cell may be placed once the total strength of glue pairs it shares with already-placed orthogonal neighbours (a pair counts only when the two tiles give the same label on the shared edge, and contributes that tile's strength) reaches 2.
Placement may proceed in any order, and it continues until no further cell can be placed, always staying inside the 2 by 6 board. The target is that exactly all 12 cells end up placed.
Tile glues (up, right, down, left; each 'label:strength'):
cell 0 (row 0, column 0): 2:1, 1:1, 4:2, 3:1
cell 1 (row 0, column 1): 2:1, 0:1, 2:1, 0:2
cell 2 (row 0, column 2): 2:1, 4:2, 4:1, 4:2
cell 3 (row 0, column 3): 3:2, 3:2, 4:1, 4:1
cell 4 (row 0, column 4): 1:2, 1:1, 3:2, 0:1
cell 5 (row 0, column 5): 1:1, 0:2, 4:2, 3:2
cell 6 (row 1, column 0): 3:1, 2:2, 2:1, 3:2
cell 7 (row 1, column 1): 3:2, 4:1, 4:2, 2:2
cell 8 (row 1, column 2): 1:2, 0:2, 0:2, 2:1
cell 9 (row 1, column 3): 3:2, 2:1, 0:2, 4:2
cell 10 (row 1, column 4): 0:2, 2:2, 3:1, 3:2
cell 11 (row 1, column 5): 4:2, 3:2, 2:1, 2:2

Give the smallest set of cells such that seeding exactly those cells forces every maximal legal attachment sequence to place exactly all 12 cells (and nothing else). If several smallest forcing seeds exist, give the lexicographically smallest (smallest first cell, then next, ...).

Answer with only a comma-separated, sorted list of cell indices, e.g. '2,5' or '0,3,7'.
```

### Answer 2

0,1,3,4,5,6,8,9

