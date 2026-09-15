# Skyline rectangle update samples (P002v1)

## Level 0

### Example 1

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,10). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-1 0, 1-10 2

We now insert the rectangle spanning x in [0,2) with height 1.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 0-1 0->1 ; 1

### Example 2

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,10). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-9 3, 9-10 0

We now insert the rectangle spanning x in [1,10) with height 3.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 9-10 0->3 ; 3

## Level 2

### Example 1

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,24). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-6 0, 6-8 1, 8-19 5, 19-21 2, 21-24 0

We now remove the rectangle spanning x in [17,21) with height 2.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 19-21 2->0 ; -4

### Example 2

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,24). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-5 0, 5-20 6, 20-22 3, 22-24 5

We now remove the rectangle spanning x in [22,24) with height 5.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 22-24 5->3 ; -4

## Level 5

### Example 1

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,45). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-7 0, 7-10 4, 10-12 7, 12-27 6, 27-30 4, 30-31 0, 31-41 8, 41-45 5

We now insert the rectangle spanning x in [30,41) with height 2.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 30-31 0->2 ; 2

### Example 2

We track the height profile of rectangles resting on the ground at y=0 over the x-range [0,45). It is given as runs "x1-x2 h", meaning the occupied height is h from x1 to x2 (h=0 means empty), covering the whole range:
0-8 0, 8-14 7, 14-26 9, 26-27 0, 27-34 8, 34-36 0, 36-37 1, 37-38 0, 38-42 5, 42-45 3

We now insert the rectangle spanning x in [40,43) with height 5.

List every maximal run in the new profile whose height differs from the base profile there, as "x1-x2 old->new", separated by commas, in increasing x order. After " ; " write the signed integer change in total covered area (new total minus old total).
Example answer: 2-4 3->1, 6-9 3->0 ; -8

**Answer**: 42-43 3->5 ; 2

