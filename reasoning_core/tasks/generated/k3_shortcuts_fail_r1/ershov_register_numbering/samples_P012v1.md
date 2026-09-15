# Samples P012v1: Ershov register numbering

## Level 0

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is ((3 4) (((8 9) ((12 13) (15 16))) (((20 21) 22) 23))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

12,13,11,15,16,14,10,8,9,7,6,20,21,19,22,18,23,17,5,3,4,2,1|3

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is ((3 (5 (7 (9 (11 12))))) ((15 (17 18)) (20 (22 23)))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

17,18,16,15,14,22,23,21,20,19,13,11,12,10,9,8,7,6,5,4,3,2,1|3

## Level 2

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is ((((5 6) (8 (10 11))) (13 (15 16))) ((19 20) ((23 24) ((27 28) ((31 ((34 35) 36)) (38 39)))))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

5,6,4,10,11,9,8,7,3,15,16,14,13,12,2,34,35,33,36,32,31,30,38,39,37,29,27,28,26,25,23,24,22,21,19,20,18,17,1|4

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is (((4 ((7 8) 9)) 10) (((((16 ((19 20) (22 23))) 24) (26 ((29 30) 31))) (33 34)) ((37 38) 39))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

19,20,18,22,23,21,17,16,15,24,14,29,30,28,31,27,26,25,13,33,34,32,12,37,38,36,39,35,11,7,8,6,9,5,4,3,10,2,1|3

## Level 5

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is (((4 ((7 (9 (11 12))) 13)) (((17 (19 20)) ((23 24) 25)) ((28 29) (31 32)))) ((((37 38) (40 ((43 (45 46)) (48 49)))) (((53 54) 55) 56)) ((59 (61 62)) 63))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

19,20,18,17,16,23,24,22,25,21,15,28,29,27,31,32,30,26,14,11,12,10,9,8,7,6,13,5,4,3,2,45,46,44,43,42,48,49,47,41,40,39,37,38,36,35,53,54,52,55,51,56,50,34,61,62,60,59,58,63,57,33,1|4

**Prompt:**

An expression is evaluated on a machine where each live value occupies one register and each binary operation needs both of its operands already computed as it produces its result, consuming the two operands' registers and producing one. The expression tree is ((((((((9 10) (12 13)) 14) 15) 16) (18 (((22 23) 24) ((((29 30) ((33 34) 35)) (37 ((40 41) 42))) (44 45))))) 46) (((50 51) (53 54)) ((57 58) ((61 62) 63)))), where each id is a distinct subexpression value. You may reorder the independent subexpressions freely (they are independent), and at a node whose two children need equally many registers you may evaluate them in either order. Give the minimum number of registers needed to evaluate the whole expression, and one postorder sequence of node ids realizing that minimum, evaluating the heavier child (more registers needed) first, ties in either order. Answer as the comma-separated node sequence followed by a vertical bar and the register count, e.g. 2,3,1|2.

**Answer:**

9,10,8,12,13,11,7,14,6,15,5,16,4,29,30,28,33,34,32,35,31,27,40,41,39,42,38,37,36,26,44,45,43,25,22,23,21,24,20,19,18,17,3,46,2,50,51,49,53,54,52,48,57,58,56,61,62,60,63,59,55,47,1|5
