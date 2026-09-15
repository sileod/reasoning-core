## Level 0

### Example 1
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((8,1),(9,-6,9),(-3,7,-5)). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
1;-5,7,9

### Example 2
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((5,-7),(-9,-4),(0,-3)). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
-3;-4

### Example 3
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((-3,6),(-1,-3,-7)). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
-3;-7

## Level 2

### Example 1
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is (((2,6,3),(-1,2,4),(-7,9,8)),((-1,1,-6),(4,7,-8),(-4,-6,9)),((0,-6),(-9,-6,9))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
4;-9,-8,-6,-4,4,7,8,9

### Example 2
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is (((-2,7),(9,7,-8),(-9,2)),((-8,-1,-7),(7,9))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
2;-8,7,9

### Example 3
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is (((-5,2,-2),(8,5,-8)),((-3,-8),(7,-3,5))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
2;-8,-3,5,7

## Level 5

### Example 1
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((((3,-1),(4,9)),((-3,4,0),(2,-1,1),(0,-5,2)),((-7,1),(8,3,3))),(((-6,0,8),(6,9,7),(8,2,2)),((8,-9),(7,-6,9)))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
-1;0,2,8,9

### Example 2
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((((-5,-6),(-1,-9,-1)),((-6,-6,3),(2,5)),((-6,-7),(6,3))),(((-3,-2,8),(-2,4,2),(-1,2)),((-4,3),(5,9,-1),(-7,1,7))),(((-1,-7),(-6,2)),((-4,-8,2),(0,-3,8)))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
-1;-8,-7,-4,-3,-1,0,1,2,5,7,8

### Example 3
**Prompt**
Consider a game tree encoded as nested parentheses: each tuple is an internal node whose children are listed left to right, and leaves are integers. MAX nodes appear at even depth (the root, depth 0), MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right move order, and record every leaf that is pruned by a cutoff (never evaluated). The tree is ((((-4,1),(-6,-1)),((7,2,-6),(3,-4,5)),((7,3,-2),(-4,-6,5),(-8,5,9))),(((8,9),(9,3,-7),(-7,-9)),((-9,9),(0,0,9),(-4,9,-5)),((7,-5),(5,4,-2),(7,3)))). Report the root value and the sorted, comma-separated list of pruned leaf values as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).

**Answer**
0;-9,-8,-7,-6,-5,-4,-1,5,9
