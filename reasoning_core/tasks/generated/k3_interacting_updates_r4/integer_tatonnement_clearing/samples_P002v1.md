## Level 0

**Prompt:**

```
good 0: demand = 2 - 7*p_0
good 1: demand = 4 - 6*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
initial prices: 2 1
Within the first 1 steps (counting the initial prices as step 0), decide whether the price adjustment ever returns the goods to an earlier price vector. Give the single word yes or no as your answer.
```

**Answer:**

```
no
```

**Prompt:**

```
good 0: demand = 5 - 4*p_0
good 1: demand = 2 - 2*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
initial prices: 2 3
Within the first 1 steps (counting the initial prices as step 0), decide whether the price adjustment ever returns the goods to an earlier price vector. Give the single word yes or no as your answer.
```

**Answer:**

```
no
```

## Level 2

**Prompt:**

```
good 0: demand = 1 - 6*p_0
good 1: demand = 4 - 4*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
good 2: demand = 2 - 5*p_2
initial prices: 4 1 2
After the adjustment at step 3, what is the price of each good? Answer 3 integers giving good 0..2 in order, separated by spaces.
```

**Answer:**

```
1 1 1
```

**Prompt:**

```
good 0: demand = 6 - 3*p_0
good 1: demand = 5 - 6*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
good 2: demand = 4 - 6*p_2
initial prices: 2 3 5
After the adjustment at step 1, what is the price of each good? Answer 3 integers giving good 0..2 in order, separated by spaces.
```

**Answer:**

```
2 2 4
```

## Level 5

**Prompt:**

```
good 0: demand = 3 - 8*p_0
good 1: demand = 8 - 6*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
good 2: demand = 7 - 1*p_2
good 3: demand = 7 - 1*p_3
good 4: demand = 6 - 4*p_4
initial prices: 9 3 3 4 6
After the adjustment at step 6, what is the price of each good? Answer 5 integers giving good 0..4 in order, separated by spaces.
```

**Answer:**

```
3 1 7 7 2
```

**Prompt:**

```
good 0: demand = 1 - 7*p_0
good 1: demand = 4 - 8*p_1
At each step, for every good simultaneously, compare its own demand to zero: if demand > 0 the price rises by 1; if demand < 0 it falls by 1; if demand == 0 the price stays (that market has cleared). Prices never drop below 1. Price changes are integer and unit-sized.
good 2: demand = 3 - 1*p_2
good 3: demand = 8 - 2*p_3
good 4: demand = 2 - 7*p_4
initial prices: 9 7 3 3 7
After the adjustment at step 1, what is the price of each good? Answer 5 integers giving good 0..4 in order, separated by spaces.
```

**Answer:**

```
8 6 3 4 6
```
