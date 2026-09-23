## Level 0

### Example 1

Consider the 3x3 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..2, columns 0..2):
39 6 26
25 15 23
22 9 5

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

36|(0,1),(1,0),(2,2)

### Example 2

Consider the 3x3 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..2, columns 0..2):
38 17 13
4 6 8
13 16 19

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

32|(0,2),(1,1),(2,0)

## Level 2

### Example 1

Consider the 5x5 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..4, columns 0..4):
5 4 33 37 24
26 56 13 15 37
6 51 52 34 18
20 27 2 14 35
28 15 24 9 25

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

52|(3,2),(1,3),(0,1),(2,0),(4,4)

### Example 2

Consider the 5x5 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..4, columns 0..4):
18 21 39 14 22
5 50 13 23 33
14 49 14 12 51
30 42 34 37 32
52 22 20 25 3

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

75|(4,4),(1,0),(0,1),(2,3),(3,2)

## Level 5

### Example 1

Consider the 8x8 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..7, columns 0..7):
69 51 65 67 1 15 45 32
78 39 78 68 76 19 23 32
44 21 3 55 14 28 64 74
57 24 6 20 61 12 54 10
49 56 66 79 56 21 20 54
19 32 80 73 54 25 26 43
50 61 71 57 78 17 1 64
28 7 18 43 10 32 33 3

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

104|(5,0),(3,3),(2,2),(0,4),(6,6),(4,5),(1,7),(7,1)

### Example 2

Consider the 8x8 cost matrix where entry (i,j) is the cost of assigning row i to column j; the goal is an optimal assignment (a one-to-one matching) that minimizes the total cost, with the cheapest total called the optimal tour value.

Matrix (rows 0..7, columns 0..7):
8 15 36 41 2 62 12 27
64 26 38 51 79 54 11 15
69 52 31 13 58 17 78 54
35 55 28 58 18 24 49 25
78 79 2 19 9 29 46 71
73 3 1 41 40 38 69 12
45 80 13 19 43 47 60 27
65 74 31 21 2 71 12 57

Solve it with branch-and-bound on the reduced matrix as follows. Reduce a matrix by subtracting the row minima then the column minima over the finite entries, and add the subtracted amounts to the node lower bound. For every zero cell, its penalty is the smallest finite entry in its row plus the smallest finite entry in its column, ignoring the zero itself. Branch on the zero of largest penalty; break ties by the lexicographic order of (row,column).  Its 'assign' child deletes that row and column from the reduced matrix and re-reduces; its 'exclude' child sets the cell to infinity and re-reduces.  Explore depth-first, always the assign child before the exclude child.  Initialize the incumbent (best complete assignment found so far) with a greedy row-by-row assignment: for each row in order pick the cheapest unused column and add its cost; update the incumbent whenever a leaf records a lower complete cost; and prune any node whose lower bound equals or exceeds the current incumbent.  A node with no remaining row or column records its complete assignment cost.

Report the optimal tour value and the branch order of the zero cells (given as (row,column), zero-indexed) in the exact order they are branched on, as
OPTIMAL_VALUE|(r,c),(r,c),...
For example, for a value of 17 branching first on the zero at row 1 column 2 then at row 0 column 1, write 17|(1,2),(0,1).

Answer:

87|(0,0),(5,1),(1,6),(7,4),(4,2),(3,7),(2,5),(6,3)

