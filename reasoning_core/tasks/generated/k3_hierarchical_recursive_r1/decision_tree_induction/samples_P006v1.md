# P006v1 Samples


## Level 0

### Example 1

**Prompt:**

```
Attributes: A, B, C.
Class labels: p0, p1.
Row 0: A=0, B=0, C=1; label=p1.
Row 1: A=1, B=0, C=0; label=p1.
Row 2: A=0, B=0, C=1; label=p0.
Row 3: A=1, B=0, C=0; label=p1.
Row 4: A=0, B=1, C=1; label=p0.
Row 5: A=1, B=1, C=0; label=p0.
Row 6: A=0, B=1, C=0; label=p1.
Row 7: A=1, B=0, C=0; label=p0.
Row 8: A=0, B=0, C=0; label=p1.
Row 9: A=1, B=1, C=0; label=p0.
Build a decision tree by recursive maximum-information-gain splitting of these 10 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(B: (A: p0, (C: p0, p1)), (C: p1, (A: p1, p1)))
```

### Example 2

**Prompt:**

```
Attributes: A, B, C.
Class labels: p0, p1.
Row 0: A=0, B=1, C=0; label=p1.
Row 1: A=1, B=1, C=1; label=p0.
Row 2: A=0, B=1, C=1; label=p0.
Row 3: A=1, B=1, C=1; label=p1.
Row 4: A=1, B=1, C=0; label=p0.
Row 5: A=0, B=1, C=0; label=p0.
Row 6: A=1, B=0, C=0; label=p0.
Row 7: A=0, B=1, C=1; label=p0.
Row 8: A=1, B=1, C=1; label=p0.
Row 9: A=0, B=0, C=0; label=p0.
Build a decision tree by recursive maximum-information-gain splitting of these 10 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(B: (C: (A: p0, p0), (A: p0, p1)), p0)
```

## Level 2

### Example 1

**Prompt:**

```
Attributes: A, B, C, D.
Class labels: p0, p1, p2.
Row 0: A=0, B=1, C=1, D=1; label=p2.
Row 1: A=0, B=1, C=1, D=1; label=p1.
Row 2: A=0, B=1, C=1, D=0; label=p1.
Row 3: A=1, B=0, C=1, D=0; label=p1.
Row 4: A=0, B=1, C=0, D=1; label=p0.
Row 5: A=0, B=1, C=1, D=0; label=p2.
Row 6: A=0, B=0, C=1, D=0; label=p0.
Row 7: A=1, B=1, C=1, D=0; label=p2.
Row 8: A=1, B=1, C=0, D=1; label=p2.
Row 9: A=0, B=1, C=1, D=1; label=p2.
Row 10: A=1, B=1, C=1, D=0; label=p0.
Row 11: A=1, B=0, C=1, D=0; label=p0.
Row 12: A=0, B=1, C=0, D=1; label=p0.
Row 13: A=1, B=1, C=0, D=0; label=p0.
Row 14: A=0, B=0, C=0, D=0; label=p0.
Row 15: A=0, B=1, C=0, D=0; label=p2.
Row 16: A=0, B=1, C=0, D=0; label=p1.
Row 17: A=0, B=0, C=0, D=0; label=p2.
Build a decision tree by recursive maximum-information-gain splitting of these 18 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(B: (A: (D: p2, p0), (C: p2, p0)), (A: p1, (C: p0, p0)))
```

### Example 2

**Prompt:**

```
Attributes: A, B, C, D.
Class labels: p0, p1, p2.
Row 0: A=0, B=0, C=0, D=1; label=p1.
Row 1: A=1, B=1, C=1, D=1; label=p1.
Row 2: A=0, B=0, C=0, D=1; label=p1.
Row 3: A=1, B=1, C=1, D=1; label=p2.
Row 4: A=1, B=0, C=1, D=1; label=p0.
Row 5: A=0, B=1, C=0, D=1; label=p1.
Row 6: A=0, B=0, C=1, D=1; label=p0.
Row 7: A=0, B=1, C=0, D=1; label=p1.
Row 8: A=1, B=0, C=1, D=1; label=p2.
Row 9: A=0, B=1, C=0, D=0; label=p2.
Row 10: A=1, B=1, C=1, D=1; label=p0.
Row 11: A=1, B=1, C=1, D=0; label=p0.
Row 12: A=1, B=1, C=0, D=1; label=p1.
Row 13: A=1, B=0, C=1, D=0; label=p2.
Row 14: A=0, B=1, C=1, D=0; label=p1.
Row 15: A=1, B=0, C=0, D=1; label=p2.
Row 16: A=1, B=1, C=0, D=0; label=p1.
Row 17: A=1, B=0, C=1, D=0; label=p2.
Build a decision tree by recursive maximum-information-gain splitting of these 18 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(C: (B: (A: p0, p1), (D: p0, p2)), (D: (A: p1, p1), (A: p1, p2)))
```

## Level 5

### Example 1

**Prompt:**

