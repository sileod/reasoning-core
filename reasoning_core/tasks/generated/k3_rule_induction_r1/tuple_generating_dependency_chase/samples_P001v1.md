# Level 0

## Example 1

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 2. Its facts are:
R(1, 1)
R(1, 4)
R(4, 1)
R(4, 2)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x1, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1) -> R(x0, fresh0_1)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(1, 0), (1, 1), (1, 3), (1, 4), (4, 1), (4, 2), (4, 5), (4, 6)]
```

## Example 2

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 2. Its facts are:
R(0, 7)
R(2, 3)
R(3, 1)
R(5, 7)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x1, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1) -> R(fresh0_0, fresh0_1)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(0, 7), (2, 3), (3, 1), (4, 6), (5, 7), (8, 9), (10, 11), (12, 13)]
```


# Level 2

## Example 1

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 2. Its facts are:
R(0, 6)
R(0, 13)
R(5, 10)
R(11, 0)
R(11, 10)
R(12, 0)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x1, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1) -> R(x0, fresh0_1)
TGD 1: R(x0, x1) -> R(fresh1_0, x1)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(0, 1), (0, 2), (0, 6), (0, 13), (5, 3), (5, 10), (9, 6), (11, 0), (11, 4), (11, 7), (11, 10), (12, 0), (12, 8), (14, 13), (15, 10), (16, 0), (17, 10), (18, 0)]
```

## Example 2

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 2. Its facts are:
R(1, 1)
R(1, 3)
R(5, 9)
R(7, 3)
R(7, 4)
R(10, 3)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x1, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1) -> R(fresh0_0, x1)
TGD 1: R(x0, x1) -> R(fresh1_0, x1)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(0, 1), (1, 1), (1, 3), (2, 3), (5, 9), (6, 9), (7, 3), (7, 4), (8, 3), (10, 3), (11, 4), (12, 3), (13, 1), (14, 3), (15, 9), (16, 3), (17, 4), (18, 3)]
```


# Level 5

## Example 1

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 3. Its facts are:
R(0, 14, 20)
R(1, 7, 7)
R(5, 0, 12)
R(8, 15, 1)
R(8, 20, 12)
R(14, 19, 15)
R(15, 0, 22)
R(16, 18, 9)
R(19, 21, 9)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x2, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1, x2) -> R(x0, x1, fresh0_2)
TGD 1: R(x0, x1, x2) -> R(fresh1_0, x1, x2)
TGD 2: R(x0, x1, x2) -> R(fresh2_0, x1, fresh2_2)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(0, 14, 2), (0, 14, 20), (1, 7, 3), (1, 7, 7), (5, 0, 4), (5, 0, 12), (8, 15, 1), (8, 15, 6), (8, 20, 10), (8, 20, 12), (14, 19, 11), (14, 19, 15), (15, 0, 13), (15, 0, 22), (16, 18, 9), (16, 18, 17), (19, 21, 9), (19, 21, 23), (24, 14, 20), (25, 7, 7), (26, 0, 12), (27, 15, 1), (28, 20, 12), (29, 19, 15), (30, 0, 22), (31, 18, 9), (32, 21, 9), (33, 14, 34), (35, 7, 36), (37, 0, 38), (39, 15, 40), (41, 20, 42), (43, 19, 44), (45, 0, 46), (47, 18, 48), (49, 21, 50)]
```

## Example 2

**Prompt:**

```
We have a finite relational instance over a single relation R of arity 3. Its facts are:
R(2, 5, 14)
R(11, 22, 15)
R(12, 11, 22)
R(13, 21, 18)
R(18, 6, 2)
R(19, 11, 7)
R(22, 9, 20)
R(22, 19, 3)
R(22, 22, 20)

A tuple-generating dependency (TGD) is a rule: whenever a tuple satisfying the body is present, the head tuple must be derived too. The head mentions the same variables x0..x2, each position being either a universal copy of a body position (value carried over verbatim) or an existential fresh witness: a brand-new constant not equal to any constant already in the instance or previously introduced, never reused.

The dependencies are:
TGD 0: R(x0, x1, x2) -> R(fresh0_0, fresh0_1, fresh0_2)
TGD 1: R(x0, x1, x2) -> R(x0, x1, fresh1_2)
TGD 2: R(x0, x1, x2) -> R(x0, x1, fresh2_2)
where each x with an index is the universal copy of the body value in that position, and each fresh name labels an existential witness.

Application rule (no recursion): go through the TGDs in the order listed above; for each one, apply it exactly once to each original fact tuple, in the order the facts are listed. Universal heads copy fact values verbatim. For each existential head position, introduce a fresh witness: the smallest non-negative integer not yet appearing among the original facts and not yet used as a fresh witness anywhere, assigned in increasing order as existential positions are filled while walking the TGDs and facts. Do not apply any TGD to tuples you derive yourself. If a head atom duplicates one already derived, keep only one copy.

Give the complete final derived atom set (facts plus everything the chase derives) as a canonical Python list of tuples sorted lexicographically, e.g. [(0, 0, 0), (1, 4, 2), ...], integers inside each tuple, constants in ascending order.
```

**Answer:**

```
[(0, 1, 4), (2, 5, 14), (2, 5, 43), (2, 5, 52), (8, 10, 16), (11, 22, 15), (11, 22, 44), (11, 22, 53), (12, 11, 22), (12, 11, 45), (12, 11, 54), (13, 21, 18), (13, 21, 46), (13, 21, 55), (17, 23, 24), (18, 6, 2), (18, 6, 47), (18, 6, 56), (19, 11, 7), (19, 11, 48), (19, 11, 57), (22, 9, 20), (22, 9, 49), (22, 9, 58), (22, 19, 3), (22, 19, 50), (22, 19, 59), (22, 22, 20), (22, 22, 51), (22, 22, 60), (25, 26, 27), (28, 29, 30), (31, 32, 33), (34, 35, 36), (37, 38, 39), (40, 41, 42)]
```

