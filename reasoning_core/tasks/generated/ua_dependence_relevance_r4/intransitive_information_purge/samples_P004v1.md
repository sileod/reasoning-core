# samples P004v1 — intransitive_information_purge

## Level 0

### Example 1

**Prompt:**

A system tracks information flow among agents A0, A1 and observer A2.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A0 -> A2
1: A0 -> A2
2: A1 -> A1
3: A1 -> A1

**Answer:** 0

### Example 2

**Prompt:**

A system tracks information flow among agents A0, A1 and observer A2.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A0 -> A2
1: A1 -> A2
2: A1 -> A2
3: A0 -> A2

**Answer:** 0,1

## Level 2

### Example 1

**Prompt:**

A system tracks information flow among agents A0, A1, A2, A3 and observer A4.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A0 -> A1
1: A3 -> A1
2: A2 -> A3
3: A3 -> A3
4: A1 -> A3
5: A3 -> A4
6: A2 -> A2
7: A0 -> A2

**Answer:** 0,1,3

### Example 2

**Prompt:**

A system tracks information flow among agents A0, A1, A2, A3 and observer A4.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A0 -> A2
1: A2 -> A2
2: A2 -> A4
3: A3 -> A3
4: A3 -> A3
5: A0 -> A3
6: A1 -> A3
7: A1 -> A2

**Answer:** 1

## Level 5

### Example 1

**Prompt:**

A system tracks information flow among agents A0, A1, A2, A3, A4, A5, A6 and observer A7.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A6 -> A4
1: A0 -> A7
2: A2 -> A1
3: A3 -> A1
4: A5 -> A7
5: A5 -> A1
6: A4 -> A1
7: A1 -> A2
8: A3 -> A5
9: A0 -> A4
10: A3 -> A7
11: A5 -> A1
12: A1 -> A1
13: A6 -> A7

**Answer:** 0,3,8

### Example 2

**Prompt:**

A system tracks information flow among agents A0, A1, A2, A3, A4, A5, A6 and observer A7.
Actions happen in order, one per line. Action k has a source and a listener: 'source -> listener'. The edge it permits is in force only after that action has happened, for every later action.
Permitted edges are directed and NOT transitive: an edge A->B and an edge B->C does not permit A->C unless a later action permits A->C directly.
Retain every action k whose source can reach the observer by repeatedly following the permitted edges of actions with index greater than k. Answer the retained action indices in increasing order as a comma-separated list, e.g. '1,3'.
0: A3 -> A2
1: A1 -> A2
2: A4 -> A7
3: A0 -> A5
4: A1 -> A3
5: A4 -> A7
6: A6 -> A3
7: A5 -> A4
8: A2 -> A1
9: A3 -> A3
10: A1 -> A5
11: A6 -> A3
12: A1 -> A1
13: A6 -> A2

**Answer:** 1,2,4

