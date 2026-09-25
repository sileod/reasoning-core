## Level 0

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = 1 and R[A] = -1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient -1.
F[A]: reassociating with outer charge A is the 2x2 matrix [[1, -1], [-2, -2]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 3 A-anyons (a · inside means fused, superscript is the fusion charge) is:
((A ⊗ A)^A ⊗ A)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 1 and 2 (they currently fuse to channel A).
F-move: reassociate the three consecutive leaves 1,2,3 (combined charge 1, present inner channel A), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** 1

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = 1 and R[A] = -1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient 2.
F[A]: reassociating with outer charge A is the 2x2 matrix [[2, -1], [-2, 2]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 3 A-anyons (a · inside means fused, superscript is the fusion charge) is:
((A ⊗ A)^A ⊗ A)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 1 and 2 (they currently fuse to channel A).
F-move: reassociate the three consecutive leaves 1,2,3 (combined charge 1, present inner channel A), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** -2

## Level 2

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = -1 and R[A] = 1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient 2.
F[A]: reassociating with outer charge A is the 2x2 matrix [[1, -1], [1, -2]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 5 A-anyons (a · inside means fused, superscript is the fusion charge) is:
((A ⊗ (A ⊗ A)^A)^1 ⊗ (A ⊗ A)^1)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 2 and 3 (they currently fuse to channel A).
F-move: reassociate the three consecutive leaves 1,2,3 (combined charge 1, present inner channel A), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** 2

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = 1 and R[A] = 1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient -1.
F[A]: reassociating with outer charge A is the 2x2 matrix [[-1, -2], [-1, -2]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 5 A-anyons (a · inside means fused, superscript is the fusion charge) is:
((A ⊗ (A ⊗ A)^A)^1 ⊗ (A ⊗ A)^1)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 2 and 3 (they currently fuse to channel A).
F-move: reassociate the three consecutive leaves 1,2,3 (combined charge 1, present inner channel A), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** -1

## Level 5

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = -1 and R[A] = 1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient -1.
F[A]: reassociating with outer charge A is the 2x2 matrix [[1, -2], [-1, 2]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 8 A-anyons (a · inside means fused, superscript is the fusion charge) is:
(((A ⊗ A)^A ⊗ ((A ⊗ A)^A ⊗ A)^A)^1 ⊗ ((A ⊗ A)^A ⊗ A)^1)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 6 and 7 (they currently fuse to channel A).
F-move: reassociate the three consecutive leaves 3,4,5 (combined charge A, present inner channel A), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** 2

### Example

**Prompt:**

An anyon fusion category has types 1 (vacuum) and A. Fusion follows 1*x = x and A*A = 1 or A.
Braiding an A,A pair is diagonal in its fusion outcome: R[1] = 1 and R[A] = -1.
Reassociation (F) of a 3-anyon subtree flips the grouping ((x*y)*z) <-> (x*(y*z)); its coefficients depend only on the outer charge and the inner channel:
F[1]: reassociating with outer charge 1, inner channel A -> A has coefficient 1.
F[A]: reassociating with outer charge A is the 2x2 matrix [[2, -1], [-2, -1]] indexed by [old inner channel][new inner channel] over (1, A).
The current fusion state of the 8 A-anyons (a · inside means fused, superscript is the fusion charge) is:
(((A ⊗ (A ⊗ (A ⊗ A)^1)^A)^A ⊗ A)^1 ⊗ ((A ⊗ A)^A ⊗ A)^1)^1
Apply the moves in this order: R-move first, then F-move.
R-move: braid the adjacent A-anyons at leaf positions 3 and 4 (they currently fuse to channel 1).
F-move: reassociate the three consecutive leaves 2,3,4 (combined charge A, present inner channel 1), flipping the grouping.
After these moves, what is the amplitude to the configuration where the reassociated inner pair fuses to channel A?
The answer is one integer (the unnormalized amplitude).

**Answer:** -1
