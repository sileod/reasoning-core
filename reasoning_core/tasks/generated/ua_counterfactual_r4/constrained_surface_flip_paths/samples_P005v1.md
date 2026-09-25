# Samples: constrained_surface_flip_paths (P005v1)

## Level 0

### Example 1

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..9 in order and the following internal triangles.
> Triangles: [[0, 1, 2], [0, 2, 7], [0, 7, 8], [0, 8, 9], [2, 3, 5], [2, 5, 7], [3, 4, 5], [5, 6, 7]]
> Marked edges (must never be flipped): []
> Forbidden edges (may never be created): []
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 2-7;2-5;5-7;3-5

### Example 2

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..9 in order and the following internal triangles.
> Triangles: [[0, 1, 2], [0, 2, 6], [0, 6, 7], [0, 7, 9], [2, 3, 4], [2, 4, 5], [2, 5, 6], [7, 8, 9]]
> Marked edges (must never be flipped): []
> Forbidden edges (may never be created): []
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 2-6;2-5;2-4;7-9

## Level 2

### Example 1

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..11 in order and the following internal triangles.
> Triangles: [[0, 1, 7], [0, 7, 9], [0, 9, 10], [0, 10, 11], [1, 2, 7], [2, 3, 4], [2, 4, 5], [2, 5, 6], [2, 6, 7], [7, 8, 9]]
> Marked edges (must never be flipped): [[0, 7], [0, 10]]
> Forbidden edges (may never be created): [[4, 7], [7, 11]]
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9], [0, 9, 10], [0, 10, 11]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 1-7;7-9;2-7;2-6;2-5;2-4

### Example 2

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..11 in order and the following internal triangles.
> Triangles: [[0, 1, 6], [0, 6, 8], [0, 8, 9], [0, 9, 11], [1, 2, 6], [2, 3, 4], [2, 4, 5], [2, 5, 6], [6, 7, 8], [9, 10, 11]]
> Marked edges (must never be flipped): [[0, 6], [0, 9]]
> Forbidden edges (may never be created): [[3, 7], [6, 9]]
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9], [0, 9, 10], [0, 10, 11]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 1-6;6-8;2-6;9-11;2-5;2-4

## Level 5

### Example 1

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..14 in order and the following internal triangles.
> Triangles: [[0, 1, 2], [0, 2, 8], [0, 8, 9], [0, 9, 10], [0, 10, 11], [0, 11, 12], [0, 12, 14], [2, 3, 8], [3, 4, 8], [4, 5, 8], [5, 6, 8], [6, 7, 8], [12, 13, 14]]
> Marked edges (must never be flipped): [[0, 2], [0, 8], [0, 9], [0, 10], [0, 12]]
> Forbidden edges (may never be created): [[1, 6], [7, 10], [9, 12], [10, 12], [10, 14]]
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9], [0, 9, 10], [0, 10, 11], [0, 11, 12], [0, 12, 13], [0, 13, 14]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 12-14;2-8;3-8;4-8;5-8;6-8

### Example 2

**Prompt:**

> A triangulated disk has boundary vertices numbered 0..14 in order and the following internal triangles.
> Triangles: [[0, 1, 4], [0, 4, 5], [0, 5, 10], [0, 10, 11], [0, 11, 13], [0, 13, 14], [1, 2, 3], [1, 3, 4], [5, 6, 7], [5, 7, 8], [5, 8, 10], [8, 9, 10], [11, 12, 13]]
> Marked edges (must never be flipped): [[0, 4], [0, 5], [0, 10], [0, 11], [0, 13]]
> Forbidden edges (may never be created): [[2, 4], [2, 10], [3, 5], [4, 9], [6, 12]]
> A legal flip replaces the shared diagonal of two adjacent triangles with the other diagonal of their quadrilateral, without flipping a marked edge, creating a forbidden edge, or raising any vertex degree beyond the allowed maximum.
> Return the shortest such flip sequence that reconfigures these triangles into the target triangulation: [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 7, 8], [0, 8, 9], [0, 9, 10], [0, 10, 11], [0, 11, 12], [0, 12, 13], [0, 13, 14]]
> The answer is a ';'-separated list of edge identifiers a-b with a<b, for example '0-3;1-4'.

**Answer:**

> 11-13;1-4;5-10;1-3;5-8;5-7;8-10
