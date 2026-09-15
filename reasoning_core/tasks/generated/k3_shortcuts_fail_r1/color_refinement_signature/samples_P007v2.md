## Level 0
### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..3, listed with their neighbors:
0: 1
1: 0 2 3
2: 1
3: 1

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0 2 3;1

### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..6, listed with their neighbors:
0: 1 2 3 6
1: 0 4
2: 0
3: 0
4: 1 5
5: 4
6: 0

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0;1;2 3 6;4;5

## Level 2
### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..10, listed with their neighbors:
0: 2 3 7 8 10
1: 3 5 6 9 10
2: 0 3 4 7 8 10
3: 0 1 2 5 6 7 9 10
4: 2 5 9
5: 1 3 4 7 9 10
6: 1 3 8 9 10
7: 0 2 3 5 8 10
8: 0 2 6 7 9
9: 1 3 4 5 6 8 10
10: 0 1 2 3 5 6 7 9

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0;1;2;3 10;4;5;6;7;8;9

### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..7, listed with their neighbors:
0: 3 5 6
1: 2 3 7
2: 1 3 7
3: 0 1 2 4 5 7
4: 3 6
5: 0 3 6
6: 0 4 5
7: 1 2 3

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0 5;1 2 7;3;4;6

## Level 5
### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..2, listed with their neighbors:
0: 
1: 
2: 

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0 1 2

### Prompt

Perform the standard color refinement (1-dimensional Weisfeiler-Leman) on the following undirected graph. Give every vertex the same starting color 0. Then repeat a refinement round: the new color of a vertex is determined by its own color together with the sorted multiset of its neighbors' colors, and two vertices keep the same color exactly when both their own colors and their sorted neighbor-color multisets are identical; relabel the resulting classes as new colors arbitrarily. Stop once a full round changes nothing. The final stable coloring partitions the vertices into color classes.

Vertices are the integers 0..7, listed with their neighbors:
0: 1 2 6
1: 0 3
2: 0 4 7
3: 1
4: 2 5
5: 4
6: 0
7: 2

Give the final stable color partition as the canonical list of its classes. Write each class as its vertex numbers in ascending order and list the classes in ascending order of their first vertex. Join the vertices within a class with a single space and separate the classes with a semicolon. For example, if vertices {0,3} share one color and vertices {1,2,4,5} share another, the answer is:
0 3;1 2 4 5

### Answer

0 2;1 4;3 5;6 7
