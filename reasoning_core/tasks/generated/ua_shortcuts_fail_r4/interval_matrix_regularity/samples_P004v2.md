## Level 0

**Example 1**


**Prompt:**

Consider 2×2 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [1, 5]
Matrix: [3, u0] ; [3, 4]
Every interval above has radius 2. At a smaller integer radius r with 0 ≤ r ≤ 2 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 2 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** singular_at_1


**Example 2**


**Prompt:**

Consider 2×2 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [1, 3]
u1 ∈ [-1, 1]
Matrix: [24, u0] ; [u1, 24]
Every interval above has radius 1. At a smaller integer radius r with 0 ≤ r ≤ 1 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 1 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** regular


## Level 2

**Example 1**


**Prompt:**

Consider 2×2 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [-5, 1]
u1 ∈ [-3, 3]
Matrix: [23, u0] ; [u1, 23]
Every interval above has radius 3. At a smaller integer radius r with 0 ≤ r ≤ 3 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 3 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** regular


**Example 2**


**Prompt:**

Consider 2×2 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [6, 8]
Matrix: [4, u0] ; [2, 3]
Every interval above has radius 1. At a smaller integer radius r with 0 ≤ r ≤ 1 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 1 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** singular_at_1


## Level 5

**Example 1**


**Prompt:**

Consider 3×3 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [1, 3]
Matrix: [3, u0, 0] ; [1, 1, 0] ; [0, 0, 1]
Every interval above has radius 1. At a smaller integer radius r with 0 ≤ r ≤ 1 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 1 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** singular_at_1


**Example 2**


**Prompt:**

Consider 3×3 integer matrices. A cell shown as a fixed integer is a constant. A cell labelled u_j may take any integer value in that u_j's interval, and any two cells carrying the same label u_j must take the same value (they are shared).
u0 ∈ [5, 9]
Matrix: [5, u0, 0] ; [1, 1, 0] ; [0, 0, 1]
Every interval above has radius 2. At a smaller integer radius r with 0 ≤ r ≤ 2 the same matrix instead restricts each u_j to [c_j − r, c_j + r] (integers).
If, for the full intervals above, every choice of the u_j yields a matrix with nonzero determinant, answer exactly: regular. Otherwise find the smallest integer radius r with 0 ≤ r ≤ 2 at which that restricted box first admits a singular matrix, and answer exactly: singular_at_r (for example singular_at_2).


**Answer:** singular_at_2

