# samples_P008v3

## Level 0

### Example 1

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a2', ')a1'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause ['!)a0', ')a2']
  leaf 1 : clause ['!)a2', ')a1']
  leaf 2 : clause ['!)a2', ')a0']
  node 3 combines parents [0, 1], shared=[')a2'], private a=[')a0'], private b=[')a1']
  node 4 combines parents [2, 3], shared=[')a0', ')a2'], private a=[], private b=[')a1']

Give the interpolant of the queried node (node 4) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a2'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
1001
```

### Example 2

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a2', ')a1'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause ['!)a0', '!)a2']
  leaf 1 : clause [')a0', ')a1']
  leaf 2 : clause ['!)a2', ')a0']
  node 3 combines parents [0, 1], shared=[')a0'], private a=[')a2'], private b=[')a1']
  node 4 combines parents [2, 3], shared=[')a0', ')a2'], private a=[], private b=[')a1']

Give the interpolant of the queried node (node 4) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a2'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
1010
```

## Level 2

### Example 1

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a2', ')a3', ')a1'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause ['!)a0', '!)a3']
  leaf 1 : clause ['!)a0', ')a2']
  leaf 2 : clause [')a0', ')a2', ')a3']
  leaf 3 : clause ['!)a0', '!)a1', '!)a3']
  leaf 4 : clause ['!)a2', ')a0']
  node 5 combines parents [2, 4], shared=[')a0', ')a2'], private a=[')a3'], private b=[]
  node 6 combines parents [0, 5], shared=[')a0', ')a3'], private a=[], private b=[')a2']
  node 7 combines parents [3, 6], shared=[')a0', ')a3'], private a=[')a1'], private b=[')a2']
  node 8 combines parents [1, 7], shared=[')a0', ')a2'], private a=[], private b=[')a1', ')a3']

Give the interpolant of the queried node (node 8) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a2', ')a3'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
01000010
```

### Example 2

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a1', ')a3', ')a2'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause [')a0', ')a1']
  leaf 1 : clause ['!)a3', ')a0']
  leaf 2 : clause ['!)a1', ')a0']
  leaf 3 : clause [')a2', ')a3']
  leaf 4 : clause ['!)a1', ')a3']
  node 5 combines parents [0, 2], shared=[')a0', ')a1'], private a=[], private b=[]
  node 6 combines parents [1, 4], shared=[')a3'], private a=[')a0'], private b=[')a1']
  node 7 combines parents [3, 6], shared=[')a3'], private a=[')a2'], private b=[')a0', ')a1']
  node 8 combines parents [5, 7], shared=[')a0', ')a1'], private a=[], private b=[')a2', ')a3']

Give the interpolant of the queried node (node 8) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a1', ')a3'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
00001101
```

## Level 5

### Example 1

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a2', ')a3', ')a4', ')a1'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause ['!)a2', '!)a3', '!)a4']
  leaf 1 : clause ['!)a0', ')a4']
  leaf 2 : clause ['!)a0', ')a1', ')a2']
  leaf 3 : clause ['!)a3', ')a2', ')a4']
  leaf 4 : clause ['!)a0', '!)a2', '!)a4', ')a3']
  leaf 5 : clause [')a0', ')a4']
  node 6 combines parents [2, 3], shared=[')a2'], private a=[')a0', ')a1'], private b=[')a3', ')a4']
  node 7 combines parents [4, 5], shared=[')a0', ')a4'], private a=[')a2', ')a3'], private b=[]
  node 8 combines parents [1, 7], shared=[')a0', ')a4'], private a=[], private b=[')a2', ')a3']
  node 9 combines parents [0, 8], shared=[')a2', ')a3', ')a4'], private a=[], private b=[')a0']
  node 10 combines parents [6, 9], shared=[')a0', ')a2', ')a3', ')a4'], private a=[')a1'], private b=[]

Give the interpolant of the queried node (node 10) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a2', ')a3', ')a4'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
0101010001010000
```

### Example 2

Prompt:
```
A propositional formula is developed as a binary resolution tree over a
set of atoms. The leaves are clauses; each combined node merges its parents
over the atoms shared between them (public/shared atoms). Atoms occurring in
exactly one parent of a combined node are that parent's private atoms; atoms
shared between the two parents are the node's shared atoms. The conjunction
of all clauses beneath a node is its formula.

Interpolant extraction rule (recursive):
  (leaf)   interpolant over a leaf's public atoms = the truth value of its
           clause over its own atoms, existential over its private atoms.
  (combine)interpolant = the existential projection over the circle of shared
           atoms between the two parents, of the conjunction of the two
           parents' interpolants.
Effectively, each non-(root) node existentially quantifies over exactly the
atoms private to one side, so any atom can be forced by an assignment of the
other side's private atoms.

The queried node's interpolant is reported over its shared atoms only; an
assignment of those atoms satisfies the interpolant iff there EXISTS a setting
of all private atoms for which every clause in the subtree holds.

The full atom set is [')a0', ')a1', ')a2', ')a3', ')a4'].
Derivation nodes (id, kind, parents, shared, private-a, private-b):
  leaf 0 : clause ['!)a0', '!)a1', '!)a2', '!)a3']
  leaf 1 : clause ['!)a2', ')a0', ')a3']
  leaf 2 : clause ['!)a3', ')a1']
  leaf 3 : clause ['!)a0', '!)a3', ')a1']
  leaf 4 : clause [')a2', ')a3']
  leaf 5 : clause ['!)a1', '!)a2', '!)a3', ')a4']
  node 6 combines parents [1, 3], shared=[')a0', ')a3'], private a=[')a2'], private b=[')a1']
  node 7 combines parents [0, 6], shared=[')a0', ')a1', ')a2', ')a3'], private a=[], private b=[]
  node 8 combines parents [4, 5], shared=[')a2', ')a3'], private a=[], private b=[')a1', ')a4']
  node 9 combines parents [2, 7], shared=[')a1', ')a3'], private a=[], private b=[')a0', ')a2']
  node 10 combines parents [8, 9], shared=[')a1', ')a2', ')a3'], private a=[')a4'], private b=[')a0']

Give the interpolant of the queried node (node 10) as a truth table over its
shared atoms. Order the shared atoms as listed: [')a0', ')a1', ')a2', ')a3'].
Enumerate assignments in lexicographic order with False before True (0 before 1).
For each assignment write '1' if the interpolant is TRUE, else '0'.
Output the string of 0s and 1s concatenated, no separators.
```

Answer:
```
0000010100100110
```
