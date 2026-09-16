# CayleyTableEvaluation samples (P001v2)

## Level 0

### Example 1

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3
0   2 2 0 2
1   1 1 2 0
2   3 0 0 0
3   1 0 2 1
Evaluate the nested term ⊙(0 ⊙ 1). The answer is the single resulting element.
```

**Answer:** `2`

### Example 2

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3
0   0 2 2 3
1   2 3 3 3
2   2 2 3 3
3   0 2 3 2
Evaluate the nested term ⊙(0 ⊙ (2 ⊙ 3)). The answer is the single resulting element.
```

**Answer:** `3`

## Level 2

### Example 1

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3
0   3 1 2 1
1   2 3 0 1
2   1 1 0 3
3   1 3 1 3
Consider the equation with the unknown element x in [0, 1, 2, 3]:
(((2 ⊙ x) ⊙ 0) ⊙ (x ⊙ 3)) = 3
Try x = 0, 1, ..., n-1, traversing every carrier element, and keep the values that make the equation true. Exactly one such value exists. The answer is that single element.
```

**Answer:** `2`

### Example 2

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3, 4] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3 4
0   2 0 1 1 0
1   2 2 0 2 0
2   3 0 0 3 0
3   2 3 4 1 1
4   0 0 1 3 3
Consider the equation with the unknown element x in [0, 1, 2, 3, 4]:
((x ⊙ x) ⊙ 1) = 2
Try x = 0, 1, ..., n-1, traversing every carrier element, and keep the values that make the equation true. Exactly one such value exists. The answer is that single element.
```

**Answer:** `3`

## Level 5

### Example 1

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3, 4, 5] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3 4 5
0   3 0 2 1 2 3
1   2 3 1 0 1 3
2   5 3 5 3 5 2
3   2 4 4 4 2 0
4   2 1 0 5 0 5
5   5 0 2 3 2 1
Consider the equation with the unknown element x in [0, 1, 2, 3, 4, 5]:
((x ⊙ ((x ⊙ x) ⊙ 3)) ⊙ 0) = 3
Try x = 0, 1, ..., n-1, traversing every carrier element, and keep the values that make the equation true. Exactly one such value exists. The answer is that single element.
```

**Answer:** `3`

### Example 2

**Prompt:**

```
A binary operation ⊙ on the carrier set [0, 1, 2, 3, 4, 5, 6, 7] is defined by the table below (row = left operand, column = right operand).
    0 1 2 3 4 5 6 7
0   2 0 5 2 4 5 1 1
1   5 0 7 2 6 6 5 4
2   2 6 4 1 3 2 5 3
3   1 6 0 6 0 5 4 1
4   6 2 3 7 1 2 5 4
5   1 4 4 7 5 4 4 0
6   7 0 0 5 7 7 1 1
7   3 3 4 1 6 7 1 4
Evaluate the nested term ⊙(((1 ⊙ 1) ⊙ (5 ⊙ 5)) ⊙ 4). The answer is the single resulting element.
```

**Answer:** `1`

