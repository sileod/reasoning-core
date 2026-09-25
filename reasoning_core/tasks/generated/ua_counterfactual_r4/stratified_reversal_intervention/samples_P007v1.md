# Samples P007v1 - stratified_reversal_intervention

## Level 0

### Example 1

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 12; the comparison of interest is whether the pooled total is at least the threshold 13.
Stratum 0: [2, 2]; [0, 3]
Stratum 1: [0, 3]; [2, 0]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 13' change from true to false or false to true). Each operation may change a cell by at most 1 in magnitude, and at most 2 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

M0:r1c1+1

### Example 2

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 13; the comparison of interest is whether the pooled total is at least the threshold 22.
Stratum 0: [1, 2]; [1, 3]
Stratum 1: [1, 3]; [1, 1]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 22' change from true to false or false to true). Each operation may change a cell by at most 1 in magnitude, and at most 2 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

IMPOSSIBLE

## Level 2

### Example 1

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 9; the comparison of interest is whether the pooled total is at least the threshold 12.
Stratum 0: [0, 0]; [2, 1]
Stratum 1: [0, 0]; [3, 3]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 12' change from true to false or false to true). Each operation may change a cell by at most 1 in magnitude, and at most 3 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

M0:r1c1+1,M0:r1c2+1,M0:r2c1+1

### Example 2

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 12; the comparison of interest is whether the pooled total is at least the threshold 13.
Stratum 0: [1, 1]; [3, 1]
Stratum 1: [2, 0]; [1, 3]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 13' change from true to false or false to true). Each operation may change a cell by at most 1 in magnitude, and at most 3 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

M0:r1c1+1

## Level 5

### Example 1

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 43; the comparison of interest is whether the pooled total is at least the threshold 46.
Stratum 0: [1, 0, 3]; [3, 0, 1]; [3, 0, 3]
Stratum 1: [2, 1, 0]; [0, 2, 3]; [3, 2, 3]
Stratum 2: [1, 3, 1]; [3, 1, 1]; [2, 0, 1]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 46' change from true to false or false to true). Each operation may change a cell by at most 2 in magnitude, and at most 4 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

M0:r1c1+1,M0:r1c3+2

### Example 2

**Prompt:**

You have stratified count tables (each stratum is a grid of non-negative integers). The pooled total is the sum of every cell across all strata. The current pooled total is 38; the comparison of interest is whether the pooled total is at least the threshold 40.
Stratum 0: [2, 1, 1]; [2, 0, 1]; [0, 2, 2]
Stratum 1: [1, 1, 1]; [0, 2, 0]; [3, 2, 1]
Stratum 2: [1, 2, 3]; [0, 3, 3]; [0, 3, 1]

An operation changes one cell of one stratum by an integer delta (M/+ means records added, D/- means records removed). A valid intervention must keep every cell non-negative and preserve every within-stratum ordering: no two cells in the same stratum that were strictly ordered may end up strictly reversed (equal values may reorder freely). Find the SMALLEST intervention (fewest operations) that flips the pooled comparison (makes 'total >= 40' change from true to false or false to true). Each operation may change a cell by at most 2 in magnitude, and at most 4 operations are permitted.
Answer as a comma-separated canonical sequence of operations, each of the form M{stratum}:r{row}c{column}+{delta} (for an increase) or D{stratum}:r{row}c{column}-{delta} (for a decrease), rows and columns are 1-indexed, e.g. M0:r1c2+1,D1:r2c1-2. If no valid intervention exists, answer exactly IMPOSSIBLE.


**Answer:**

M0:r1c1+2
