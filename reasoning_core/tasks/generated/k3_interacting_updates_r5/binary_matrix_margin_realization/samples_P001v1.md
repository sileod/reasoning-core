# samples_P001v1

## Level 0

### Example 1

**Prompt:**

```
Consider an 3-by-3 binary matrix, where every entry is either 0 or 1.
Its row sums are: 3 3 3
Its column sums are: 3 3 3
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
1 1 1
1 1 1
1 1 1
```

### Example 2

**Prompt:**

```
Consider an 3-by-3 binary matrix, where every entry is either 0 or 1.
Its row sums are: 0 0 2
Its column sums are: 0 1 1
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
0 0 0
0 0 0
0 1 1
```

## Level 2

### Example 1

**Prompt:**

```
Consider an 5-by-5 binary matrix, where every entry is either 0 or 1.
Its row sums are: 5 4 3 5 5
Its column sums are: 5 4 3 5 5
The following cells are fixed in advance: row 0 column 0 = 1, row 0 column 3 = 1, row 3 column 2 = 1.
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
1 1 1 1 1
1 1 0 1 1
1 0 0 1 1
1 1 1 1 1
1 1 1 1 1
```

### Example 2

**Prompt:**

```
Consider an 5-by-5 binary matrix, where every entry is either 0 or 1.
Its row sums are: 4 5 5 5 5
Its column sums are: 5 5 5 5 4
The following cells are fixed in advance: row 3 column 2 = 1, row 3 column 4 = 1.
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
1 1 1 1 0
1 1 1 1 1
1 1 1 1 1
1 1 1 1 1
1 1 1 1 1
```

## Level 5

### Example 1

**Prompt:**

```
Consider an 7-by-7 binary matrix, where every entry is either 0 or 1.
Its row sums are: 4 6 7 7 6 7 7
Its column sums are: 4 7 6 7 7 6 7
The following cells are fixed in advance: row 5 column 0 = 1.
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
0 1 0 1 1 0 1
0 1 1 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 1 1 1
0 1 1 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 1 1 1
```

### Example 2

**Prompt:**

```
Consider an 7-by-7 binary matrix, where every entry is either 0 or 1.
Its row sums are: 7 7 7 5 7 7 7
Its column sums are: 6 7 6 7 7 7 7
The following cells are fixed in advance: row 0 column 3 = 1, row 2 column 0 = 1, row 6 column 2 = 1.
Find a binary matrix satisfying these row and column sums (and the fixed cells, if any). Fill each row by placing its ones into the columns with the largest remaining demand. If exactly one such matrix exists, answer the matrix with one row per line and entries separated by spaces. If more than one distinct matrix satisfies the constraints, write exactly 'non-unique'.
```

**Answer:**

```
1 1 1 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 1 1 1
0 1 0 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 1 1 1
```
