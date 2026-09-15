# Termination Ranking Function - samples P031v1

## Level 0

### Example 1

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2:

while ( -7 x1 +5 x2 >= 0 ) {
    x1 := - 1x1;
    x2 := - 4x1 - 4x2;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2, with integer coefficients a1..a2, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a2] as a comma-separated sequence of integers in the order of x1, x2, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
1,0
```

### Example 2

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2:

while ( -2 x1 +5 x2 >= 0 ) {
    x1 := - 1x1 - 2x2;
    x2 := - 4x1 - 4x2;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2, with integer coefficients a1..a2, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a2] as a comma-separated sequence of integers in the order of x1, x2, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
1,0
```

## Level 2

### Example 1

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2, x3:

while ( +2 x1 +5 x2 -4 x3 >= 0 ) {
    x1 := - 4x1 - 4x2 + 3x3;
    x2 := - 1x1 - 1x2 + 2x3;
    x3 := 4x1 - 2x2 - 3x3;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2 + a3*x3, with integer coefficients a1..a3, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a3] as a comma-separated sequence of integers in the order of x1, x2, x3, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
0,1,0
```

### Example 2

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2, x3:

while ( -6 x1 +6 x2 +5 x3 >= 0 ) {
    x1 := - 2x1 - 4x2 + 1x3;
    x2 := - 1x1 - 4x2 - 2x3;
    x3 := - 3x1 - 3x2 - 1x3;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2 + a3*x3, with integer coefficients a1..a3, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a3] as a comma-separated sequence of integers in the order of x1, x2, x3, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
1,0,0
```

## Level 5

### Example 1

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2, x3, x4:

while ( +6 x1 +5 x2 +4 x3 -1 x4 >= 0 ) {
    x1 := - 4x1 - 3x2 - 4x4;
    x2 := 1x1 - 3x2 - 4x3 + 4x4;
    x3 := 1x1 - 4x2 - 1x3 - 2x4;
    x4 := - 1x1 - 4x2 - 1x4;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2 + a3*x3 + a4*x4, with integer coefficients a1..a4, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a4] as a comma-separated sequence of integers in the order of x1, x2, x3, x4, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
0,1,0,0
```

### Example 2

**Prompt:**

```
A program computes the following single loop over integer variables x1, x2, x3, x4:

while ( -4 x1 -1 x2 +2 x3 +8 x4 >= 0 ) {
    x1 := 2x1 + 1x2 + 1x3 - 4x4;
    x2 := - 1x2 + 4x3 - 4x4;
    x3 := 1x1 - 1x3 - 1x4;
    x4 := - 3x1 - 3x3;
}

Each update uses linear integer arithmetic on the current values. The loop always terminates if there exists a linear ranking function r = a1*x1 + a2*x2 + a3*x3 + a4*x4, with integer coefficients a1..a4, such that whenever the guard holds, r strictly decreases by at least 1 on every iteration.
Find such a ranking function and report its coefficient list [a1, a2, ..., a4] as a comma-separated sequence of integers in the order of x1, x2, x3, x4, choosing coefficients with absolute value at most 5. Give only the coefficient list, nothing else.
```

**Answer:**

```
1,0,0,2
```
