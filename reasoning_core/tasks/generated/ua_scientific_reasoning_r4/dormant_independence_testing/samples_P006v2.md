## Level 0
### Example 1
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 15  Y=1: 30
  X=0 M=1 -> Y=0: 11  Y=1: 32
  X=1 M=0 -> Y=0: 38  Y=1: 45
  X=1 M=1 -> Y=0: 66  Y=1: 83
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
31/44 != 12887451/21765920
```

### Example 2
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 44  Y=1: 31
  X=0 M=1 -> Y=0: 67  Y=1: 59
  X=1 M=0 -> Y=0: 64  Y=1: 16
  X=1 M=1 -> Y=0: 35  Y=1: 4
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
20/119 != 888793/2665600
```

## Level 2
### Example 1
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 27  Y=1: 31
  X=0 M=1 -> Y=0: 41  Y=1: 70
  X=0 M=2 -> Y=0: 36  Y=1: 71
  X=1 M=0 -> Y=0: 42  Y=1: 9
  X=1 M=1 -> Y=0: 40  Y=1: 7
  X=1 M=2 -> Y=0: 22  Y=1: 4
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
5/31 != 263440323/569462560
```

### Example 2
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 19  Y=1: 68
  X=0 M=1 -> Y=0: 9  Y=1: 9
  X=0 M=2 -> Y=0: 10  Y=1: 17
  X=1 M=0 -> Y=0: 49  Y=1: 80
  X=1 M=1 -> Y=0: 12  Y=1: 19
  X=1 M=2 -> Y=0: 39  Y=1: 69
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
47/66 != 45918091/70382400
```

## Level 5
### Example 1
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 43  Y=1: 66
  X=0 M=1 -> Y=0: 5  Y=1: 9
  X=0 M=2 -> Y=0: 31  Y=1: 52
  X=0 M=3 -> Y=0: 31  Y=1: 61
  X=1 M=0 -> Y=0: 32  Y=1: 34
  X=1 M=1 -> Y=0: 10  Y=1: 17
  X=1 M=2 -> Y=0: 29  Y=1: 39
  X=1 M=3 -> Y=0: 23  Y=1: 38
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
64/111 != 68211824217/112097396320
```

### Example 2
**Prompt**
```
A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), but a hidden confounder makes the raw observational link between X and Y misleading. The cohort counts by (X, M, Y) are:
  X=0 M=0 -> Y=0: 40  Y=1: 92
  X=0 M=1 -> Y=0: 11  Y=1: 33
  X=0 M=2 -> Y=0: 10  Y=1: 23
  X=0 M=3 -> Y=0: 7  Y=1: 26
  X=1 M=0 -> Y=0: 47  Y=1: 110
  X=1 M=1 -> Y=0: 18  Y=1: 24
  X=1 M=2 -> Y=0: 9  Y=1: 40
  X=1 M=3 -> Y=0: 9  Y=1: 21
Name the standard algorithm: apply the front-door adjustment to estimate the causal probability P(Y=1 | do(X)) by marginalizing over the kernel, and compare it with the naive conditional probability P(Y=1 | X) that an ordinary conditional-independence shortcut would read off. Give the violated polynomial equality -- the reduced-fraction forms of the two values, separated by ` != ` -- for the X level where they diverge most; write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each side, do not guess.
```
**Answer**
```
87/121 != 310234447/440039600
```

