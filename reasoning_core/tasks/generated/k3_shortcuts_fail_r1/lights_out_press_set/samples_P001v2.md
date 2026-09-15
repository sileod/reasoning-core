# LightsOutPressSet samples

## Level 0

### Example 1

Prompt:

```
Cells are numbered 0..8 in row-major order: the cell at row r, column c has index r*3+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (3 rows, 3 cols):
1 1 1
0 0 0
1 1 1
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
1 7
```

### Example 2

Prompt:

```
Cells are numbered 0..8 in row-major order: the cell at row r, column c has index r*3+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (3 rows, 3 cols):
0 1 1
0 1 1
0 1 1
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
0 1 2 5 6 7 8
```

## Level 2

### Example 1

Prompt:

```
Cells are numbered 0..19 in row-major order: the cell at row r, column c has index r*5+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (4 rows, 5 cols):
1 0 1 0 0
0 0 0 0 0
0 1 1 1 0
1 1 0 0 1
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
0 1 2 4 5 6 7 9 10 12 17 19
```

### Example 2

Prompt:

```
Cells are numbered 0..11 in row-major order: the cell at row r, column c has index r*4+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (3 rows, 4 cols):
0 1 1 0
1 0 1 1
0 1 1 0
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
0 4 6 8
```

## Level 5

### Example 1

Prompt:

```
Cells are numbered 0..20 in row-major order: the cell at row r, column c has index r*3+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (7 rows, 3 cols):
0 0 1
0 1 1
0 0 1
1 1 1
0 0 1
1 0 1
1 1 1
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
0 2 3 9 11 13 16 17 19 20
```

### Example 2

Prompt:

```
Cells are numbered 0..24 in row-major order: the cell at row r, column c has index r*5+c. A 1 means the cell is lit and a 0 means dark. Pressing a cell toggles it and every orthogonally adjacent cell (up, down, left, right, when present). Each cell may be pressed at most once.
Grid (5 rows, 5 cols):
1 1 0 1 1
0 1 1 1 1
1 1 0 0 0
1 0 1 1 0
0 0 0 1 1
Give the set of cells to press (sorted ascending, space-separated indices) so that every cell ends dark, or the exact word NONE if no such set exists. The pattern of 1s is guaranteed to have a unique answer if pressable; it is NONE exactly when no set of presses can darken every lit cell.
Answer:
```

Answer:

```
NONE
```
