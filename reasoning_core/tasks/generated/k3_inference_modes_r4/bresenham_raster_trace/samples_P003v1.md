## Level 0
### Example 1
**Prompt**
Using Bresenham's line algorithm with error term err initialized to dx + (-dy) for the line from (4,4) to (5,4), what is the integer decision value err at the start of step 2 (step 1 is the (4,4) endpoint)? Give the integer only.

**Answer**
1

### Example 2
**Prompt**
Using Bresenham's line algorithm with the standard integer error term (err initialized to dx + (-dy), updating err by -dy when 2*err >= -dy and by dx when 2*err <= dx), rasterize the line from (1,5) to (1,10). Give the full ordered list of pixels from start to end as a compact string of bracketed coordinate pairs, e.g. (0,0)(1,1)(2,2).

**Answer**
(1,5)(1,6)(1,7)(1,8)(1,9)(1,10)

## Level 2
### Example 1
**Prompt**
Using Bresenham's line algorithm with error term err initialized to dx + (-dy) for the line from (11,8) to (11,17), what is the integer decision value err at the start of step 3 (step 1 is the (11,8) endpoint)? Give the integer only.

**Answer**
-9

### Example 2
**Prompt**
Using the midpoint circle algorithm, rasterize the circle centered at (12,14) with radius 3. List every integer lattice pixel on the circle, sorted in ascending (x then y) order, as a compact string of bracketed coordinate pairs, e.g. (0,0)(1,1).

**Answer**
(9,13)(9,14)(9,15)(10,12)(10,16)(11,11)(11,17)(12,11)(12,17)(13,11)(13,17)(14,12)(14,16)(15,13)(15,14)(15,15)

## Level 5
### Example 1
**Prompt**
Using Bresenham's line algorithm with the standard integer error term (err initialized to dx + (-dy), updating err by -dy when 2*err >= -dy and by dx when 2*err <= dx), rasterize the line from (19,22) to (6,31). Give the full ordered list of pixels from start to end as a compact string of bracketed coordinate pairs, e.g. (0,0)(1,1)(2,2).

**Answer**
(19,22)(18,23)(17,23)(16,24)(15,25)(14,25)(13,26)(12,27)(11,28)(10,28)(9,29)(8,30)(7,30)(6,31)

### Example 2
**Prompt**
Using Bresenham's line algorithm, rasterize the line from (19,19) to (18,5). Counting steps starting at 1 (step 1 is the (19,19) endpoint), which pixel is chosen at step 3? Give the single bracketed pair, e.g. (3,4). If the line has fewer than 3 steps, answer OUT_OF_RANGE.

**Answer**
(19,17)
