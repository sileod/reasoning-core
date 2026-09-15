# d_separation samples

## Level 0

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 0->3, 1->4, 3->4. Are nodes 3 and 0 d-separated given the conditioning set {none}? Answer exactly 'yes' or 'no'.

**Answer:**

no

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 3->4. Are nodes 3 and 1 d-separated given the conditioning set {none}? Answer exactly 'yes' or 'no'.

**Answer:**

yes

## Level 2

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 1->2, 1->4, 1->5, 3->5, 4->6. Are nodes 3 and 2 d-separated given the conditioning set {none}? Answer exactly 'yes' or 'no'.

**Answer:**

yes

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 1->6. Are nodes 6 and 0 d-separated given the conditioning set {none}? Answer exactly 'yes' or 'no'.

**Answer:**

yes

## Level 5

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 2->7, 3->5, 3->9, 4->8, 4->9, 6->9, 8->9. Are nodes 6 and 3 d-separated given the conditioning set {1, 4}? Answer exactly 'yes' or 'no'.

**Answer:**

yes

**Prompt:**

Consider the following causal DAG (nodes are integers) with directed edges 0->2, 0->7, 0->8, 1->2, 2->4, 2->7, 2->8, 2->9, 3->4, 3->6, 4->7, 5->7, 6->9, 7->8, 8->9. Are nodes 6 and 5 d-separated given the conditioning set {1, 3, 4}? Answer exactly 'yes' or 'no'.

**Answer:**

yes

