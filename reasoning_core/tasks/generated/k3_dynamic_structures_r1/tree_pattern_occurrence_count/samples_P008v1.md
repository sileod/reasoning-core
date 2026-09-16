# Tree pattern occurrence count (P008v1)

## Level 0

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 b -> 1,4
  1 a -> 2,3
  2 a
  3 b
  4 b
Pattern tree:
  0 b -> 1
  1 *
How many rooted embeddings are there? Answer with the integer count only.

Answer:
4

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 a -> 1
  1 b -> 2,4
  2 b -> 3
  3 a
  4 a
Pattern tree:
  0 a -> 1
  1 a
How many rooted embeddings are there? Answer with the integer count only.

Answer:
2

## Level 2

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 b -> 1
  1 b -> 2,4,5
  2 a -> 3
  3 b
  4 a
  5 a
Pattern tree:
  0 * -> 1,2
  1 *
  2 a
How many rooted embeddings are there? Answer with the integer count only.

Answer:
5

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 b -> 1
  1 c -> 2,3
  2 b -> 4
  3 a
  4 a -> 5
  5 b
Pattern tree:
  0 b -> 1
  1 c -> 2
  2 *
How many rooted embeddings are there? Answer with the integer count only.

Answer:
4

## Level 5

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 a -> 1,6
  1 b -> 2,4
  2 c -> 3,5
  3 a
  4 c
  5 b
  6 a
Pattern tree:
  0 b -> 1,2
  1 * -> 3
  2 c
  3 *
How many rooted embeddings are there? Answer with the integer count only.

Answer:
2

### Example

Prompt:
An ordered tree is given as adjacency lists, one line per node: "<index> <label> -> <child-index>,<child-index>" in left-to-right child order (root is index 0, labels are single letters). A pattern label '*' matches any host label. Count every rooted embedding of the pattern tree into the host: an injective map of pattern nodes to host nodes where each pattern node maps to a host node of the same label and the children of every pattern node occupy pairwise distinct child-subtrees of the host image, in the given order. Two embeddings that differ at any node position are counted separately.
Host tree:
  0 c -> 1,2,3,4
  1 a
  2 a -> 6
  3 b
  4 a -> 5
  5 a
  6 c
Pattern tree:
  0 c -> 1,2,3
  1 c
  2 b
  3 a
How many rooted embeddings are there? Answer with the integer count only.

Answer:
2
