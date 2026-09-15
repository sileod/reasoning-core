## Level 0

**Prompt:** {'nodes': 5, 'order': [1, 3, 2, 0, 4], 'adjacency': [[1], [0, 2], [1, 4], [4], [2, 3]], 'fill_edges': [[0, 2], [0, 4]], 'fill_size': 2, 'largest_clique': 3, 'mode': 'largest'}

**Prompt rendered:** An undirected graph on vertices 0..4 has edges {0-1, 1-2, 2-4, 3-4}. We eliminate vertices in the order [1, 3, 2, 0, 4]. Eliminating a vertex makes its current neighborhood (including the vertex) into a clique. What is the size of the largest clique formed during any elimination step? Answer with the integer.

**Answer:** 3

**Prompt:** {'nodes': 5, 'order': [3, 4, 2, 0, 1], 'adjacency': [[3], [3, 4], [3], [0, 1, 2, 4], [1, 3]], 'fill_edges': [[0, 1], [0, 2], [0, 4], [1, 2], [2, 4]], 'fill_size': 5, 'largest_clique': 5, 'mode': 'largest'}

**Prompt rendered:** An undirected graph on vertices 0..4 has edges {0-3, 1-3, 1-4, 2-3, 3-4}. We eliminate vertices in the order [3, 4, 2, 0, 1]. Eliminating a vertex makes its current neighborhood (including the vertex) into a clique. What is the size of the largest clique formed during any elimination step? Answer with the integer.

**Answer:** 5

## Level 2

**Prompt:** {'nodes': 9, 'order': [7, 3, 4, 1, 5, 8, 0, 2, 6], 'adjacency': [[5, 6], [2, 3, 4, 5, 7, 8], [1, 3, 4, 5, 7, 8], [1, 2, 4, 5, 6, 7], [1, 2, 3, 5, 6, 8], [0, 1, 2, 3, 4, 6, 7], [0, 3, 4, 5, 7], [1, 2, 3, 5, 6, 8], [1, 2, 4, 7]], 'fill_edges': [[0, 2], [0, 8], [1, 6], [2, 6], [3, 8], [5, 8], [6, 8]], 'fill_size': 7, 'largest_clique': 7, 'mode': 'list'}

**Prompt rendered:** An undirected graph on vertices 0..8 has edges {0-5, 0-6, 1-2, 1-3, 1-4, 1-5, 1-7, 1-8, 2-3, 2-4, 2-5, 2-7, 2-8, 3-4, 3-5, 3-6, 3-7, 4-5, 4-6, 4-8, 5-6, 5-7, 6-7, 7-8}. We eliminate vertices in the order [7, 3, 4, 1, 5, 8, 0, 2, 6]. Eliminating a vertex adds fill edges to make its current neighborhood a clique. What is the complete sorted list of added fill edges as unordered pairs a-b, separated by semicolons? If none are added, answer with 'none'.

**Answer:** 0-2;0-8;1-6;2-6;3-8;5-8;6-8

**Prompt:** {'nodes': 9, 'order': [7, 2, 6, 8, 5, 4, 1, 3, 0], 'adjacency': [[4, 6, 7], [2, 3, 6, 8], [1, 3, 5, 6, 7, 8], [1, 2, 5, 8], [0, 5, 7, 8], [2, 3, 4, 6, 7, 8], [0, 1, 2, 5, 8], [0, 2, 4, 5, 8], [1, 2, 3, 4, 5, 6, 7]], 'fill_edges': [[0, 1], [0, 2], [0, 3], [0, 5], [0, 8], [1, 4], [1, 5], [2, 4], [3, 4], [3, 6], [4, 6]], 'fill_size': 11, 'largest_clique': 6, 'mode': 'largest'}

**Prompt rendered:** An undirected graph on vertices 0..8 has edges {0-4, 0-6, 0-7, 1-8, 1-2, 1-3, 1-6, 2-3, 2-5, 2-6, 2-7, 2-8, 3-8, 3-5, 4-8, 4-5, 4-7, 5-6, 5-7, 5-8, 6-8, 7-8}. We eliminate vertices in the order [7, 2, 6, 8, 5, 4, 1, 3, 0]. Eliminating a vertex makes its current neighborhood (including the vertex) into a clique. What is the size of the largest clique formed during any elimination step? Answer with the integer.

**Answer:** 6

## Level 5

