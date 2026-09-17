# Samples: block_pile_surface_accounting (P002v2)

## Level 0

### Example 1

Prompt:

A pile of cubes stands on a floor. The horizontal floor covers exactly the 3 by 3 cells x=0..2, y=0..2. It has no walls; faces along its perimeter touch air.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The complete cube coordinate list (x, y, z) is:
(0,0,0),(1,2,0),(2,0,0),(2,2,0)
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 0,0,0,0,2,2

### Example 2

Prompt:

A pile of cubes stands on a floor. The horizontal floor covers exactly the 3 by 3 cells x=0..2, y=0..2. It has no walls; faces along its perimeter touch air.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The height map has rows in increasing x and columns in increasing y, both starting at 0. Height h means cubes at z=0 through h-1; 0 means an empty column:
2 2 2
2 2 2
2 2 2
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 1,5,8,4,0,0

## Level 2

### Example 1

Prompt:

A pile of cubes stands on a floor. The horizontal floor covers exactly the 4 by 4 cells x=0..3, y=0..3. It has no walls; faces along its perimeter touch air.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The height map has rows in increasing x and columns in increasing y, both starting at 0. Height h means cubes at z=0 through h-1; 0 means an empty column:
2 4 2 3
1 3 0 3
2 1 3 4
3 4 1 2
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 0,9,12,7,7,3

### Example 2

Prompt:

A pile of cubes stands on a floor. The horizontal floor covers exactly the 4 by 4 cells x=0..3, y=0..3. It has no walls; faces along its perimeter touch air.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The height map has rows in increasing x and columns in increasing y, both starting at 0. Height h means cubes at z=0 through h-1; 0 means an empty column:
1 1 1 1
1 2 2 2
1 2 3 3
1 2 2 4
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 5,5,9,8,1,1

## Level 5

### Example 1

Prompt:

A pile of cubes stands on a floor. The horizontal floor extends infinitely in both directions, with no walls.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The height map has rows in increasing x and columns in increasing y, both starting at 0. Height h means cubes at z=0 through h-1; 0 means an empty column:
0 0 6 6 6 6
0 6 0 6 0 6
0 6 6 6 6 6
5 0 6 6 6 0
6 6 2 0 1 6
6 0 6 6 6 6
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 5,31,62,41,7,0

### Example 2

Prompt:

A pile of cubes stands on a floor. The horizontal floor covers exactly the 6 by 6 cells x=0..5, y=0..5. It has no walls; faces along its perimeter touch air.
All cubes are axis-aligned unit cubes. The floor is at z=0; cube (x,y,z) occupies [x,x+1] by [y,y+1] by [z,z+1]. A face is exposed exactly when it touches neither another cube nor the floor. Edge or corner contact does not hide a face. There are no cubes other than those specified.
The height map has rows in increasing x and columns in increasing y, both starting at 0. Height h means cubes at z=0 through h-1; 0 means an empty column:
0 4 5 4 5 4
4 5 5 6 5 5
5 0 0 6 6 0
0 5 0 6 6 0
5 6 6 6 0 6
5 6 6 6 6 6
Use neighbour counting to give how many cubes have exactly 0,1,2,3,4,5 exposed faces, in that order, including fully hidden cubes. Answer only c0,c1,c2,c3,c4,c5 with no spaces; for example a single cube on the floor gives 0,0,0,0,0,1.

Answer: 13,61,44,24,7,1
