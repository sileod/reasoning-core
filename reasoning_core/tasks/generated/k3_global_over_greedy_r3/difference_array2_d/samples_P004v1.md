# Difference array 2D samples (P004v1)

## Level 0

### Example 1

A 4x5 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
0 2 1 4 1
1 1 3 2 3
2 1 3 4 2

Report the entire final grid, all cells, as 4 rows separated by semicolons, each row listing its 5 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 0 1 1 0; 0 3 0 0 0; 0 5 2 2 0; 0 0 0 0 0

### Example 2

A 4x5 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
2 2 3 4 1
1 1 3 2 -1
1 0 2 1 0

Report the entire final grid, all cells, as 4 rows separated by semicolons, each row listing its 5 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 0 0 0 0; 0 -1 0 0 0; 0 -1 1 1 0; 0 0 0 0 0

## Level 2

### Example 1

A 8x11 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
2 1 7 2 4
6 7 7 9 5
1 3 7 10 -4
3 3 5 6 2
6 4 7 7 -2
1 3 4 9 -1
6 9 7 10 -4
0 1 4 10 -4
2 4 6 7 -3

Report the entire final grid, all cells, as 8 rows separated by semicolons, each row listing its 11 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 -4 -4 -4 -4 -4 -4 -4 -4 -4 0; 0 -4 -4 -9 -9 -9 -9 -9 -9 -8 0; 0 0 -4 -9 -12 -12 -12 -9 -9 -8 0; 0 0 -4 -7 -10 -10 -12 -9 -9 -8 0; 0 4 0 -2 -5 -5 -7 -4 -4 -4 0; 0 4 0 -4 -7 -7 -7 -4 -4 -4 0; 0 4 0 -4 -6 -6 -6 1 1 -8 0; 0 0 0 0 0 0 0 0 0 0 0

### Example 2

A 8x11 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
2 7 7 10 2
2 3 7 4 -2
0 3 3 10 -2
4 4 6 8 -1
4 7 6 8 0
5 3 7 9 -3
1 2 4 10 2
4 0 5 5 1
5 9 7 10 0

Report the entire final grid, all cells, as 8 rows separated by semicolons, each row listing its 11 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 0 0 -2 -2 -2 -2 -2 -2 -2 0; 0 0 2 0 0 0 0 0 0 0 0; 0 0 2 -2 0 0 0 2 2 2 0; 0 0 2 0 2 2 2 4 4 4 0; 1 1 1 -1 0 -1 -1 1 2 2 0; 0 0 0 -5 -4 -4 -4 -2 -1 2 0; 0 0 0 -5 -3 -3 -3 -1 -1 2 0; 0 0 0 0 0 0 0 0 0 0 0

## Level 5

### Example 1

A 14x20 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
10 6 13 16 7
0 13 2 16 -6
7 2 13 4 -7
3 7 11 17 -7
6 15 13 16 -1
1 4 7 16 -3
12 10 13 18 -1
4 14 11 19 6
1 1 5 16 1
7 12 9 16 -3
2 5 11 19 -5
9 7 12 17 0
11 14 13 15 4
4 6 10 9 -7
12 5 13 17 -3
1 6 13 8 1
3 3 4 11 -4
9 12 13 19 5

Report the entire final grid, all cells, as 14 rows separated by semicolons, each row listing its 20 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 0 0 0 0 0 0 0 0 0 0 0 0 -6 -6 -6 0 0 0 0; 0 1 1 1 -2 -2 -1 -1 -2 -2 -2 -2 -2 -8 -8 -8 0 0 0 0; 0 1 1 1 -2 -7 -6 -6 -7 -7 -7 -7 -7 -7 -7 -7 -5 -5 -5 0; 0 1 1 -3 -6 -11 -10 -17 -18 -18 -18 -14 -14 -14 -14 -14 -12 -5 -5 0; 0 1 1 1 -2 -7 -13 -20 -21 -14 -14 -14 -14 -14 -8 -8 -6 1 1 0; 0 0 0 0 -3 -8 -14 -21 -22 -15 -15 -15 -15 -15 -9 -9 -6 1 1 0; 0 0 0 0 -3 -8 -14 -21 -22 -15 -15 -15 -15 -15 -9 -10 -6 1 1 0; 0 0 -7 -7 0 -5 -11 -18 -19 -12 -12 -12 -15 -15 -9 -10 -6 1 1 0; 0 0 -7 -7 0 -5 -11 -18 -19 -12 -12 -12 -15 -15 -9 -10 -6 1 1 0; 0 0 -7 -7 0 -5 -11 -18 -19 -12 -12 -12 -7 -7 -1 -2 -1 6 6 0; 0 0 -7 -7 0 -5 3 -4 -5 -5 -5 -5 0 0 6 5 -1 6 6 0; 0 0 -7 -7 0 0 8 8 7 7 7 7 12 12 16 11 5 5 5 0; 0 0 -7 -7 0 -3 5 5 4 4 3 3 8 8 12 7 1 4 5 0; 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

### Example 2

A 14x20 grid of integers starts as all zeros. Each update is a rectangle 'r1 c1 r2 c2 delta' using half-open index ranges: it adds delta to every cell with r1 <= row < r2 and c1 <= col < c2 (0-based, so '0 1 2 3 -4' means add -4 to rows 0-1 and columns 1-2 and '2 3' in the pair is an exclusive upper bound). Apply all of these updates:
11 12 13 15 0
5 7 12 16 2
6 11 9 17 1
9 17 11 18 5
5 0 6 19 -8
10 12 12 14 7
5 15 12 19 -7
12 3 13 16 7
4 6 7 17 -2
1 10 9 16 -7
10 7 11 11 1
7 14 10 19 1
0 2 11 14 3
11 18 12 19 2
12 1 13 12 -5
4 3 11 6 -1
3 18 10 19 2
0 8 6 19 5

Report the entire final grid, all cells, as 14 rows separated by semicolons, each row listing its 20 integers space-separated, in row-major order from cell (0,0). Example for a 2x2 grid: 3 -1; 0 5

**Answer**: 0 0 3 3 3 3 3 3 8 8 8 8 8 8 5 5 5 5 5 0; 0 0 3 3 3 3 3 3 8 8 1 1 1 1 -2 -2 5 5 5 0; 0 0 3 3 3 3 3 3 8 8 1 1 1 1 -2 -2 5 5 5 0; 0 0 3 3 3 3 3 3 8 8 1 1 1 1 -2 -2 5 5 7 0; 0 0 3 2 2 2 1 1 6 6 -1 -1 -1 -1 -4 -4 3 5 7 0; -8 -8 -5 -6 -6 -6 -7 -5 0 0 -7 -7 -7 -7 -10 -17 -12 -10 -8 0; 0 0 3 2 2 2 1 3 3 3 -4 -3 -3 -3 -6 -13 -8 -7 -5 0; 0 0 3 2 2 2 3 5 5 5 -2 -1 -1 -1 -3 -10 -5 -6 -4 0; 0 0 3 2 2 2 3 5 5 5 -2 -1 -1 -1 -3 -10 -5 -6 -4 0; 0 0 3 2 2 2 3 5 5 5 5 5 5 5 3 -4 -6 -1 -4 0; 0 0 3 2 2 2 3 6 6 6 6 5 12 12 2 -5 -7 -2 -7 0; 0 0 0 0 0 0 0 2 2 2 2 2 9 9 2 -5 -7 -7 -5 0; 0 -5 -5 2 2 2 2 2 2 2 2 2 7 7 7 7 0 0 0 0; 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

