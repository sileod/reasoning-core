# Level 0
## Example 1
**Prompt:**
Consider a 4x4 nonogram grid. Row i (0-indexed) has clues [[3], [2], [1], [1, 1]] and column j has clues [[0], [2, 1], [2], [1, 2]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 2, column 1? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** W

## Example 2
**Prompt:**
Consider a 4x4 nonogram grid. Row i (0-indexed) has clues [[1], [1, 1], [3], [3]] and column j has clues [[2], [2], [3], [2]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 0, column 2? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** W

# Level 2
## Example 1
**Prompt:**
Consider a 7x7 nonogram grid. Row i (0-indexed) has clues [[1, 1], [1, 1], [2, 2], [4, 1], [2, 2], [2], [1, 3, 1]] and column j has clues [[4, 1], [2], [2, 2, 1], [3, 1], [1, 2], [3], [1, 1]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 1, column 6? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** W

## Example 2
**Prompt:**
Consider a 7x7 nonogram grid. Row i (0-indexed) has clues [[1, 4], [1, 3], [2, 1, 1], [1, 1, 1], [1, 2], [1, 1], [1, 1, 2]] and column j has clues [[2, 1], [2, 1], [2], [2, 1, 1], [4], [1, 1, 1], [1, 5]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 0, column 4? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** B

# Level 5
## Example 1
**Prompt:**
Consider a 12x12 nonogram grid. Row i (0-indexed) has clues [[2, 1, 4, 1], [1, 1, 3, 1], [12], [2, 6], [4, 1, 1, 1], [2, 1, 5, 1], [3, 1, 1, 1], [1, 4, 2], [2, 1, 3, 1], [1, 2, 4, 1], [5, 4, 1], [3, 2, 1, 2]] and column j has clues [[6, 5], [1, 5, 1, 2], [1, 1, 1, 3], [1, 1, 3, 3], [2, 1, 2], [3, 1, 3, 1], [1, 9], [4, 1, 5], [4, 2, 2], [6, 1, 2], [1, 2, 1, 1], [3, 2, 1, 1]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 0, column 9? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** B

## Example 2
**Prompt:**
Consider a 12x12 nonogram grid. Row i (0-indexed) has clues [[4, 3, 1], [3, 3, 3], [2, 6], [3, 4, 1, 1], [3, 3, 3], [3, 1, 5], [3, 8], [7, 1], [10, 1], [9], [1, 3, 5], [1, 1, 2, 3]] and column j has clues [[2, 1, 1, 3], [2, 4, 2, 1], [2, 4, 3], [1, 1, 2, 4], [3, 6], [2, 7], [5, 6], [1, 10], [1, 6], [8, 2], [2, 3, 2], [9, 1]]. After performing full fixpoint propagation (repeatedly marking cells forced by each line's clue overlap, propagating those marks across crossing lines until no further cell is forced), what is the final known state of the cell at row 3, column 3? Answer with exactly one of B (black/filled), W (white/empty), or ? (still unknown).

**Answer:** W
