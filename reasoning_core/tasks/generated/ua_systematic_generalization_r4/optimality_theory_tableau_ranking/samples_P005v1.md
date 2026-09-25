# Samples P005v1: optimality_theory_tableau_ranking

## Level 0

### Example 1

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C2  C0  C1

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C2 in that order.

  A: -  -  *
  B: -  -  *
  C: *  -  -

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

Give a different permutation of the constraint order (highest priority first) whose optimal winner differs from the winner under the ranking shown above. Answer with the reranking as a comma-separated list of constraint indices from 0..2. Example: '1,0,2'.
```

**Answer:**

1,0,2

### Example 2

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C2  C0  C1

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C2 in that order.

  A: *  -  *
  B: *  -  *
  C: -  *  -

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

Give a different permutation of the constraint order (highest priority first) whose optimal winner differs from the winner under the ranking shown above. Answer with the reranking as a comma-separated list of constraint indices from 0..2. Example: '1,0,2'.
```

**Answer:**

1,2,0

## Level 2

### Example 1

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C1  C0  C2  C3

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C3 in that order.

  A: *  -  *  *
  B: -  *  *  -
  C: -  -  *  *
  D: -  *  *  -

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

All candidates except the optimal one(s) are eliminated. List the eliminated candidate labels as a comma-separated, alphabetically sorted string, chosen from A/B/C/D. Example: if A is eliminated but B is not, answer 'A'.
```

**Answer:**

A,B,D

### Example 2

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C3  C2  C1  C0

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C3 in that order.

  A: -  *  -  *
  B: *  -  *  -
  C: -  -  *  *
  D: -  -  -  *

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

Which candidate is the sole optimal winner? Answer with the single candidate label, chosen from A/B/C/D.
```

**Answer:**

B

## Level 5

### Example 1

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C1  C2  C3  C4  C0

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C4 in that order.

  A: **  **  **  **  -
  B: **  **  *  **  -
  C: -  *  **  *  -
  D: *  **  -  *  *
  E: -  *  *  *  *
  F: **  **  -  **  *

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

Which candidate is the sole optimal winner? Answer with the single candidate label, chosen from A/B/C/D/E/F.
```

**Answer:**

E

### Example 2

**Prompt:**

```
Optimality-theoretic tableau. The constraint ranking, highest priority first, is:
  C4  C1  C0  C3  C2

Candidates: each '*' below a column counts as one violation of that constraint ('-' means zero violations). Columns are the constraints C0..C4 in that order.

  A: **  *  **  **  *
  B: *  -  *  **  *
  C: -  -  **  *  **
  D: **  **  *  -  -
  E: **  **  **  -  **
  F: **  -  *  **  **

A candidate is optimal if no other candidate has fewer violations on the highest-ranked constraint. Ties there are broken by the next constraint down the ranking, and a candidate that ties on every constraint ties overall.

All candidates except the optimal one(s) are eliminated. List the eliminated candidate labels as a comma-separated, alphabetically sorted string, chosen from A/B/C/D/E/F. Example: if A is eliminated but B is not, answer 'A'.
```

**Answer:**

A,B,C,E,F
