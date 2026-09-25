# P002v1 samples

## Level 0

### Example 1

**Prompt:**
```
2 players A and B divide a total surplus of 4. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 0, cap 2
B: guarantee 1, cap 2

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{A, B}: 5

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Does a stable allocation exist? Reply only with a single word: yes or no.
Does a stable allocation exist?
```

**Answer:**
```
no
```

### Example 2

**Prompt:**
```
2 players A and B divide a total surplus of 1. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 0, cap 1
B: guarantee 0, cap 1

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{B}: 0

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Give the tight range of integer values A can receive in some stable allocation. Answer as a single bracket pair [lo, hi] with the two integers.
```

**Answer:**
```
[0, 1]
```

## Level 2

### Example 1

**Prompt:**
```
4 players A, B, C and D divide a total surplus of 12. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 0, cap 1
B: guarantee 2, cap 4
C: guarantee 2, cap 7
D: guarantee 3, cap 7

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{A, C}: 0
{B, D}: 1
{B, C, D}: 4

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Give the tight range of integer values A can receive in some stable allocation. Answer as a single bracket pair [lo, hi] with the two integers.
```

**Answer:**
```
[0, 1]
```

### Example 2

**Prompt:**
```
4 players A, B, C and D divide a total surplus of 13. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 0, cap 5
B: guarantee 0, cap 7
C: guarantee 2, cap 5
D: guarantee 1, cap 8

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{A, B}: 3
{D}: 4
{C}: 0

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Does a stable allocation exist? Reply only with a single word: yes or no.
Does a stable allocation exist?
```

**Answer:**
```
yes
```

## Level 5

### Example 1

**Prompt:**
```
6 players A, B, C, D, E and F divide a total surplus of 38. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 6, cap 13
B: guarantee 0, cap 3
C: guarantee 3, cap 6
D: guarantee 3, cap 14
E: guarantee 4, cap 11
F: guarantee 4, cap 7

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{A, B, E}: 21
{B, C}: 7
{A, E, F}: 25
{D, F}: 13
{B, D}: 20
{A, D, E}: 24

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Does a stable allocation exist? Reply only with a single word: yes or no.
Does a stable allocation exist?
```

**Answer:**
```
no
```

### Example 2

**Prompt:**
```
6 players A, B, C, D, E and F divide a total surplus of 47. Every player must receive at least its individual guarantee and at most its payoff cap:
A: guarantee 3, cap 11
B: guarantee 6, cap 19
C: guarantee 1, cap 14
D: guarantee 0, cap 12
E: guarantee 5, cap 18
F: guarantee 5, cap 8

The following coalitions each block any allocation whose combined payoff for their members is below the threshold shown:
{A, B, F}: 23
{B, C}: 3
{A, C}: 5
{A, C, E}: 21
{B, C}: 9
{B, E, F}: 4

A stable allocation satisfies every guarantee, every cap, the total {T} (all players receive exactly {T} together), and every coalition threshold.
Give the tight range of integer values A can receive in some stable allocation. Answer as a single bracket pair [lo, hi] with the two integers.
```

**Answer:**
```
[3, 11]
```
