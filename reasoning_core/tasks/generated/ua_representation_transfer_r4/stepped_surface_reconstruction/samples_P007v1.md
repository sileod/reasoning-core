## Level 0

### Prompt

A stepped surface over a 2x2 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..1 top to bottom, columns 0..1 left to right.

Height array:
1 1
0 0

What is the cube-stack height at column (1,1) on this surface? Give the answer as a single number.

**Answer**: 0

### Prompt

A stepped surface over a 2x2 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..1 top to bottom, columns 0..1 left to right.

Height array:
0 0
0 0

What is the cube-stack height at column (1,0) on this surface? Give the answer as a single number.

**Answer**: 0

## Level 2

### Prompt

A stepped surface over a 4x4 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..3 top to bottom, columns 0..3 left to right.

Height array:
2 0 0 0
2 0 0 0
2 0 0 0
2 0 0 0

At integer level k, the cross-section marks each column (r,c) occupied when H[r][c] >= k. Give the cross-section at level 2 as one string of length 16, reading rows in order and within each row columns in order, writing X for an occupied column and . for an empty one. Give the answer as a single string.

**Answer**: X...X...X...X...

### Prompt

A stepped surface over a 4x4 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..3 top to bottom, columns 0..3 left to right.

Height array:
1 0 0 0
1 0 0 0
1 0 0 0
0 0 0 0

What is the cube-stack height at column (2,1) on this surface? Give the answer as a single number.

**Answer**: 0

## Level 5

### Prompt

A stepped surface over a 7x7 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..6 top to bottom, columns 0..6 left to right.

Height array:
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0

A unit cube (r,c,k) is inside the order ideal exactly when k <= H[r][c]. Is the cube (5,5,1) occupied? Give the answer as a single word.

**Answer**: no

### Prompt

A stepped surface over a 7x7 box is given by a monotone height array H: column (r,c) stacks H[r][c] unit cubes, so H is the top face of a 3D order ideal of cubes and the height function of the equivalent lozenge tiling. H never increases as r or c grows. Rows are indexed 0..6 top to bottom, columns 0..6 left to right.

Height array:
2 2 1 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0

At integer level k, the cross-section marks each column (r,c) occupied when H[r][c] >= k. Give the cross-section at level 3 as one string of length 49, reading rows in order and within each row columns in order, writing X for an occupied column and . for an empty one. Give the answer as a single string.

**Answer**: .................................................
