
## Level 0

### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (-6, -6)
1: (5, -6)
2: (0, 0)
3: (4, 4)
4: (8, 8)
5: (-3, 0)
6: (-6, 0)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[0, 4, 3, 2] diags=[(1, 6), (3, 5), (2, 5), (1, 5)]


### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (-8, -8)
1: (-5, -7)
2: (-2, -6)
3: (-7, -7)
4: (4, 5)
5: (-3, -2)
6: (2, 7)
7: (-7, 6)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[2, 1, 0, 4, 3] diags=[(1, 3), (0, 3), (3, 7), (3, 5), (5, 7)]


## Level 2

### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (3, -20)
1: (20, -18)
2: (20, -12)
3: (20, -6)
4: (11, -7)
5: (8, -2)
6: (6, 4)
7: (4, 10)
8: (1, 16)
9: (-7, 17)
10: (-15, 18)
11: (-17, 11)
12: (0, -17)
13: (-15, -6)
14: (-13, -14)
15: (-20, -18)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[0, 3, 2, 7, 6, 8, 5, 9, 4, 10, 11, 1, 13] diags=[(1, 15), (2, 4), (1, 4), (6, 8), (5, 8), (5, 9), (4, 9), (4, 10), (1, 10), (1, 11), (1, 12), (12, 15), (12, 14)]


### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (11, -20)
1: (16, -17)
2: (19, -2)
3: (18, -2)
4: (17, -2)
5: (19, 11)
6: (20, 19)
7: (5, 13)
8: (5, 11)
9: (5, 9)
10: (-4, 5)
11: (1, -13)
12: (-4, -16)
13: (-9, -19)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[0, 2, 3, 5, 6, 4, 7, 8, 9, 10, 11] diags=[(1, 13), (1, 3), (1, 4), (4, 6), (4, 7), (1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12)]


## Level 5

### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (-12, -29)
1: (36, 12)
2: (24, 4)
3: (12, -4)
4: (9, -7)
5: (6, 7)
6: (13, 22)
7: (20, 37)
8: (10, 27)
9: (0, 17)
10: (3, 32)
11: (-8, -10)
12: (-5, 25)
13: (-13, 20)
14: (-17, 33)
15: (-37, 18)
16: (-32, 1)
17: (-29, -16)
18: (-33, -25)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[1, 2, 3, 0, 7, 6, 8, 5, 10, 9, 4, 11, 14, 15, 13, 16] diags=[(0, 2), (0, 3), (0, 4), (4, 18), (6, 8), (5, 8), (5, 9), (4, 9), (9, 11), (4, 11), (11, 18), (12, 18), (13, 15), (13, 16), (12, 16), (12, 17)]


### Example

**Prompt:**

Triangulate the simple polygon whose vertices are listed below in counterclockwise order, each as "index: (x, y)":

0: (11, -34)
1: (24, -25)
2: (36, -6)
3: (31, -5)
4: (26, -4)
5: (36, 21)
6: (35, 19)
7: (32, 17)
8: (14, -26)
9: (17, -6)
10: (16, -1)
11: (15, 30)
12: (-1, 33)
13: (2, -14)
14: (-19, 32)
15: (-12, 10)
16: (-5, -12)
17: (-26, 13)
18: (-27, 13)
19: (-28, 13)
20: (-14, -8)
21: (-14, -23)
22: (1, -30)
23: (-11, -29)

Algorithm (classic ear clipping): at each step consider every ear, which is a vertex v whose polygon-interior angle is strictly convex (positive signed turn under an exact, tolerance-free orientation test; collinear triples are allowed as vertices but never as ears) and whose diagonal between its two neighbours lies fully inside the polygon with no other vertex in the resulting triangle. Among all valid ears, cut the one whose tip vertex appears earliest in the current vertex order. Record the tip's ORIGINAL index and the added diagonal's two ORIGINAL endpoint indices, with the two endpoints written in ascending order. Repeat until exactly three vertices remain.

Answer exactly in the format  tips=[...] diags=[(a,c),(a,c),...]  : the ordered ear-tip original indices as tips, and the ordered diagonals you added as diags.

**Answer:**

tips=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21] diags=[(0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7), (0, 8), (0, 9), (0, 10), (0, 11), (0, 12), (0, 13), (0, 14), (0, 15), (0, 16), (0, 17), (0, 18), (0, 19), (0, 20), (0, 21), (0, 22)]
