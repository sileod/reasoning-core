## Level 0
### Example 1
**Prompt:**

Given the planar points 3,-5;-1,-2;-7,1;4,6;5,3;3,-4;8,-8;0,-5. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

0,-5;8,-8;5,3;4,6;-7,1

### Example 2
**Prompt:**

Given the planar points -9,2;-6,8;3,-3;0,9;1,-2;-8,5;10,3;1,9. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

-9,2;3,-3;10,3;1,9;0,9;-6,8;-8,5

## Level 2
### Example 1
**Prompt:**

Given the planar points 14,-15;-14,-18;-14,4;8,7;-14,-3;-17,-17;-3,-16;3,-6;9,2;-8,-5;-6,-13;14,10;11,18;0,14. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

-17,-17;-14,-18;14,-15;14,10;11,18;0,14;-14,4

### Example 2
**Prompt:**

Given the planar points 7,4;11,-3;-7,14;-18,-18;-12,-7;18,0;8,-3;-13,10;-13,3;-4,2;3,-17;4,-18;-6,-7;-12,-15. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

-18,-18;4,-18;18,0;-7,14;-13,10

## Level 5
### Example 1
**Prompt:**

Given the planar points -9,-22;27,-1;-6,4;0,-7;21,28;2,-7;-1,-23;16,-5;-11,-5;-2,10;29,19;26,-26;9,-2;4,14;23,30;28,23;-1,3;7,21;-15,24;-19,5;6,-24;-20,-6;13,12. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

-20,-6;-9,-22;6,-24;26,-26;29,19;28,23;23,30;-15,24;-19,5

### Example 2
**Prompt:**

Given the planar points -15,29;14,22;-14,15;2,8;26,8;11,29;-29,11;-8,-9;11,-1;-26,-18;-9,-2;-27,23;5,27;-29,-14;5,-25;5,-10;-23,-17;-25,-8;-26,30;1,-5;20,-19;-25,-24;7,14. Compute the convex hull (the minimal convex polygon containing all points) using the monotone chain algorithm. Since points may be collinear, keep only the extreme hull vertices (intermediate points lying exactly on an edge are not hull vertices). Return the hull vertices in counterclockwise order starting from the leftmost-lowest vertex, as a compact semicolon-separated list of x,y pairs, e.g. '0,0;2,0;2,1;0,1'. The answer is this exact list.

**Answer:**

-29,-14;-25,-24;5,-25;20,-19;26,8;11,29;-26,30;-29,11
