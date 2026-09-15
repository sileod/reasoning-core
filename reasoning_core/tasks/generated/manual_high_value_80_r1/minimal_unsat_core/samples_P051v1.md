# minimal_unsat_core samples (P051v1)


## Level 0


**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x2.
C1: (not x1)
C2: (x1)
C3: (not x1 or not x2)
C4: (not x0 or not x2)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

1 2



**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x2.
C1: (not x0 or x2)
C2: (x0)
C3: (x1 or not x2)
C4: (not x0)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

2 4



## Level 2


**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x3.
C1: (not x0)
C2: (x1 or not x2 or x3)
C3: (x0 or not x1)
C4: (x0)
C5: (x3)
C6: (x0 or x1 or x3)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

1 4



**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x3.
C1: (not x0)
C2: (x3)
C3: (not x1)
C4: (x0 or x1)
C5: (not x0 or x2)
C6: (not x2)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

1 3 4



## Level 5


**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x4.
C1: (not x0 or not x2 or not x3 or not x4)
C2: (not x2 or x3 or x4)
C3: (not x1 or not x4)
C4: (not x0 or not x1)
C5: (x0 or not x1)
C6: (not x1)
C7: (x0 or x3)
C8: (x2)
C9: (not x2)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

8 9



**Prompt:**

Consider the following Boolean constraints over boolean variables x0..x4.
C1: (not x3)
C2: (not x1 or x2 or not x3)
C3: (x0 or x2)
C4: (not x0 or x2 or x3 or not x4)
C5: (not x3)
C6: (not x1)
C7: (not x0 or x1)
C8: (not x0 or x3)
C9: (x0 or x1)
Together these constraints are unsatisfiable. A subset-minimal inconsistent subset is a set of these constraints that is itself unsatisfiable but becomes satisfiable if any one of its members is removed. Give the lexicographically smallest such subset-minimal inconsistent subset, as a space-separated list of ascending constraint indices (C1 => 1, C2 => 2, ...). For example the answer format is '1 3 4'.

**Answer:**

1 6 8 9

