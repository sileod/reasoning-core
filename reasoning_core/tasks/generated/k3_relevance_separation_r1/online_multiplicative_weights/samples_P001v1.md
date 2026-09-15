# Samples P001v1 — online_multiplicative_weights

## Level 0

### Example 1

**Prompt:**

```
There are 4 experts and 6 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  1, 0, 0, 0
  0, 0, 0, 1
  1, 0, 0, 0
  1, 0, 0, 0
  1, 0, 0, 0
  0, 0, 1, 0
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^6, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
4/64, 64/64, 32/64, 32/64
```

### Example 2

**Prompt:**

```
There are 4 experts and 6 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  0, 0, 1, 0
  1, 0, 0, 0
  0, 0, 1, 0
  0, 1, 0, 0
  0, 0, 1, 0
  0, 0, 1, 0
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^6, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
32/64, 32/64, 4/64, 64/64
```

## Level 2

### Example 1

**Prompt:**

```
There are 6 experts and 10 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  0, 1, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0
  0, 0, 0, 0, 1, 0
  0, 0, 0, 0, 0, 1
  0, 0, 1, 0, 0, 0
  0, 0, 0, 1, 0, 0
  0, 1, 0, 0, 0, 0
  0, 1, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0
  0, 0, 0, 0, 0, 1
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^10, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
256/1024, 128/1024, 512/1024, 512/1024, 512/1024, 256/1024
```

### Example 2

**Prompt:**

```
There are 6 experts and 10 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  0, 0, 0, 1, 0, 0
  1, 0, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0
  0, 0, 0, 0, 0, 1
  0, 0, 0, 1, 0, 0
  0, 0, 0, 0, 1, 0
  0, 0, 0, 0, 1, 0
  0, 0, 0, 1, 0, 0
  0, 0, 0, 0, 0, 1
  0, 0, 0, 0, 0, 1
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^10, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
256/1024, 1024/1024, 1024/1024, 128/1024, 256/1024, 128/1024
```

## Level 5

### Example 1

**Prompt:**

```
There are 7 experts and 14 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  1, 0, 0, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 1, 0, 0, 0
  0, 0, 1, 0, 0, 0, 0
  0, 0, 0, 0, 0, 1, 0
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 0, 0, 0, 1
  0, 0, 0, 0, 0, 1, 0
  0, 0, 0, 0, 0, 1, 0
  0, 0, 0, 0, 0, 1, 0
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 0, 0, 0, 1
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 1, 0, 0, 0
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^14, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
512/16384, 16384/16384, 8192/16384, 4096/16384, 16384/16384, 1024/16384, 4096/16384
```

### Example 2

**Prompt:**

```
There are 7 experts and 14 rounds of online prediction.
Each round, exactly one of the experts incurs loss 1 and all others incur loss 0.
The loss vectors (round by round, expert by expert) are:
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 0, 1, 0, 0
  0, 0, 1, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 1, 0, 0, 0
  0, 1, 0, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0, 0
  0, 1, 0, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0, 0
  1, 0, 0, 0, 0, 0, 0
  0, 0, 0, 0, 0, 1, 0
  0, 1, 0, 0, 0, 0, 0
  0, 0, 1, 0, 0, 0, 0
  0, 0, 0, 0, 1, 0, 0
Using the multiplicative weights algorithm with learning rate eta=0.5, starting from initial weights all 1, multiply each weight by (1-eta)^(its loss) each round.
Give the resulting final weight vector as a list of fractions 'a1/D, a2/D, ...' over one common denominator D=2^14, one fraction per expert in expert order, e.g. '1/4, 3/4'. The weights are not normalized.
```

**Answer:**

```
512/16384, 2048/16384, 4096/16384, 8192/16384, 4096/16384, 8192/16384, 16384/16384
```
