## Level 0

### Prompt

Two small relations are given below. Relation L has columns x, a (key x). Relation R has columns y, c (key y).

Perform an inner join of L and R on the condition that the keys are equal, keeping only the L rows that have at least one matching R row.

Project the join result onto the columns a, y.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a)
1, 4
1, 6

R (y, c)
0, 1
0, 7

### Answer

a, y


---

### Prompt

Two small relations are given below. Relation L has columns x, a (key x). Relation R has columns y, c (key y).

Perform an inner join of L and R on the condition that the keys are equal, keeping only the L rows that have at least one matching R row.

Project the join result onto the columns x, a.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a)
1, 7
1, 5

R (y, c)
1, 7
1, 8

### Answer

x, a
1, 7
1, 7
1, 5
1, 5

---

## Level 2

### Prompt

Two small relations are given below. Relation L has columns x, a (key x). Relation R has columns y, c.

Perform an anti join: keep each L row, once, if it has no matching R row; output only the L columns.

Project the join result onto the columns x, a.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a)
1, 5
0, 1
1, 7
0, 6

R (y, c)
0, 5
1, 3
1, 8
0, 4

### Answer

x, a


---

### Prompt

Two small relations are given below. Relation L has columns x, a (key x). Relation R has columns y, c (key y).

Perform a left join of L and R on the condition that the keys are equal, keeping every L row; for an L row with no matching R row, put NULL for the R columns.

Project the join result onto the columns y.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a)
1, 2
0, 4
1, 8
1, 8

R (y, c)
0, 2
1, 3
1, 5
1, 1

### Answer

y
1
1
1
0
1
1
1
1
1
1

---

## Level 5

### Prompt

Two small relations are given below. Relation L has columns x, a, b (key x). Relation R has columns y, c, d (key y).

Perform an inner join of L and R on the condition that the keys are equal, keeping only the L rows that have at least one matching R row.

Project the join result onto the columns x, a, b, y, d.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a, b)
0, 6, 5
0, 4, 6
2, 9, 1
3, 2, 7
1, 8, 2
0, 2, 2
3, 7, 7

R (y, c, d)
1, 7, 2
0, 6, 1
0, 3, 3
3, 6, 2
0, 1, 4
3, 7, 4
0, 2, 6

### Answer

x, a, b, y, d
0, 6, 5, 0, 1
0, 6, 5, 0, 3
0, 6, 5, 0, 4
0, 6, 5, 0, 6
0, 4, 6, 0, 1
0, 4, 6, 0, 3
0, 4, 6, 0, 4
0, 4, 6, 0, 6
3, 2, 7, 3, 2
3, 2, 7, 3, 4
1, 8, 2, 1, 2
0, 2, 2, 0, 1
0, 2, 2, 0, 3
0, 2, 2, 0, 4
0, 2, 2, 0, 6
3, 7, 7, 3, 2
3, 7, 7, 3, 4

---

### Prompt

Two small relations are given below. Relation L has columns x, a, b (key x). Relation R has columns y, c, d (key y).

Perform an inner join of L and R on the condition that the keys are equal, keeping only the L rows that have at least one matching R row.

Project the join result onto the columns x, a, b, c, d.

Write the resulting table with a first line listing the projected column names and one row per output line, values separated by ", " (a comma then a space), keeping rows in join order: for inner and left joins, walk the L rows in their given order and, for each, the matching R rows in their given order; for semi and anti joins, list the kept L rows in their given order. Represent a missing value as NULL. Example format:

p, q
1, 2
3, 4

L (x, a, b)
1, 7, 2
0, 8, 4
1, 4, 3
0, 6, 5
3, 4, 6
0, 9, 9
3, 7, 4

R (y, c, d)
1, 6, 9
1, 9, 7
2, 4, 3
2, 7, 6
1, 6, 5
1, 9, 6
1, 6, 9

### Answer

x, a, b, c, d
1, 7, 2, 6, 9
1, 7, 2, 9, 7
1, 7, 2, 6, 5
1, 7, 2, 9, 6
1, 7, 2, 6, 9
1, 4, 3, 6, 9
1, 4, 3, 9, 7
1, 4, 3, 6, 5
1, 4, 3, 9, 6
1, 4, 3, 6, 9

---
