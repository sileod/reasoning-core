## Level 0
### Example 1
**Prompt:**
Given the symbol sequence S = [0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1], count how many occurrences of symbol 0 appear in positions lo = 1 to hi = 16 (0-indexed, hi exclusive). A wavelet tree descends the bit partition of S answering rank queries level by level. Report the count as one integer.

**Answer:**
7

### Example 2
**Prompt:**
Given the symbol sequence S = [1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0], find the 0-indexed position of the 2nd occurrence of symbol 0 in S. A wavelet tree answers select queries by descending the bit partition. Report the position as one integer.

**Answer:**
2

## Level 2
### Example 1
**Prompt:**
Given the symbol sequence S = [1, 0, 0, 1, 2, 3, 2, 0, 0, 3, 3, 1, 0, 2, 0, 3, 2, 1, 0, 3, 3, 3, 2, 3, 3, 0, 2, 0], count how many occurrences of symbol 1 appear in positions lo = 0 to hi = 15 (0-indexed, hi exclusive). A wavelet tree descends the bit partition of S answering rank queries level by level. Report the count as one integer.

**Answer:**
3

### Example 2
**Prompt:**
Given the symbol sequence S = [2, 3, 0, 2, 3, 2, 0, 0, 2, 1, 1, 3, 0, 1, 3, 1, 0, 2, 1, 2, 3, 3, 2, 2, 3, 0, 3, 0], find the k = 1-th smallest value (1-indexed) among the elements in positions lo = 9 to hi = 12 (0-indexed, hi exclusive). A wavelet tree answers range-quantile queries on the bit partition. Report that value as one integer.

**Answer:**
1

## Level 5
### Example 1
**Prompt:**
Given the symbol sequence S = [5, 3, 5, 1, 0, 1, 1, 2, 1, 3, 5, 2, 4, 2, 4, 6, 2, 3, 6, 0, 6, 4, 3, 5, 2, 4, 4, 3, 4, 3, 3, 4, 1, 4, 4, 6, 0, 3, 1, 0, 2, 1, 3, 2, 6, 2], find the k = 21-th smallest value (1-indexed) among the elements in positions lo = 18 to hi = 41 (0-indexed, hi exclusive). A wavelet tree answers range-quantile queries on the bit partition. Report that value as one integer.

**Answer:**
6

### Example 2
**Prompt:**
Given the symbol sequence S = [4, 4, 1, 4, 3, 1, 6, 2, 3, 1, 0, 2, 5, 6, 3, 3, 2, 2, 3, 2, 1, 4, 3, 2, 5, 1, 1, 6, 6, 3, 1, 1, 3, 3, 2, 2, 3, 2, 2, 1, 2, 0, 2, 3, 2, 0], count how many occurrences of symbol 0 appear in positions lo = 29 to hi = 46 (0-indexed, hi exclusive). A wavelet tree descends the bit partition of S answering rank queries level by level. Report the count as one integer.

**Answer:**
2

