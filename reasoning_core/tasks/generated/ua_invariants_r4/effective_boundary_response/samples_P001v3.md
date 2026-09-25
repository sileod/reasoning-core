## Level 0

### Example 1 (mode C)

**Prompt:**

A resistive network has terminals 0 and 1 and hidden interior nodes. One edge (2,3) has unknown conductance e, all other conductances in siemens are: ((1,3):2), ((2,0):1), ((2,3):e). Eliminating all hidden nodes preserves terminal current-voltage behavior, whose effective conductance between terminals 0 and 1 must equal 1/2. The unknown conductance is uniquely determined by this boundary response. Give the value of e. Answer with one rational number in lowest terms, e.g. 3/7.

**Answer:**

`2`

### Example 2 (mode B)

**Prompt:**

Two resistive networks share terminals 0 and 1 with hidden interior nodes. Network one conductances: ((1,0):1), ((2,1):1), ((3,2):2). Network two conductances: ((1,0):1), ((2,1):1), ((3,2):2). Two networks are exterior-equivalent if their terminal current-voltage behavior is identical, i.e. the effective conductance between terminals 0 and 1 is the same after eliminating all hidden nodes. Are they exterior-equivalent? Answer yes or no.

**Answer:**

`yes`

## Level 2

### Example 1 (mode C)

**Prompt:**

A resistive network has terminals 0 and 1 and hidden interior nodes. One edge (5,7) has unknown conductance e, all other conductances in siemens are: ((0,5):7), ((1,6):1), ((1,7):3), ((2,0):7), ((3,2):7), ((4,3):6), ((5,0):5), ((5,7):e), ((7,6):5). Eliminating all hidden nodes preserves terminal current-voltage behavior, whose effective conductance between terminals 0 and 1 must equal 1932/941. The unknown conductance is uniquely determined by this boundary response. Give the value of e. Answer with one rational number in lowest terms, e.g. 3/7.

**Answer:**

`7`

### Example 2 (mode A)

**Prompt:**

A resistive network has terminals 0 and 1 and hidden interior nodes. Edge conductances in siemens are: ((0,4):7), ((1,0):5), ((1,5):1), ((2,0):4), ((3,1):5), ((4,1):1), ((5,3):6), ((6,2):4), ((7,4):6). Current-voltage behavior at the terminals is fully given by the effective conductance between terminals 0 and 1. Eliminate every hidden node (Kron reduction, Schur complement) while preserving terminal behavior and give the resulting effective conductance between terminals 0 and 1. Answer with one rational number in lowest terms, e.g. 3/7.

**Answer:**

`47/8`

## Level 5

### Example 1 (mode B)

**Prompt:**

Two resistive networks share terminals 0 and 1 with hidden interior nodes. Network one conductances: ((0,2):8), ((1,0):12), ((1,9):13), ((2,1):8), ((3,1):8), ((3,5):2), ((4,1):9), ((5,2):12), ((5,13):6), ((6,2):3), ((6,9):7), ((7,0):12), ((8,7):5), ((9,0):7), ((10,9):12), ((10,12):5), ((11,10):5), ((12,11):2), ((13,3):7). Network two conductances: ((0,2):8), ((1,0):12), ((1,9):13), ((2,1):8), ((3,1):8), ((3,5):2), ((4,1):9), ((5,2):12), ((5,13):6), ((6,2):3), ((6,9):7), ((7,0):12), ((8,7):5), ((9,0):7), ((10,9):12), ((10,12):5), ((11,10):5), ((12,11):2), ((13,3):7). Two networks are exterior-equivalent if their terminal current-voltage behavior is identical, i.e. the effective conductance between terminals 0 and 1 is the same after eliminating all hidden nodes. Are they exterior-equivalent? Answer yes or no.

**Answer:**

`yes`

### Example 2 (mode C)

**Prompt:**

A resistive network has terminals 0 and 1 and hidden interior nodes. One edge (10,13) has unknown conductance e, all other conductances in siemens are: ((1,11):12), ((1,12):9), ((1,13):8), ((2,0):5), ((3,2):12), ((4,2):4), ((4,7):10), ((5,2):5), ((6,4):11), ((7,5):3), ((7,9):4), ((8,7):2), ((9,2):2), ((10,7):12), ((10,13):e), ((12,11):6), ((13,11):12). Eliminating all hidden nodes preserves terminal current-voltage behavior, whose effective conductance between terminals 0 and 1 must equal 519690/441311. The unknown conductance is uniquely determined by this boundary response. Give the value of e. Answer with one rational number in lowest terms, e.g. 3/7.

**Answer:**

`3`
