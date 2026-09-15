# Samples: P005v1 simplex_pivot_execution

Two complete prompt/answer examples at levels 0, 2 and 5.

## Level 0

### Prompt

```
Consider the linear program in standard form
maximize  -4x1 + 2x2
subject to
  5x1 - 5x2 <= 4
  -2x1 + 3x2 <= 2
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-4/3`

### Prompt

```
Consider the linear program in standard form
maximize  3x1 - 3x2
subject to
  4x1 + 2x2 <= 1
  2x1 + 5x2 <= 2
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-3/4`

## Level 2

### Prompt

```
Consider the linear program in standard form
maximize  4x1 - 9x2 - 5x3 + 5x4
subject to
  4x1 - 6x2 + 3x3 - 2x4 <= 3
  4x1 - 4x2 + 7x3 + 4x4 <= 4
  4x1 + x2 - 2x3 <= 6
  -7x1 + 3x2 + 4x3 - 6x4 <= 4
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-5`

### Prompt

```
Consider the linear program in standard form
maximize  8x1 - 4x3 - 9x4
subject to
  -9x1 + 4x2 - 4x3 + 9x4 <= 6
  -6x2 + 8x3 - 3x4 <= 3
  6x1 + 5x2 + 2x3 - 2x4 <= 11
  -7x1 + 8x2 - 4x3 + 9x4 <= 2
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-44/3`

## Level 5

### Prompt

```
Consider the linear program in standard form
maximize  -13x1 - 14x2 - 12x3 + 6x5 - 9x6 - 4x7
subject to
  13x1 + 8x2 - 13x3 + 12x4 - 6x5 - 14x6 - 15x7 <= 4
  -7x1 - 13x2 - 7x3 + 2x4 - 2x5 + 2x6 + x7 <= 3
  -9x1 - 14x2 + 15x3 + 3x4 + 11x5 - 10x6 - 3x7 <= 7
  2x1 - 7x2 - 8x3 + 9x4 + 5x5 - 5x6 + 8x7 <= 9
  -3x1 + 9x2 + 11x3 + 14x4 + 15x5 - 15x6 + 7x7 <= 16
  -5x1 - 12x2 + x3 - 12x4 - 13x5 - 12x6 - 10x7 <= 4
  -15x1 + 13x2 - 12x3 + 13x4 - 11x5 + 10x6 + 11x7 <= 19
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-42/11`

### Prompt

```
Consider the linear program in standard form
maximize  x1 + 14x2 - 9x3 + x4 - x5 - 11x7
subject to
  -13x1 - 4x2 - 6x4 - 3x5 + 15x6 - 14x7 <= 15
  -13x1 + 7x2 - 3x3 + 10x4 - 3x5 + 5x6 + 3x7 <= 10
  -13x1 + 11x2 + 9x3 - 7x4 + 9x5 + 2x6 + x7 <= 8
  4x1 + 5x2 + 9x3 - 3x4 + 13x5 + 13x6 - 11x7 <= 11
  x2 - 14x3 - 5x4 - 11x5 - x6 - 8x7 <= 15
  -14x1 + 5x2 + 2x3 - 8x4 - 6x5 + 10x6 + 10x7 <= 1
  15x1 - 4x2 + 8x3 + 10x4 - 10x5 + 15x6 + 13x7 <= 5
  x_i >= 0 for all i.

Bland's rule: at each step enter the smallest indexed variable with negative reduced cost; leave the row attaining the minimum ratio, tying by smallest row index.

Run primal simplex from the origin with exact rational arithmetic.
Give the optimal objective value V as a single rational number
(for example 3 or 5/2).

Answer format: the optimal value V only.
```

**Answer**:

`-283/12`
