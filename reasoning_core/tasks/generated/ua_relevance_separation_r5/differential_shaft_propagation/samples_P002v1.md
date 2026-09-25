## Level 0

**Prompt:**
A gear train has 3 shafts numbered 0..2. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an internal ring mesh (teeth 24:72) drives shaft 2 from shaft 0, same direction
an external gear mesh (teeth 48:15) drives shaft 1 from shaft 2, reversing direction
Give the signed rotation of shaft 1, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
-16/15


**Prompt:**
A gear train has 3 shafts numbered 0..2. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an external gear mesh (teeth 24:18) drives shaft 2 from shaft 0, reversing direction
an external gear mesh (teeth 20:30) drives shaft 1 from shaft 2, reversing direction
Give the signed rotation of shaft 2, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
-4/3

## Level 2

**Prompt:**
A gear train has 5 shafts numbered 0..4. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an external gear mesh (teeth 36:15) drives shaft 4 from shaft 0, reversing direction
shaft 3 is rigidly shared with shaft 0 (same rotation)
an external gear mesh (teeth 30:18) drives shaft 1 from shaft 4, reversing direction
an external gear mesh (teeth 30:30) drives shaft 2 from shaft 1, reversing direction
Give the signed rotation of shaft 1, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
4


**Prompt:**
A gear train has 5 shafts numbered 0..4. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an external gear mesh (teeth 60:24) drives shaft 3 from shaft 0, reversing direction
an external gear mesh (teeth 30:24) drives shaft 1 from shaft 3, reversing direction
shaft 4 is rigidly shared with shaft 0 (same rotation)
shaft 2 is rigidly shared with shaft 4 (same rotation)
Give the signed rotation of shaft 1, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
25/8

## Level 5

**Prompt:**
A gear train has 9 shafts numbered 0..8. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an external gear mesh (teeth 30:18) drives shaft 7 from shaft 0, reversing direction
an internal ring mesh (teeth 20:60) drives shaft 1 from shaft 0, same direction
shaft 4 is rigidly shared with shaft 7 (same rotation)
an external gear mesh (teeth 20:18) drives shaft 3 from shaft 4, reversing direction
an external gear mesh (teeth 36:15) drives shaft 5 from shaft 4, reversing direction
an internal ring mesh (teeth 36:90) drives shaft 2 from shaft 4, same direction
an external gear mesh (teeth 24:36) drives shaft 8 from shaft 4, reversing direction
an external gear mesh (teeth 24:36) drives shaft 6 from shaft 2, reversing direction
Give the signed rotation of shaft 2, 7, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
-2/3, -5/3


**Prompt:**
A gear train has 9 shafts numbered 0..8. Shaft 0 is driven at exactly one counterclockwise turn. For a mesh that reverses direction, rotation_b = -(A/B)*rotation_a; an internal same-direction mesh gives rotation_b = +(A/B)*rotation_a; a shared shaft gives equal rotation. Closed loops are feasible only if every implied rotation agrees. Connections:
an internal ring mesh (teeth 24:48) drives shaft 2 from shaft 0, same direction
an external gear mesh (teeth 20:18) drives shaft 1 from shaft 0, reversing direction
an external gear mesh (teeth 20:15) drives shaft 7 from shaft 2, reversing direction
an external gear mesh (teeth 20:36) drives shaft 5 from shaft 1, reversing direction
an external gear mesh (teeth 24:24) drives shaft 6 from shaft 7, reversing direction
an external gear mesh (teeth 60:24) drives shaft 8 from shaft 2, reversing direction
an internal ring mesh (teeth 20:48) drives shaft 3 from shaft 5, same direction
an external gear mesh (teeth 20:36) drives shaft 4 from shaft 8, reversing direction
Give the signed rotation of shaft 3, 5, each as a reduced fraction (a plain integer such as 1 or -3 is allowed), or exactly the word LOCKED if no consistent rotation exists.

**Answer:**
125/486, 50/81

