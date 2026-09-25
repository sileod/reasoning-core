# samples_P004v2

## Level 0

### Example 1

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=0, threshold=2, edges=[('n1', 2)]
  n1: initial_load=0, threshold=2, edges=[('n0', 2)]

Load increments applied in order:
  +1 to n1

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n1

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n0=1
```

### Example 2

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=0, threshold=2, edges=[('n1', 2)]
  n1: initial_load=1, threshold=2, edges=[('n0', 2)]

Load increments applied in order:
  +1 to n1

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n0

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n1=2
```

## Level 2

### Example 1

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=0, threshold=4, edges=[('n2', 5)]
  n1: initial_load=2, threshold=4, edges=[('n3', 2)]
  n2: initial_load=2, threshold=4, edges=[('n0', 6), ('n3', 5)]
  n3: initial_load=2, threshold=3, edges=[('n0', 6), ('n1', 5), ('n2', 5)]

Load increments applied in order:
  +2 to n2

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n2

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n0=2;n1=2;n3=3
```

### Example 2

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=1, threshold=3, edges=[('n3', 4)]
  n1: initial_load=2, threshold=3, edges=[('n3', 4)]
  n2: initial_load=1, threshold=3, edges=[('n0', 3), ('n1', 1), ('n3', 1)]
  n3: initial_load=2, threshold=2, edges=[('n0', 1), ('n1', 5)]

Load increments applied in order:
  +1 to n0
  +3 to n3

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n2

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n0=3
```

## Level 5

### Example 1

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=4, threshold=2, edges=[('n2', 4)]
  n1: initial_load=5, threshold=6, edges=[('n0', 6), ('n3', 8), ('n4', 5), ('n5', 1)]
  n2: initial_load=2, threshold=7, edges=[('n3', 11)]
  n3: initial_load=1, threshold=6, edges=[('n0', 10), ('n4', 1)]
  n4: initial_load=1, threshold=5, edges=[('n0', 8), ('n1', 11), ('n2', 4), ('n5', 6), ('n6', 7)]
  n5: initial_load=2, threshold=6, edges=[('n0', 4), ('n1', 7), ('n2', 7), ('n6', 9)]
  n6: initial_load=2, threshold=4, edges=[('n3', 3)]

Load increments applied in order:
  +4 to n4

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n0

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n1=5;n2=6;n3=1;n4=5;n5=2;n6=2
```

### Example 2

Prompt:

```
A load network has these nodes, each carrying its current load and its failure
threshold. A node breaks irreversibly the moment its load exceeds its threshold,
and its whole load is redistributed to its out-neighbors in proportion to the
stated directed edge weights (each out-neighbor gets weight/total_weight of the
load, rounded down; if a node has no surviving out-neighbor its load is lost).
Breaking can push other nodes over their threshold, triggering further breaks,
until no surviving node exceeds its threshold.

Nodes and directed edges (edge weight shown after 'w='):
  n0: initial_load=5, threshold=6, edges=[('n5', 11)]
  n1: initial_load=0, threshold=5, edges=[('n5', 5)]
  n2: initial_load=1, threshold=6, edges=[('n3', 6), ('n6', 11)]
  n3: initial_load=6, threshold=2, edges=[('n2', 5), ('n5', 12)]
  n4: initial_load=3, threshold=4, edges=[('n0', 4), ('n1', 3), ('n3', 1), ('n5', 3), ('n6', 4)]
  n5: initial_load=4, threshold=4, edges=[('n3', 4), ('n4', 1), ('n6', 9)]
  n6: initial_load=5, threshold=5, edges=[('n0', 3), ('n5', 7)]

Load increments applied in order:
  +2 to n1

Nodes removed in order (a removed node's load goes to its out-neighbors by the
same weighted rule; it can no longer break):
  remove n3

Report the surviving node labels and their final loads as 'label=load;label=load;...' with labels sorted in the order given above. Use only integer loads.
```

Answer:

```
n1=2;n2=2;n4=3
```
