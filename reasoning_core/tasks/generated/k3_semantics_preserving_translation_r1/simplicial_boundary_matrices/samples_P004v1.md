# Level 0

## Example 1

**Prompt:**

A simplicial complex has vertices 0..3. Its faces are:
dimension 0: {0}, {1}, {2}, {3}
dimension 1: {0 1}, {0 2}, {0 3}, {1 3}
Compute the boundary matrix over GF(2) between dimension 0 and dimension 1. Rows are the dimension-0 simplices in this order: {0}, {1}, {2}, {3}. Columns are the dimension-1 simplices in this order: {0 1}, {0 2}, {0 3}, {1 3}. The matrix has 4 rows and 4 columns (dimensions 4x4). Answer as a sparse matrix row,col:1 pairs (all entries are 1 mod 2) separated by semicolons, ordered by row then column. Use 0x{n}x{m} if the matrix is all zero.

**Answer:**

0,0:1;0,1:1;0,2:1;1,0:1;1,3:1;2,1:1;3,2:1;3,3:1

## Example 2

**Prompt:**

A simplicial complex on vertices 0..3 is known only by its edges, which are:
{0 1}, {0 2}, {0 3}, {1 2}, {1 3}.
It is closed under taking faces: whenever a k-simplex is present, every (k-1)-face of it is present, and conversely any set of vertices all of whose pairwise edges are present forms a simplex. Rebuild the full complex and list every simplex as comma-separated vertex indices {a},{b},{c} for 4 vertices, ordered by dimension then lexicographically within a dimension, joined by semicolons.

**Answer:**

0;1;2;3;0,1;0,2;0,3;1,2;1,3;0,1,2

# Level 2

## Example 1

**Prompt:**

A simplicial complex on vertices 0..6 is known only by its edges, which are:
{0 1}, {0 2}, {0 3}, {0 4}, {0 5}, {0 6}, {1 3}, {1 6}, {2 3}, {2 4}, {2 5}, {3 4}, {3 5}, {3 6}.
It is closed under taking faces: whenever a k-simplex is present, every (k-1)-face of it is present, and conversely any set of vertices all of whose pairwise edges are present forms a simplex. Rebuild the full complex and list every simplex as comma-separated vertex indices {a},{b},{c} for 7 vertices, ordered by dimension then lexicographically within a dimension, joined by semicolons.

**Answer:**

0;1;2;3;4;5;6;0,1;0,2;0,3;0,4;0,5;0,6;1,3;1,6;2,3;2,4;2,5;3,4;3,5;3,6

## Example 2

**Prompt:**

A simplicial complex has vertices 0..4. Its faces are:
dimension 0: {0}, {1}, {2}, {3}, {4}
dimension 1: {0 1}, {0 2}, {0 4}, {1 2}, {1 3}, {1 4}
dimension 2: {0 1 2}, {0 1 4}
Compute the signed incidence boundary matrix between dimension 1 and dimension 2. Rows are the dimension-1 simplices in this order: {0 1}, {0 2}, {0 4}, {1 2}, {1 3}, {1 4}. Columns are the dimension-2 simplices in this order: {0 1 2}, {0 1 4}. For each column simplex, write its vertices in increasing order; the entry in the row whose simplex is that column with the vertex at position i removed equals (-1)^i. The matrix has 6 rows and 2 columns. Answer as sparse row,col:value pairs with value -1 or 1, separated by semicolons, ordered by row then column. Use 0x{n}x{m} if the matrix is all zero.

**Answer:**

0,0:1;0,1:1;1,0:-1;2,1:-1;3,0:1;5,1:1

# Level 5

## Example 1

**Prompt:**

A simplicial complex has vertices 0..8. Its faces are:
dimension 0: {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}
dimension 1: {0 2}, {0 4}, {0 5}, {0 8}, {1 2}, {1 6}, {1 8}, {3 8}, {4 7}, {4 8}, {5 8}, {6 7}, {6 8}, {7 8}
dimension 2: {1 6 8}, {4 7 8}, {6 7 8}
Compute the signed incidence boundary matrix between dimension 0 and dimension 1. Rows are the dimension-0 simplices in this order: {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}. Columns are the dimension-1 simplices in this order: {0 2}, {0 4}, {0 5}, {0 8}, {1 2}, {1 6}, {1 8}, {3 8}, {4 7}, {4 8}, {5 8}, {6 7}, {6 8}, {7 8}. For each column simplex, write its vertices in increasing order; the entry in the row whose simplex is that column with the vertex at position i removed equals (-1)^i. The matrix has 9 rows and 14 columns. Answer as sparse row,col:value pairs with value -1 or 1, separated by semicolons, ordered by row then column. Use 0x{n}x{m} if the matrix is all zero.

**Answer:**

0,0:-1;0,1:-1;0,2:-1;0,3:-1;1,4:-1;1,5:-1;1,6:-1;2,0:1;2,4:1;3,7:-1;4,1:1;4,8:-1;4,9:-1;5,2:1;5,10:-1;6,5:1;6,11:-1;6,12:-1;7,8:1;7,11:1;7,13:-1;8,3:1;8,6:1;8,7:1;8,9:1;8,10:1;8,12:1;8,13:1

## Example 2

**Prompt:**

A simplicial complex has vertices 0..8. Its faces are:
dimension 0: {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}
dimension 1: {0 1}, {0 2}, {0 3}, {0 4}, {0 5}, {0 7}, {1 5}, {1 7}, {2 4}, {2 5}, {2 6}, {2 7}, {2 8}, {3 5}, {3 6}, {4 5}, {4 7}, {5 6}, {5 8}, {6 7}, {6 8}, {7 8}
Compute the signed incidence boundary matrix between dimension 0 and dimension 1. Rows are the dimension-0 simplices in this order: {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}. Columns are the dimension-1 simplices in this order: {0 1}, {0 2}, {0 3}, {0 4}, {0 5}, {0 7}, {1 5}, {1 7}, {2 4}, {2 5}, {2 6}, {2 7}, {2 8}, {3 5}, {3 6}, {4 5}, {4 7}, {5 6}, {5 8}, {6 7}, {6 8}, {7 8}. For each column simplex, write its vertices in increasing order; the entry in the row whose simplex is that column with the vertex at position i removed equals (-1)^i. The matrix has 9 rows and 22 columns. Answer as sparse row,col:value pairs with value -1 or 1, separated by semicolons, ordered by row then column. Use 0x{n}x{m} if the matrix is all zero.

**Answer:**

0,0:-1;0,1:-1;0,2:-1;0,3:-1;0,4:-1;0,5:-1;1,0:1;1,6:-1;1,7:-1;2,1:1;2,8:-1;2,9:-1;2,10:-1;2,11:-1;2,12:-1;3,2:1;3,13:-1;3,14:-1;4,3:1;4,8:1;4,15:-1;4,16:-1;5,4:1;5,6:1;5,9:1;5,13:1;5,15:1;5,17:-1;5,18:-1;6,10:1;6,14:1;6,17:1;6,19:-1;6,20:-1;7,5:1;7,7:1;7,11:1;7,16:1;7,19:1;7,21:-1;8,12:1;8,18:1;8,20:1;8,21:1

