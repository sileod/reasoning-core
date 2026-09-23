## Level 0

### Example 1

**Prompt:**

A directed graph has nodes 0..4. A directed edge u->v makes u an in-neighbor of v.
Edges: 0->1, 0->4, 1->0, 1->3, 1->4, 2->0, 2->4, 3->2, 3->4, 4->1, 4->2, 4->3
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=1, t(1)=2, t(2)=2, t(3)=1, t(4)=1
Initially active (round 1): 4
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
In which round does node 2 first become active? Answer with a single integer only.

**Answer:**

3

### Example 2

**Prompt:**

A directed graph has nodes 0..4. A directed edge u->v makes u an in-neighbor of v.
Edges: 0->1, 0->2, 0->4, 1->0, 1->4, 2->0, 2->3, 2->4, 3->1, 3->2, 3->4, 4->0
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=2, t(1)=1, t(2)=1, t(3)=1, t(4)=1
Initially active (round 1): 0
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
Answer with the final active set as a comma-separated list of node labels in ascending order, nothing else.

**Answer:**

0,1,2,3,4

## Level 2

### Example 1

**Prompt:**

A directed graph has nodes 0..7. A directed edge u->v makes u an in-neighbor of v.
Edges: 1->0, 1->2, 1->4, 1->6, 2->0, 2->4, 2->6, 3->0, 3->1, 3->2, 3->4, 3->5, 3->6, 3->7, 4->0, 4->6, 5->0, 5->1, 5->2, 5->4, 5->6, 6->0, 7->0, 7->1, 7->2, 7->4, 7->5, 7->6
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=8, t(1)=1, t(2)=1, t(3)=1, t(4)=1, t(5)=1, t(6)=1, t(7)=1
Initially active (round 1): 3
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
Does the process saturate and activate every node? Reply with the single word yes or no and no extra text.

**Answer:**

no

### Example 2

**Prompt:**

A directed graph has nodes 0..7. A directed edge u->v makes u an in-neighbor of v.
Edges: 0->2, 1->7, 2->3, 3->0, 3->6, 4->7, 5->3, 6->3, 6->4, 6->5, 7->0, 7->4
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=3, t(1)=4, t(2)=1, t(3)=4, t(4)=4, t(5)=3, t(6)=4, t(7)=4
Initially active (round 1): 2
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
Answer with the final active set as a comma-separated list of node labels in ascending order, nothing else.

**Answer:**

2

## Level 5

### Example 1

**Prompt:**

A directed graph has nodes 0..11. A directed edge u->v makes u an in-neighbor of v.
Edges: 0->7, 1->6, 1->8, 10->3, 10->6, 10->9, 11->7, 11->8, 2->10, 3->1, 3->4, 3->6, 4->10, 4->3, 5->8, 5->9, 6->4, 6->8, 6->9, 7->3, 8->2, 9->5, 9->6
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=6, t(1)=4, t(2)=6, t(3)=3, t(4)=6, t(5)=5, t(6)=2, t(7)=4, t(8)=4, t(9)=2, t(10)=6, t(11)=1
Initially active (round 1): 5, 7
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
Answer with the final active set as a comma-separated list of node labels in ascending order, nothing else.

**Answer:**

5,7

### Example 2

**Prompt:**

A directed graph has nodes 0..11. A directed edge u->v makes u an in-neighbor of v.
Edges: 1->0, 1->10, 1->11, 1->3, 1->7, 1->8, 10->0, 10->11, 10->3, 11->0, 2->0, 2->1, 2->10, 2->11, 2->3, 2->7, 2->8, 3->0, 3->11, 4->0, 4->1, 4->10, 4->11, 4->2, 4->3, 4->7, 4->8, 5->0, 5->1, 5->10, 5->11, 5->2, 5->3, 5->4, 5->7, 5->8, 6->0, 6->1, 6->10, 6->11, 6->2, 6->3, 6->4, 6->5, 6->7, 6->8, 7->0, 7->10, 7->11, 7->3, 7->8, 8->0, 8->10, 8->11, 8->3, 9->0, 9->1, 9->10, 9->11, 9->2, 9->3, 9->4, 9->5, 9->6, 9->7, 9->8
Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).
Thresholds: t(0)=12, t(1)=1, t(2)=1, t(3)=1, t(4)=1, t(5)=1, t(6)=1, t(7)=1, t(8)=1, t(9)=1, t(10)=1, t(11)=1
Initially active (round 1): 9
Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.
Does the process saturate and activate every node? Reply with the single word yes or no and no extra text.

**Answer:**

no

