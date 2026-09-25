## Level 0

### Example 1

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [3, 2] and backward [3, 3]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 3. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 11

### Example 2

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [3, 1] and backward [-2, 3, 3]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 3. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 8

## Level 2

### Example 1

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [3, -1, 1, 1, -1, -2] and backward [1, 2, -1, -1, -2, 2]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 5. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 7

### Example 2

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [2, 3, 3, 2] and backward [-2, -2, 2, 1, -2, -2]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 5. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 10

## Level 5

### Example 1

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [-2, 3, 1, -2, 2, -1, -2, -1] and backward [-2, -1, 1, 3, 2, 1, -2]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 8. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 2

### Example 2

Two scenarios have been reconciled into forward and backward load sequences over shared time steps: forward [2, -1, 3, -2, 1, -2, 3, 2] and backward [3, 1, -1, -2, 2, 2, 3, 2, 1]. The worst cumulative load of a sequence is the maximum prefixed sum over its steps (the empty prefix counts 0). You may recombine the two sequences by cutting each at exactly one internal splice checkpoint and concatenating a prefix from one scenario with the remaining suffix from the other (keeping relative order within each piece); the concatenation may be built in either order. A recombined schedule is admissible only when its worst cumulative load is at most the history cap of 8. What is the maximum worst cumulative load attainable by any admissible recombined schedule (or by the original schedules if no recombination is admissible)? The answer is a single non-negative integer.

Answer: 17
