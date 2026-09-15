## Level 0

### Prompt

Consider the tree on vertices 1..6 whose Prüfer code (built by repeated removal of the smallest leaf, appending its neighbor) is [1, 3, 1, 1]. Rebuild the tree from this code and list all its edges. Give every edge as u-v with u<v, edges separated by semicolons in lexicographic order.

### Answer

1-2;1-3;1-5;1-6;3-4

### Prompt

Consider the tree on vertices 1..5 with edges {1-2, 2-3, 2-5, 3-4}. Treat vertex 1 as the root and orient every edge away from it, so each other vertex has a unique parent. What is the parent vertex of vertex 4 in this rooted tree? Answer with a single integer.

### Answer

3

## Level 2

### Prompt

Consider the tree on vertices 1..10 whose Prüfer code (built by repeated removal of the smallest leaf, appending its neighbor) is [2, 2, 1, 6, 1, 4, 1, 1]. Rebuild the tree from this code and list all its edges. Give every edge as u-v with u<v, edges separated by semicolons in lexicographic order.

### Answer

1-2;1-4;1-6;1-9;1-10;2-3;2-5;4-8;6-7

### Prompt

Consider the tree on vertices 1..10 with edges {1-2, 1-3, 1-4, 1-8, 1-9, 1-10, 3-6, 4-5, 6-7}. Treat vertex 1 as the root and orient every edge away from it, so each other vertex has a unique parent. What is the parent vertex of vertex 3 in this rooted tree? Answer with a single integer.

### Answer

1

## Level 5

### Prompt

Consider the tree on vertices 1..16 with edges {1-2, 1-3, 1-4, 1-5, 1-6, 1-12, 1-14, 2-8, 5-11, 6-7, 6-9, 7-15, 8-10, 8-16, 12-13}. A labeled tree can be encoded as its Prüfer code by the rule: at each step, remove the smallest-labeled leaf and append its neighbor to the code, repeating until only two vertices remain. What is the 13th entry of the Prüfer code of this tree? Answer with a single integer.

### Answer

2

### Prompt

Consider the tree on vertices 1..10 whose Prüfer code (built by repeated removal of the smallest leaf, appending its neighbor) is [2, 1, 4, 4, 1, 5, 8, 5]. Rebuild the tree from this code and list all its edges. Give every edge as u-v with u<v, edges separated by semicolons in lexicographic order.

### Answer

1-2;1-4;1-5;2-3;4-6;4-7;5-8;5-10;8-9
