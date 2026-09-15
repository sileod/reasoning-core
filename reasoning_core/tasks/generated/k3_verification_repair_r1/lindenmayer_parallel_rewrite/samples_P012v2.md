# Level 0

## Example 1

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> C with probability 0.16666666666666666, B with probability 0.4166666666666667, A with probability 0.4166666666666667
B -> C with probability 0.5, A with probability 0.5
C -> A with probability 0.6, C with probability 0.4
Start with the string "AABC". After exactly 2 step(s), what is the expected number of occurrences of the symbol A in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 2

## Example 2

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> B with probability 0.125, A with probability 0.25, C with probability 0.625
B -> A with probability 0.8333333333333334, C with probability 0.16666666666666666
C -> C with probability 0.375, A with probability 0.25, B with probability 0.375
Start with the string "AABB". After exactly 2 step(s), what is the expected number of occurrences of the symbol C in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 2

# Level 2

## Example 1

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> A with probability 0.38461538461538464, B with probability 0.38461538461538464, C with probability 0.23076923076923078
B -> C with probability 0.6, A with probability 0.4
C -> B with probability 0.75, C with probability 0.25
Start with the string "ABC". After exactly 4 step(s), what is the expected number of occurrences of the symbol C in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 1

## Example 2

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> B with probability 0.6, A with probability 0.4
B -> A with probability 0.4444444444444444, C with probability 0.4444444444444444, B with probability 0.1111111111111111
C -> A with probability 0.125, B with probability 0.625, C with probability 0.25
Start with the string "AAC". After exactly 4 step(s), what is the expected number of occurrences of the symbol B in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 1

# Level 5

## Example 1

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> A with probability 0.6, B with probability 0.4
B -> C with probability 0.7142857142857143, A with probability 0.2857142857142857
C -> B with probability 0.6, A with probability 0.2, C with probability 0.2
Start with the string "ACC". After exactly 7 step(s), what is the expected number of occurrences of the symbol B in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 1

## Example 2

In an L-system, in a single step every symbol is replaced simultaneously according to independent probabilistic productions:
A -> C with probability 0.5714285714285714, A with probability 0.2857142857142857, B with probability 0.14285714285714285
B -> A with probability 0.2857142857142857, C with probability 0.35714285714285715, B with probability 0.35714285714285715
C -> B with probability 0.2222222222222222, C with probability 0.2222222222222222, A with probability 0.5555555555555556
Start with the string "BBCC". After exactly 7 step(s), what is the expected number of occurrences of the symbol B in the string? Give the expected count as a non-negative integer (round to the nearest integer).

Answer: 1
