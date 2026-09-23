# Level 0

**Example 1**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); split into 1+2+3; remove 2 token(s); remove 1 token(s)
of size 5: remove 4 token(s); split into 1+2+3; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); remove 4 token(s); split into 2+3+5; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); remove 5 token(s); split into 2+4+5; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); split into 1+3+6; remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 4+7; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 5+8; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 6? Answer with a single non-negative integer.

**Answer:** 3

**Example 2**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); split into 1+2+3; remove 2 token(s); remove 1 token(s)
of size 5: remove 4 token(s); split into 1+4; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); remove 4 token(s); remove 3 token(s); split into 3+4; remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); split into 1+3+5; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); remove 6 token(s); split into 2+7; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); split into 5+7+8; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); split into 1+2+9; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 6? Answer with a single non-negative integer.

**Answer:** 5

# Level 2

**Example 1**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); split into 1+2+3; remove 2 token(s); remove 1 token(s)
of size 5: remove 4 token(s); remove 3 token(s); split into 2+3+4; remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); split into 1+2+4; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); remove 5 token(s); split into 2+3; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 3+5; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); remove 6 token(s); split into 3+5+7; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); split into 1+3+6; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 11: remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); split into 9+10; remove 1 token(s)
of size 12: remove 11 token(s); remove 10 token(s); remove 9 token(s); split into 3+4+11; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 13: remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 8+10+12; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 14: remove 13 token(s); remove 12 token(s); remove 11 token(s); split into 3+5; remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 12? Answer with a single non-negative integer.

**Answer:** 11

**Example 2**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); remove 2 token(s); split into 2+3; remove 1 token(s)
of size 5: remove 4 token(s); split into 1+4; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); split into 1+4+5; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); split into 1+5; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); remove 6 token(s); split into 2+4; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 4+7; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); remove 8 token(s); split into 2+4; remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 11: remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 6+9; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 12: remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); split into 6+11; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 13: remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); split into 4+5+8; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 14: remove 13 token(s); remove 12 token(s); split into 2+8+9; remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 6? Answer with a single non-negative integer.

**Answer:** 5

# Level 5

**Example 1**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); split into 1+2+3; remove 2 token(s); remove 1 token(s)
of size 5: remove 4 token(s); split into 1+2; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); remove 4 token(s); split into 2+5; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); remove 5 token(s); remove 4 token(s); split into 3+4+5; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); split into 1+3+4; remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); split into 2+6; remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); split into 1+3; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 11: remove 10 token(s); remove 9 token(s); split into 2+4; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 12: remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); split into 4+5; remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 13: remove 12 token(s); split into 1+4; remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 14: remove 13 token(s); remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); split into 10+12; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 15: remove 14 token(s); remove 13 token(s); remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); split into 9+11+14; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 16: remove 15 token(s); remove 14 token(s); remove 13 token(s); remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); split into 7+12+13; remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 12? Answer with a single non-negative integer.

**Answer:** 11

**Example 2**

A take-away game is played on a single heap of tokens. From a heap of size n, a move either removes some tokens leaving one smaller heap, or (for some sizes) splits n into several independent subheaps which are then played separately. The game value (Grundy nimber) of a heap is the mex of the XOR-combined values of the heaps reachable in one move; the positions are lost exactly when the nimber is 0. Move sets:
of size 1: 
of size 2: remove 1 token(s)
of size 3: remove 2 token(s); split into 1+2; remove 1 token(s)
of size 4: remove 3 token(s); split into 1+2+3; remove 2 token(s); remove 1 token(s)
of size 5: remove 4 token(s); remove 3 token(s); split into 2+3+4; remove 2 token(s); remove 1 token(s)
of size 6: remove 5 token(s); split into 1+2+5; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 7: remove 6 token(s); split into 1+3+5; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 8: remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); split into 4+6; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 9: remove 8 token(s); remove 7 token(s); remove 6 token(s); split into 3+4+6; remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 10: remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); split into 6+7+8; remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 11: remove 10 token(s); split into 1+2+9; remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 12: remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); split into 7+8+9; remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 13: remove 12 token(s); remove 11 token(s); remove 10 token(s); split into 3+4+10; remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 14: remove 13 token(s); remove 12 token(s); split into 2+6; remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 15: remove 14 token(s); split into 1+6+11; remove 13 token(s); remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
of size 16: remove 15 token(s); split into 1+4; remove 14 token(s); remove 13 token(s); remove 12 token(s); remove 11 token(s); remove 10 token(s); remove 9 token(s); remove 8 token(s); remove 7 token(s); remove 6 token(s); remove 5 token(s); remove 4 token(s); remove 3 token(s); remove 2 token(s); remove 1 token(s)
What is the nimber of a heap of size 16? Answer with a single non-negative integer.

**Answer:** 15

