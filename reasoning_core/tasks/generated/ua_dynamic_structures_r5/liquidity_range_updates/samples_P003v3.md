## Level 0

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 20 (integer).

Positions:
  id 0: lo=1, hi=40, L=3
  id 1: lo=31, hi=37, L=1

Operations, in order:
  1. swap 8 units of token1 in (s goes up)
  2. swap 3 units of token1 in (s goes up)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 24

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 28 (integer).

Positions:
  id 0: lo=1, hi=40, L=2
  id 1: lo=19, hi=30, L=1

Operations, in order:
  1. remove the position with id 1
  2. swap 8 units of token1 in (s goes up)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 32

## Level 2

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 37 (integer).

Positions:
  id 0: lo=1, hi=80, L=4
  id 1: lo=37, hi=46, L=1
  id 2: lo=33, hi=75, L=1
  id 3: lo=38, hi=59, L=5

Operations, in order:
  1. swap 11 units of token1 in (s goes up)
  2. remove the position with id 3
  3. swap 9 units of token1 in (s goes up)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 40

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 42 (integer).

Positions:
  id 0: lo=1, hi=80, L=3
  id 1: lo=8, hi=35, L=6
  id 2: lo=50, hi=67, L=5
  id 3: lo=7, hi=24, L=4
  id 4: lo=70, hi=73, L=5

Operations, in order:
  1. add a position lo=38, hi=79, L=5
  2. swap 1 units of token0 in (s goes down)
  3. swap 1 units of token0 in (s goes down)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 24

## Level 5

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 57 (integer).

Positions:
  id 0: lo=1, hi=140, L=5
  id 1: lo=49, hi=108, L=2

Operations, in order:
  1. add a position lo=99, hi=116, L=4
  2. swap 10 units of token1 in (s goes up)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 58

### Prompt
```
A concentrated-liquidity (Uniswap v3 style) pool holds several positions, each with a liquidity L active only while the current sqrt price s lies in its range [lo, hi]. Within each interval between range boundaries the pool behaves as one constant-product AMM with total liquidity equal to the sum of the in-range positions. The price only changes through swaps.

Swap law: swapping a units of token0 in moves s down to the s' satisfying a = L*(1/s' - 1/s); swapping a units of token1 in moves s up to the s' satisfying a = L*(s' - s). All intermediate values are exact rationals and a single trade may cross several range boundaries, re-activating or de-activating positions at each one. Liquidity additions and removals change the positions but do not themselves move the price.

Initial sqrt price s = 82 (integer).

Positions:
  id 0: lo=1, hi=140, L=5
  id 1: lo=11, hi=78, L=5
  id 2: lo=130, hi=135, L=6
  id 3: lo=5, hi=57, L=8
  id 4: lo=94, hi=104, L=2

Operations, in order:
  1. add a position lo=99, hi=131, L=3
  2. swap 1 units of token0 in (s goes down)

After all operations, compute the final sqrt price s and report it rounded to the nearest integer (a value at the midpoint rounds up). The answer is one integer.
```

Answer: 57

