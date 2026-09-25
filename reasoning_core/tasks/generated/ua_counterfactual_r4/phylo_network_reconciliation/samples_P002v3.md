# phylogenetic_network_reconciliation samples

## Level 0

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: ((((3,4),1),(2,5)),0);
Tree 2: ((((3,5),2),(1,4)),0);

**Answer:**

1

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: (((((3,5),0),1),2),4);
Tree 2: ((((0,5),1),(2,3)),4);

**Answer:**

1

## Level 2

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: ((((0,3),(4,5)),(2,6)),(1,7));
Tree 2: ((((0,3),(4,5)),6),((2,7),1));

**Answer:**

1

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: ((((((2,3),1),6),0),5),(4,7));
Tree 2: (((((1,3),6),(0,4)),(2,5)),7);

**Answer:**

2

## Level 5

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: ((((((1,3),5),7),(0,8)),(2,4)),(6,9));
Tree 2: (((((((0,1),3),(2,5)),(6,7)),8),4),9);

**Answer:**

3

**Prompt:**

Two rooted trees on the same set of leaves are given in parenthesized form (leaves are integers; a node's children are the strings inside its parentheses). A phylogenetic network can display both trees by letting some node inherit two parents (a reticulation / reticulate node) and by suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of any network that displays both trees, as a single non-negative integer (answer format e.g. '4').
Tree 1: ((((0,1),(4,9)),(2,8)),(((5,6),7),3));
Tree 2: (((((0,4),(5,9)),1),8),(((2,7),6),3));

**Answer:**

3

