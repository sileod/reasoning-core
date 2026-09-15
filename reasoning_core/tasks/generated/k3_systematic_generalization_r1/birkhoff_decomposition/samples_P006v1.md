# Level 0
## Example 1
Prompt:
The doubly stochastic matrix has rows: [1/6 5/6 0] [0 0 1] [5/6 1/6 0]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
1-2-0 | 5/6; 0-2-1 | 1/6

## Example 2
Prompt:
The doubly stochastic matrix has rows: [0 1/6 5/6] [1 0 0] [0 5/6 1/6]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
2-0-1 | 5/6; 1-0-2 | 1/6

# Level 2
## Example 1
Prompt:
The doubly stochastic matrix has rows: [1/8 0 7/8] [3/8 1/2 1/8] [1/2 1/2 0]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
2-1-0 | 1/2; 2-0-1 | 3/8; 0-2-1 | 1/8

## Example 2
Prompt:
The doubly stochastic matrix has rows: [1/8 7/8 0] [0 1/8 7/8] [7/8 0 1/8]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
1-2-0 | 7/8; 0-1-2 | 1/8

# Level 5
## Example 1
Prompt:
The doubly stochastic matrix has rows: [1/14 0 11/14 1/14 1/14] [4/7 1/14 0 1/14 2/7] [0 6/7 0 1/14 1/14] [1/7 0 1/14 11/14 0] [3/14 1/14 1/7 0 4/7]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
3-4-1-2-0 | 1/14; 2-4-1-3-0 | 1/7; 2-0-4-3-1 | 1/14; 0-4-1-3-2 | 1/14; 4-1-3-0-2 | 1/14; 2-3-1-0-4 | 1/14; 2-0-1-3-4 | 1/2

## Example 2
Prompt:
The doubly stochastic matrix has rows: [3/7 3/14 5/14 0 0] [3/14 0 0 11/14 0] [0 3/7 0 3/14 5/14] [5/14 0 9/14 0 0] [0 5/14 0 0 9/14]. Write its Birkhoff-von Neumann decomposition as a weighted sum of permutation matrices. Use the canonical greedy residual algorithm: at each step, among the remaining rows and columns, take the permutation that maximises the smallest remaining entry (ties broken by lexicographically smallest permutation), subtract that minimum entry from it, and record the permutation and that coefficient, removing cells that reach zero; repeat until no entry remains. Answer with each term as the permutation shown as a hyphen-separated column sequence (row 0 output column, row 1 output column, ...), then a pipe and its coefficient, terms joined by semicolons in discovery order. For example: 2-0-1 | 1/3; 1-2-0 | 1/6.

Answer:
0-3-4-2-1 | 5/14; 2-3-1-0-4 | 5/14; 0-3-1-2-4 | 1/14; 1-0-3-2-4 | 3/14