**Prompt:** {'nodes': 15, 'order': [11, 1, 13, 3, 2, 6, 12, 10, 7, 4, 9, 0, 14, 5, 8], 'adjacency': [[1, 2, 4, 5, 6, 7, 8, 10, 12, 13, 14], [0, 2, 5, 6, 8, 11, 14], [0, 1, 4, 5, 6, 7, 9, 10], [6, 8, 9, 11, 14], [0, 2, 7, 8, 10, 12], [0, 1, 2, 6, 7, 8, 9, 10, 11, 12, 13], [0, 1, 2, 3, 5, 8, 9, 10, 11, 12, 14], [0, 2, 4, 5, 8, 9, 10, 14], [0, 1, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13], [2, 3, 5, 6, 7, 8, 10, 12, 13], [0, 2, 4, 5, 6, 7, 8, 9, 12, 13], [1, 3, 5, 6, 8, 13], [0, 4, 5, 6, 8, 9, 10, 13], [0, 5, 8, 9, 10, 11, 12], [0, 1, 3, 6, 7]], 'fill_edges': [[0, 3], [0, 9], [1, 3], [1, 13], [2, 3], [2, 8], [2, 12], [2, 13], [2, 14], [3, 5], [3, 10], [3, 12], [3, 13], [4, 5], [4, 6], [4, 9], [4, 14], [5, 14], [6, 7], [6, 13], [7, 12], [8, 14], [9, 14], [10, 14], [12, 14], [13, 14]], 'fill_size': 26, 'largest_clique': 8, 'mode': 'size'}

**Prompt rendered:** An undirected graph on vertices 0..14 has edges {0-1, 0-2, 0-4, 0-5, 0-6, 0-7, 0-8, 0-10, 0-12, 0-13, 0-14, 1-2, 1-5, 1-6, 1-8, 1-11, 1-14, 2-4, 2-5, 2-6, 2-7, 2-9, 2-10, 3-6, 3-8, 3-9, 3-11, 3-14, 4-7, 4-8, 4-10, 4-12, 5-6, 5-7, 5-8, 5-9, 5-10, 5-11, 5-12, 5-13, 6-8, 6-9, 6-10, 6-11, 6-12, 6-14, 7-8, 7-9, 7-10, 7-14, 8-9, 8-10, 8-11, 8-12, 8-13, 9-10, 9-12, 9-13, 10-12, 10-13, 11-13, 12-13}. We eliminate vertices in the order [11, 1, 13, 3, 2, 6, 12, 10, 7, 4, 9, 0, 14, 5, 8]. Eliminating a vertex adds fill edges to make its current neighborhood a clique. How many fill edges are added in total? Answer with the count.

**Answer:** 26

**Prompt:** {'nodes': 15, 'order': [6, 1, 11, 3, 2, 5, 13, 14, 12, 4, 0, 8, 9, 7, 10], 'adjacency': [[1, 2, 3, 4, 5, 7, 8, 9, 12, 13], [0, 3, 6, 9, 10, 12, 13], [0, 6, 7, 8, 9, 10, 11, 12, 13, 14], [0, 1, 5, 6, 10, 12], [0, 5, 7, 8, 9, 11, 12], [0, 3, 4, 7, 8, 9, 10, 12, 14], [1, 2, 3, 7, 8, 11], [0, 2, 4, 5, 6, 8, 9, 10, 11, 12, 14], [0, 2, 4, 5, 6, 7, 9, 10, 12, 13], [0, 1, 2, 4, 5, 7, 8, 10, 11, 12], [1, 2, 3, 5, 7, 8, 9, 12, 13, 14], [2, 4, 6, 7, 9, 12, 14], [0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14], [0, 1, 2, 8, 10, 12, 14], [2, 5, 7, 10, 11, 12, 13]], 'fill_edges': [[0, 10], [0, 11], [0, 14], [1, 2], [1, 7], [1, 8], [1, 11], [2, 3], [2, 4], [2, 5], [3, 4], [3, 7], [3, 8], [3, 9], [3, 11], [3, 13], [3, 14], [4, 10], [4, 13], [4, 14], [5, 13], [7, 13], [8, 11], [8, 14], [9, 13], [9, 14], [10, 11], [11, 13]], 'fill_size': 28, 'largest_clique': 9, 'mode': 'list'}

**Prompt rendered:** An undirected graph on vertices 0..14 has edges {0-1, 0-2, 0-3, 0-4, 0-5, 0-7, 0-8, 0-9, 0-12, 0-13, 1-3, 1-6, 1-9, 1-10, 1-12, 1-13, 2-6, 2-7, 2-8, 2-9, 2-10, 2-11, 2-12, 2-13, 2-14, 3-5, 3-6, 3-10, 3-12, 4-5, 4-7, 4-8, 4-9, 4-11, 4-12, 5-7, 5-8, 5-9, 5-10, 5-12, 5-14, 6-7, 6-8, 6-11, 7-8, 7-9, 7-10, 7-11, 7-12, 7-14, 8-9, 8-10, 8-12, 8-13, 9-10, 9-11, 9-12, 10-12, 10-13, 10-14, 11-12, 11-14, 12-13, 12-14, 13-14}. We eliminate vertices in the order [6, 1, 11, 3, 2, 5, 13, 14, 12, 4, 0, 8, 9, 7, 10]. Eliminating a vertex adds fill edges to make its current neighborhood a clique. What is the complete sorted list of added fill edges as unordered pairs a-b, separated by semicolons? If none are added, answer with 'none'.

**Answer:** 0-10;0-11;0-14;1-2;1-7;1-8;1-11;2-3;2-4;2-5;3-4;3-7;3-8;3-9;3-11;3-13;3-14;4-10;4-13;4-14;5-13;7-13;8-11;8-14;9-13;9-14;10-11;11-13
