## Level 0

### Example 1

**Prompt**

Let the coordinates (u, v) and (x, y) be related by the coordinate change x = -2*u + 3*v, y = 2*u + v (each expression is a linear form in the (u, v) coordinates).

Consider the differential 1-form on the (x, y) coordinates
ω = -3*dx,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du, dv with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

6*du - 9*dv


## Level 0

### Example 2

**Prompt**

Let the coordinates (u, v) and (x, y) be related by the coordinate change x = 3*u - 3*v, y = -3*u + 3*v (each expression is a linear form in the (u, v) coordinates).

Consider the differential 1-form on the (x, y) coordinates
ω = 1*dx,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du, dv with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

3*du - 3*dv


## Level 2

### Example 1

**Prompt**

Let the coordinates (u, v, w) and (x, y) be related by the coordinate change x = -u/2 + v + 3*w/2 + 5/3, y = -u/3 + 3*v + 4*w (each expression is a linear form in the (u, v, w) coordinates).

Consider the differential 1-form on the (x, y) coordinates
ω = -4*dx - 1*dy,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v, w) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du, dv, dw with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

7/3*du - 7*dv - 10*dw


## Level 2

### Example 2

**Prompt**

Let the coordinates (u, v) and (x, y) be related by the coordinate change x = -3*u + 3*v/2 + 1/3, y = -5*u/2 + 3*v + 1 (each expression is a linear form in the (u, v) coordinates).

Consider the differential 2-form on the (x, y) coordinates
ω = -4*dx^dy,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du^dv with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

21*du^dv


## Level 5

### Example 1

**Prompt**

Let the coordinates (x, y, z) be related to auxiliary coordinates (a, b) by x = 2*a - 7*b - 5, y = a/2 + 3*b/2 + 1, z = 5*a - 5*b/3 + 1, and (a, b) be related to (u, v) by a = u/2 - 3*v - 5, b = -u - v (each expression is linear in the coordinates on its right).

Consider the differential 2-form on the (x, y, z) coordinates
ω = 5*dx^dy + 7*dx^dz + 4*dy^dz,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du^dv with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

-9275/12*du^dv


## Level 5

### Example 2

**Prompt**

Let the coordinates (x, y) be related to auxiliary coordinates (a) by x = -5*a, y = a, and (a) be related to (u, v) by a = u - 3*v (each expression is linear in the coordinates on its right).

Consider the differential 1-form on the (x, y) coordinates
ω = -2*dy - 6*dx,
where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge product. Compute the pullback of ω through the composition of these coordinate maps back to the (u, v) coordinates, expanding every differential through the Jacobian substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products (du^du = 0, du^dv = -dv^du).

Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the basis wedges are chosen from du, dv with the coordinates in each wedge in ascending lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions (integers when whole) and negative terms following a ` - ` sign, and every zero term omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.

Pullback of ω:

**Answer**

28*du - 84*dv