```
Attributes: A, B, C, D, E.
Class labels: p0, p1, p2.
Row 0: A=1, B=0, C=1, D=1, E=0; label=p2.
Row 1: A=1, B=1, C=0, D=0, E=0; label=p2.
Row 2: A=0, B=0, C=0, D=0, E=0; label=p0.
Row 3: A=1, B=1, C=0, D=0, E=0; label=p2.
Row 4: A=0, B=1, C=1, D=1, E=1; label=p2.
Row 5: A=1, B=1, C=0, D=1, E=0; label=p1.
Row 6: A=0, B=1, C=0, D=0, E=0; label=p1.
Row 7: A=1, B=0, C=1, D=0, E=0; label=p2.
Row 8: A=1, B=1, C=0, D=1, E=1; label=p0.
Row 9: A=1, B=0, C=0, D=0, E=0; label=p2.
Row 10: A=1, B=0, C=1, D=1, E=1; label=p1.
Row 11: A=1, B=0, C=1, D=0, E=1; label=p0.
Row 12: A=0, B=1, C=0, D=1, E=0; label=p2.
Row 13: A=1, B=1, C=1, D=1, E=1; label=p2.
Row 14: A=1, B=1, C=0, D=1, E=1; label=p2.
Row 15: A=1, B=0, C=0, D=1, E=0; label=p2.
Row 16: A=0, B=0, C=1, D=1, E=0; label=p1.
Row 17: A=0, B=0, C=1, D=1, E=0; label=p0.
Row 18: A=0, B=0, C=0, D=1, E=1; label=p1.
Row 19: A=0, B=1, C=1, D=0, E=1; label=p0.
Row 20: A=1, B=0, C=1, D=0, E=0; label=p2.
Row 21: A=0, B=1, C=0, D=1, E=1; label=p0.
Row 22: A=0, B=1, C=0, D=0, E=0; label=p1.
Row 23: A=1, B=1, C=1, D=0, E=1; label=p0.
Row 24: A=1, B=0, C=0, D=0, E=1; label=p0.
Row 25: A=1, B=0, C=0, D=1, E=0; label=p2.
Row 26: A=0, B=1, C=0, D=1, E=0; label=p1.
Row 27: A=1, B=0, C=1, D=0, E=0; label=p1.
Row 28: A=0, B=0, C=0, D=0, E=0; label=p1.
Row 29: A=1, B=1, C=0, D=0, E=0; label=p0.
Build a decision tree by recursive maximum-information-gain splitting of these 30 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(A: (E: (D: p2, p0), (B: p2, p2)), (B: (E: p0, p1), (E: p1, p0)))
```

### Example 2

**Prompt:**

```
Attributes: A, B, C, D, E.
Class labels: p0, p1, p2.
Row 0: A=0, B=1, C=1, D=1, E=0; label=p2.
Row 1: A=0, B=1, C=1, D=1, E=1; label=p1.
Row 2: A=0, B=0, C=0, D=1, E=0; label=p0.
Row 3: A=0, B=0, C=1, D=0, E=1; label=p0.
Row 4: A=1, B=1, C=0, D=1, E=1; label=p0.
Row 5: A=1, B=0, C=1, D=0, E=1; label=p2.
Row 6: A=1, B=1, C=1, D=1, E=1; label=p1.
Row 7: A=0, B=1, C=0, D=1, E=0; label=p1.
Row 8: A=1, B=1, C=1, D=0, E=0; label=p1.
Row 9: A=1, B=0, C=0, D=0, E=0; label=p0.
Row 10: A=1, B=1, C=0, D=1, E=1; label=p0.
Row 11: A=0, B=0, C=1, D=1, E=1; label=p0.
Row 12: A=0, B=1, C=0, D=1, E=0; label=p0.
Row 13: A=0, B=0, C=1, D=0, E=1; label=p0.
Row 14: A=0, B=1, C=1, D=0, E=1; label=p2.
Row 15: A=1, B=1, C=1, D=1, E=1; label=p1.
Row 16: A=0, B=1, C=0, D=1, E=1; label=p0.
Row 17: A=1, B=1, C=0, D=1, E=0; label=p2.
Row 18: A=0, B=0, C=1, D=1, E=0; label=p2.
Row 19: A=0, B=0, C=0, D=0, E=1; label=p0.
Row 20: A=1, B=1, C=0, D=1, E=1; label=p0.
Row 21: A=0, B=1, C=0, D=1, E=0; label=p2.
Row 22: A=1, B=0, C=1, D=0, E=1; label=p0.
Row 23: A=1, B=1, C=1, D=1, E=0; label=p0.
Row 24: A=1, B=0, C=0, D=1, E=0; label=p1.
Row 25: A=0, B=1, C=0, D=0, E=0; label=p0.
Row 26: A=0, B=1, C=1, D=0, E=0; label=p1.
Row 27: A=1, B=1, C=0, D=1, E=1; label=p1.
Row 28: A=0, B=1, C=0, D=0, E=1; label=p2.
Row 29: A=1, B=0, C=0, D=1, E=0; label=p0.
Build a decision tree by recursive maximum-information-gain splitting of these 30 rows. At every node choose the available attribute with the largest information gain; break ties by picking the alphabetically first attribute, then the larger split value. Stop when all remaining rows share one class or no useful split exists; a region with mixed labels is labeled by its majority class. Represent the tree in balanced parentheses: a node is written (Attr: left, right), as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, and each branch may itself be a further node or a single class label such as p0 or p1. What is the tree?
```

**Answer:**

```
(B: (C: (A: p1, p2), (D: p0, p0)), (C: (E: p0, p2), (A: p0, p0)))
```
