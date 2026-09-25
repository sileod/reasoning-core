## Level 0

### Example 1

**Prompt:**

We have a 3x3 grid where every cell holds a 0 or a 1. The masked cell at row 3, column 3 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..3): 0 1 1
column sums (col 1..3): 0 1 1
region 1 cells [2,3 2,2 1,2] sum to 1
region 2 cells [1,1 2,1] sum to 0
Is the masked cell value uniquely determined across all valid completions? Answer 1 if the value is forced to a single number, 0 if more than one value is possible.
The answer is one integer.

**Answer:**

0

### Example 2

**Prompt:**

We have a 3x3 grid where every cell holds a 0 or a 1. The masked cell at row 3, column 3 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..3): 2 1 0
column sums (col 1..3): 2 1 0
region 1 cells [2,2 1,3 1,2] sum to 1
region 2 cells [2,3 3,1] sum to 0
What value (0 or 1) must the masked cell take in every valid completion?
The answer is one integer.

**Answer:**

0

## Level 2

### Example 1

**Prompt:**

We have a 3x3 grid where every cell holds a 0 or a 1. The masked cell at row 3, column 3 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..3): 2 1 1
column sums (col 1..3): 2 1 1
region 1 cells [2,3 2,1] sum to 1
region 2 cells [2,2 1,1] sum to 1
region 3 cells [1,3] sum to 1
What value (0 or 1) must the masked cell take in every valid completion?
The answer is one integer.

**Answer:**

0

### Example 2

**Prompt:**

We have a 3x3 grid where every cell holds a 0 or a 1. The masked cell at row 3, column 3 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..3): 0 2 1
column sums (col 1..3): 1 1 1
region 1 cells [1,3 3,1] sum to 0
region 2 cells [1,1 1,2] sum to 0
region 3 cells [2,2] sum to 1
What value (0 or 1) must the masked cell take in every valid completion?
The answer is one integer.

**Answer:**

1

## Level 5

### Example 1

**Prompt:**

We have a 4x4 grid where every cell holds a 0 or a 1. The masked cell at row 4, column 4 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..4): 1 1 2 2
column sums (col 1..4): 0 2 2 2
region 1 cells [3,2 1,1 4,2] sum to 2
region 2 cells [4,3 2,1 3,1] sum to 1
region 3 cells [1,3 1,4] sum to 1
region 4 cells [2,2 2,3] sum to 1
What value (0 or 1) must the masked cell take in every valid completion?
The answer is one integer.

**Answer:**

0

### Example 2

**Prompt:**

We have a 4x4 grid where every cell holds a 0 or a 1. The masked cell at row 4, column 4 is hidden; every other cell is present but its value is not stated directly.
Known sums over the visible cells (each excludes the masked cell's own value):
row sums (row 1..4): 2 1 0 2
column sums (col 1..4): 0 2 1 2
region 1 cells [4,3 1,1 3,2] sum to 0
region 2 cells [2,4 4,2 1,4] sum to 2
region 3 cells [3,1 3,3] sum to 0
region 4 cells [2,3 1,2] sum to 1
Is the masked cell value uniquely determined across all valid completions? Answer 1 if the value is forced to a single number, 0 if more than one value is possible.
The answer is one integer.

**Answer:**

1

