# Samples: prufer_coding (P006v1)


## Level 0


### Example 1

Prompt:

A labeled tree has vertices 1 through 5. Its undirected edges are: (1,2), (1,3), (1,4), (3,5). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

1 1 3

### Example 2

Prompt:

A labeled tree has vertices 1 through 4. Its undirected edges are: (1,3), (2,3), (2,4). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

3 2

## Level 2


### Example 1

Prompt:

A labeled tree has vertices 1 through 8. Its undirected edges are: (1,8), (2,3), (2,6), (3,5), (4,5), (4,8), (7,8). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

8 2 3 5 4 8

### Example 2

Prompt:

A labeled tree has vertices 1 through 8. Its undirected edges are: (1,3), (1,6), (1,8), (2,5), (2,7), (4,8), (5,6). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

1 8 2 5 6 1

## Level 5


### Example 1

Prompt:

A labeled tree has vertices 1 through 17. Its undirected edges are: (1,3), (1,5), (2,16), (3,15), (3,17), (4,7), (5,14), (6,8), (6,9), (7,16), (7,17), (8,10), (8,13), (10,14), (11,17), (12,14). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

16 7 6 8 17 14 8 10 14 5 1 3 3 17 7

### Example 2

Prompt:

A labeled tree has vertices 1 through 13. Its undirected edges are: (1,8), (1,10), (2,9), (2,10), (2,12), (3,6), (4,9), (5,6), (6,8), (7,12), (10,13), (11,13). The Prufer code of a labeled tree is built by repeatedly removing the leaf with the smallest remaining label and appending the label of its unique neighbor, until two vertices remain; the code has length n-2. Compute the Prufer code of this tree and report it as a space-separated list of integers in the exact order the algorithm produces. Format example: 2 3 1. Give only the code.

Answer:

6 9 6 8 12 1 10 2 13 2 10
