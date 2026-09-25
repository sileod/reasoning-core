# Samples for uniform_test_dominance (P009v1)

## Level 0

**Prompt:**

```
A hypothesis test of a null against an alternative family of 2 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.072. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   | 0.011 | 0.715, 0.957
    1   | 0.121 | 0.648, 0.786
    2   | 0.051 | 0.608, 0.902
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [0]

---

**Prompt:**

```
A hypothesis test of a null against an alternative family of 2 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.111. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   | 0.018 | 0.356, 0.551
    1   |  0.06 | 0.375, 0.963
    2   | 0.022 | 0.686, 0.994
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [2]

---

## Level 2

**Prompt:**

```
A hypothesis test of a null against an alternative family of 3 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.061. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   |  0.03 | 0.341, 0.674, 0.816
    1   | 0.062 | 0.612, 0.826, 0.892
    2   | 0.136 | 0.357, 0.927, 0.934
    3   | 0.145 | 0.379, 0.381, 0.825
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [0]

---

**Prompt:**

```
A hypothesis test of a null against an alternative family of 3 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.079. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   | 0.106 | 0.313, 0.492, 0.774
    1   |  0.09 | 0.894, 0.897, 0.924
    2   | 0.034 | 0.415, 0.509, 0.839
    3   | 0.147 | 0.435, 0.566, 0.777
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [2]

---

## Level 5

**Prompt:**

```
A hypothesis test of a null against an alternative family of 4 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.119. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   |  0.04 | 0.452, 0.486, 0.514, 0.817
    1   | 0.043 | 0.462, 0.593, 0.872, 0.915
    2   | 0.063 | 0.478, 0.772, 0.862, 0.866
    3   | 0.072 | 0.755, 0.82, 0.833, 0.915
    4   | 0.133 | 0.505, 0.597, 0.716, 0.891
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [1, 2, 3]

---

**Prompt:**

```
A hypothesis test of a null against an alternative family of 4 parameter values uses candidate decision (possibly randomized) rules. Each rule's size is its chance of rejecting under the null, and its power is its chance of rejecting at each alternative (alternatives indexed 1..m, non-decreasing). Size-valid means size <= alpha = 0.093. Rule A strictly dominates rule B if every power of A is >= the corresponding power of B and at least one is >. A size-valid rule is non-dominated if no other size-valid rule strictly dominates it.
  rule | size | powers
    0   | 0.026 | 0.357, 0.619, 0.738, 0.818
    1   | 0.104 | 0.605, 0.618, 0.82, 0.93
    2   | 0.094 | 0.316, 0.894, 0.912, 0.962
    3   | 0.113 | 0.506, 0.649, 0.818, 0.968
    4   | 0.089 | 0.459, 0.482, 0.845, 0.925
List the IDs of the non-dominated size-valid rules as a sorted bracket list, e.g. [0, 2]. If every size-valid rule is dominated (no non-dominated ones exist), answer []. 
```

**Answer:** [0, 4]

---
