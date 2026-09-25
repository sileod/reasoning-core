# Samples for material_frame_equivalence (P002v1)

## Level 0

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (0, -1).
  O2 has velocity (1, 0).
  O3 has velocity (0, -1).
Chain A applies the following maps in order:
  T(-1,-1) · id · T(-1,1) · r180
Chain B applies the following maps in order:
  d · T(-1,-1) · m_y
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** No

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (0, -1).
  O2 has velocity (-1, 1).
  O3 has velocity (0, -1).
Chain A applies the following maps in order:
  T(-1,0) · m_y · id
Chain B applies the following maps in order:
  m_x · T(0,1) · id
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** No


## Level 2

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (-2, 2).
  O2 has velocity (1, 2).
  O3 has velocity (2, -2).
  O4 has velocity (-2, 0).
  O5 has velocity (-1, 2).
Chain A applies the following maps in order:
  T(-2,-1) · m_y · r180 · id · T(-1,1) · a
Chain B applies the following maps in order:
  m_y · T(-2,1) · m_x · T(2,1) · d · id
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** No

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (-1, -1).
  O2 has velocity (0, 1).
  O3 has velocity (1, 2).
  O4 has velocity (1, 2).
  O5 has velocity (-1, -2).
Chain A applies the following maps in order:
  T(-2,-1) · a · r270 · id · T(-2,0) · r270
Chain B applies the following maps in order:
  T(1,-2) · r180 · r270 · T(0,1) · d · r90
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** Yes


## Level 5

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (2, 0).
  O2 has velocity (2, -1).
  O3 has velocity (3, -2).
  O4 has velocity (-2, 2).
  O5 has velocity (-1, -4).
  O6 has velocity (-2, -3).
  O7 has velocity (-1, 1).
  O8 has velocity (4, -4).
Chain A applies the following maps in order:
  T(4,-1) · m_y · T(-4,4) · r90 · T(3,1) · r180 · T(0,3) · m_y · T(0,-1) · m_y · a · m_y
Chain B applies the following maps in order:
  T(-4,-4) · r90 · d · r270 · T(4,-1) · r90 · a · r180 · id
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** No

**Prompt:**

The material points below move with constant velocities. A linear map applied to a velocity vector rotates or reflects it, while a translation T(dx,dy) only shifts an object's position and leaves its velocity unchanged.
Points:
  O1 has velocity (1, 2).
  O2 has velocity (-1, -2).
  O3 has velocity (1, -4).
  O4 has velocity (1, -4).
  O5 has velocity (3, -2).
  O6 has velocity (1, -4).
  O7 has velocity (-1, -1).
  O8 has velocity (0, -4).
Chain A applies the following maps in order:
  T(-4,3) · m_y · T(3,3) · id · T(-1,-4) · a · r270 · d · T(0,-1) · id · T(1,-1) · m_y
Chain B applies the following maps in order:
  T(4,4) · id · T(-4,4) · id · T(3,-1) · id · T(4,-1) · r270 · d · T(1,-1) · r270 · m_x
Here r90/r180/r270 rotate counterclockwise by 90/180/270 degrees and m_x, m_y, d, a reflect across the x-axis, y-axis, line y=x and line y=-x respectively.
Do chains A and B produce the identical velocity field at all material points? Answer exactly 'Yes' or 'No'.

**Answer:** No
