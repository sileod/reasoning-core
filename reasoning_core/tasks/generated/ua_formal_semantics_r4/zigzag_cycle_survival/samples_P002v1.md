# Level 0

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v2, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0 + 1*v1
e1: d(e1) = 1*v0 + 1*v1
e2: d(e2) = 1*v1

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2
S1: e1, e2
S2: e1
S3: (none)

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,1)
```

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v2, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0
e1: d(e1) = 1*v0
e2: d(e2) = 1*v1 + 1*v2
e3: d(e3) = 1*v0 + 1*v1
e4: d(e4) = 1*v0
e5: d(e5) = 1*v0

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2
S1: e0, e1, e2, e3
S2: e0, e2, e3
S3: e0, e2, e3, e5

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,2),(3,inf)
```

# Level 2

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v4, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0 + 1*v3
e1: d(e1) = 1*v1 + 1*v2
e2: d(e2) = 1*v1 + 1*v3
e3: d(e3) = 1*v0 + 1*v1 + 1*v2
e4: d(e4) = 1*v0 + 1*v3
e5: d(e5) = 1*v0 + 1*v3
e6: d(e6) = 1*v2 + 1*v3
e7: d(e7) = 1*v2 + 1*v4
e8: d(e8) = 1*v0 + 1*v3

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2, e3, e4
S1: e0, e1, e2, e4
S2: e0, e1, e4
S3: e0, e4
S4: e0, e4, e6
S5: e0, e4, e6, e7
S6: e0, e4, e6

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,inf)
```

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v4, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0 + 1*v1 + 1*v2 + 1*v4
e1: d(e1) = 1*v2
e2: d(e2) = 1*v3
e3: d(e3) = 1*v1 + 1*v2 + 1*v3
e4: d(e4) = 1*v0 + 1*v3 + 1*v4
e5: d(e5) = 1*v0 + 1*v2 + 1*v3 + 1*v4
e6: d(e6) = 1*v0 + 1*v3
e7: d(e7) = 1*v4

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2, e3, e4
S1: e0, e1, e3, e4
S2: e1, e3, e4
S3: e1, e3
S4: e3
S5: e3, e6
S6: e3, e6, e7

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,2)
```

# Level 5

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v7, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0 + 1*v1 + 1*v4 + 1*v6
e1: d(e1) = 1*v0 + 1*v2 + 1*v6
e2: d(e2) = 1*v1 + 1*v4 + 1*v6
e3: d(e3) = 1*v0 + 1*v2 + 1*v4 + 1*v5 + 1*v7
e4: d(e4) = 1*v0 + 1*v1 + 1*v6 + 1*v7
e5: d(e5) = 1*v0 + 1*v2 + 1*v3
e6: d(e6) = 1*v0 + 1*v2 + 1*v3
e7: d(e7) = 1*v0 + 1*v3 + 1*v5 + 1*v7
e8: d(e8) = 1*v2 + 1*v4 + 1*v7
e9: d(e9) = 1*v0 + 1*v2 + 1*v3 + 1*v5
e10: d(e10) = 1*v0 + 1*v3 + 1*v4 + 1*v5 + 1*v6
e11: d(e11) = 1*v0 + 1*v2 + 1*v4 + 1*v5 + 1*v6 + 1*v7
e12: d(e12) = 1*v5 + 1*v6 + 1*v7
e13: d(e13) = 1*v0 + 1*v2 + 1*v4 + 1*v6 + 1*v7
e14: d(e14) = 1*v1 + 1*v6
e15: d(e15) = 1*v0 + 1*v3
e16: d(e16) = 1*v2 + 1*v3
e17: d(e17) = 1*v1 + 1*v2 + 1*v3 + 1*v4 + 1*v6

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2, e3, e4, e5, e6, e7, e8
S1: e0, e1, e2, e3, e4, e5, e6, e7
S2: e0, e1, e3, e4, e5, e6, e7
S3: e0, e1, e3, e5, e6, e7
S4: e0, e3, e5, e6, e7
S5: e3, e5, e6, e7
S6: e3, e5, e7
S7: e3, e5, e7, e14
S8: e3, e5, e7, e14, e15
S9: e3, e5, e7, e14, e15, e16
S10: e3, e5, e7, e14, e15, e16, e17

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,6),(10,inf)
```

**Prompt:**
```
We track a zigzag filtration of chain complexes over the field F2 (all arithmetic below is mod 2). The complex has vertices v0, ..., v7, all present throughout. It evolves only by adding or removing 1-cells (edges); each edge carries an explicit boundary, a formal sum of vertices with coefficients in F2.

Edge boundaries (each is its row in the boundary matrix):
e0: d(e0) = 1*v0 + 1*v1 + 1*v2 + 1*v3 + 1*v5 + 1*v6 + 1*v7
e1: d(e1) = 1*v0 + 1*v1 + 1*v2 + 1*v3 + 1*v5 + 1*v6 + 1*v7
e2: d(e2) = 1*v1 + 1*v2 + 1*v3 + 1*v5 + 1*v6 + 1*v7
e3: d(e3) = 1*v0 + 1*v3
e4: d(e4) = 1*v0 + 1*v5 + 1*v6
e5: d(e5) = 1*v0 + 1*v2 + 1*v5 + 1*v6 + 1*v7
e6: d(e6) = 1*v2 + 1*v3 + 1*v6 + 1*v7
e7: d(e7) = 1*v0 + 1*v3 + 1*v5
e8: d(e8) = 1*v0 + 1*v1 + 1*v3 + 1*v4 + 1*v7
e9: d(e9) = 1*v0 + 1*v1 + 1*v4 + 1*v5
e10: d(e10) = 1*v0 + 1*v3 + 1*v4 + 1*v5 + 1*v6
e11: d(e11) = 1*v5
e12: d(e12) = 1*v2 + 1*v3 + 1*v7
e13: d(e13) = 1*v0 + 1*v1 + 1*v3 + 1*v4 + 1*v7
e14: d(e14) = 1*v7

Filtration (stage 0 onward; under each stage are its present edges):
S0: e0, e1, e2, e3, e4, e5, e6, e8, e9
S1: e0, e1, e2, e4, e5, e6, e8, e9
S2: e0, e2, e4, e5, e6, e8, e9
S3: e0, e2, e4, e5, e8, e9
S4: e0, e2, e4, e5, e9
S5: e0, e2, e4, e5, e9, e12
S6: e0, e2, e4, e5, e9, e12, e13
S7: e0, e2, e4, e5, e9, e12, e13, e14
S8: e0, e2, e4, e9, e12, e13, e14
S9: e0, e2, e9, e12, e13, e14
S10: e0, e2, e9, e13, e14

A homology class (cycle) in dimension 1 is a 1-chain whose boundary is zero, taken modulo boundaries of higher cells. Its dimension-1 Betti number at a stage equals (number of present edges) minus the rank of the boundary matrix over F2. Compute the dimension-1 zigzag persistence: each maximal consecutive run of stages with Betti number 1 is one interval, born at the first stage of the run and dead at the first following stage with Betti number 0; a run reaching the last stage is written with death 'inf'.

Give only the intervals as comma-separated pairs in order of birth, each pair as (birth,death), e.g. `(1,3),(5,7)`. Output nothing else.
```

**Answer:**
```
(0,2)
```
