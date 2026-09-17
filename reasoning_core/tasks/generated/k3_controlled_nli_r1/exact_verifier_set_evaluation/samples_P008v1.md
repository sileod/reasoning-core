# P008v1 exact verifier-set evaluation samples

## Level 0

### Example 1

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    h o r v
h   h o r v
o   o o v v
r   r v r v
v   v v v v
Subject-matter map:
p0 -> {h, o, v}
p1 -> {o, v}
p2 -> {o}
Formula: (p0 ∧ (p1 ∨ p1))
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
o, v
```

### Example 2

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    d i n u
d   d n n d
i   n i n i
n   n n n n
u   d i n u
Subject-matter map:
p0 -> {d, u}
p1 -> {n}
p2 -> {d, n, u}
Formula: ((p0 ∧ p1) ∨ p0)
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
d, n, u
```

## Level 2

### Example 1

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    c o r x
c   c o r x
o   o o o o
r   r o r o
x   x o o x
Subject-matter map:
p0 -> {c, o, x}
p1 -> {c, o, x}
p2 -> {c, x}
p3 -> {c}
Formula: ((p1 ∨ (p1 ∧ p2)) ∧ p2)
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
c, o, x
```

### Example 2

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    k n o s
k   k k k k
n   k n o s
o   k o o k
s   k s k s
Subject-matter map:
p0 -> {k, o}
p1 -> {o}
p2 -> {k, o, s}
p3 -> {k, o, s}
Formula: (p2 ∧ (p1 ∨ ((p0 ∨ p1) ∧ p1)))
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
k, o
```

## Level 5

### Example 1

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    a f l t u v w x
a   a f l t u v w x
f   f f w x v v w x
l   l w l u u v w v
t   t x u t u v v x
u   u v u u u v v v
v   v v v v v v v v
w   w w w v v v w v
x   x x v x v v v x
Subject-matter map:
p0 -> {l, u}
p1 -> {a, f}
p2 -> {t}
p3 -> {w, x}
p4 -> {t, x}
Formula: (((p0 ∧ ((p2 ∨ (p4 ∧ p3)) ∧ (p0 ∧ p2))) ∧ (p3 ∧ p1)) ∧ p2)
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
v
```

### Example 2

Prompt:
```
Evaluate exact verification in this finite state space. The subject-matter map lists exactly the states relevant to each atom; these are its exact verifiers.
Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. Use only these clauses; add no other states. Repeated results count once.
Fusion table (left state's row, right state's column; headers list all states):
    a c j m n p t
a   a c j m m a c
c   c c c c c c c
j   j c j c c j c
m   m c c m m m c
n   m c c m n n t
p   a c j m n p t
t   c c c c t t t
Subject-matter map:
p0 -> {a, j, m}
p1 -> {m}
p2 -> {a, c, t}
p3 -> {a, m}
p4 -> {j, m, n}
Formula: ((p4 ∧ (p0 ∧ p1)) ∧ ((((p1 ∧ p4) ∧ p1) ∨ (p3 ∨ (p2 ∧ p2))) ∨ (((p2 ∨ p2) ∨ p2) ∧ p3)))
Return the verifier states in lexicographic order, separated by commas and single spaces. Format example: a, c, d. For an empty set write none.
```

Answer:
```
c, m
```
