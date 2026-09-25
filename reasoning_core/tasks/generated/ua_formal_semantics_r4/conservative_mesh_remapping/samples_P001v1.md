# Samples P001v1: conservative_mesh_remapping

## Level 0

**Prompt:**

A 1D material occupies domain [0, 31] and is divided into old cells:
old cell 0: constant density 1 over [0, 3]
old cell 1: constant density 9 over [3, 17]
old cell 2: constant density 7 over [17, 31]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 3], [3, 31].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 1? Answer only the numeric mass.


**Answer:**

224.0

---

**Prompt:**

A 1D material occupies domain [0, 31] and is divided into old cells:
old cell 0: constant density 5 over [0, 9]
old cell 1: constant density 2 over [9, 18]
old cell 2: constant density 9 over [18, 31]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 28], [28, 31].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 1? Answer only the numeric mass.


**Answer:**

27.0

---

## Level 2

**Prompt:**

A 1D material occupies domain [0, 71] and is divided into old cells:
old cell 0: constant density 6 over [0, 5]
old cell 1: constant density 4 over [5, 6]
old cell 2: constant density 2 over [6, 8]
old cell 3: constant density 10 over [8, 25]
old cell 4: constant density 6 over [25, 49]
old cell 5: constant density 8 over [49, 58]
old cell 6: constant density 3 over [58, 71]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 1], [1, 2], [2, 50], [50, 54], [54, 69], [69, 71].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 2? Answer only the numeric mass.


**Answer:**

348.0

---

**Prompt:**

A 1D material occupies domain [0, 71] and is divided into old cells:
old cell 0: constant density 11 over [0, 2]
old cell 1: constant density 1 over [2, 12]
old cell 2: constant density 11 over [12, 28]
old cell 3: constant density 1 over [28, 30]
old cell 4: constant density 1 over [30, 47]
old cell 5: constant density 8 over [47, 64]
old cell 6: constant density 2 over [64, 71]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 14], [14, 71].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 0? Answer only the numeric mass.


**Answer:**

54.0

---

## Level 5

**Prompt:**

A 1D material occupies domain [0, 131] and is divided into old cells:
old cell 0: constant density 6 over [0, 1]
old cell 1: constant density 10 over [1, 7]
old cell 2: constant density 8 over [7, 15]
old cell 3: constant density 5 over [15, 31]
old cell 4: constant density 14 over [31, 48]
old cell 5: constant density 1 over [48, 67]
old cell 6: constant density 12 over [67, 75]
old cell 7: constant density 1 over [75, 87]
old cell 8: constant density 7 over [87, 102]
old cell 9: constant density 8 over [102, 104]
old cell 10: constant density 4 over [104, 117]
old cell 11: constant density 13 over [117, 125]
old cell 12: constant density 10 over [125, 131]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 4], [4, 13], [13, 15], [15, 58], [58, 61], [61, 68], [68, 70], [70, 76], [76, 80], [80, 101], [101, 113], [113, 128], [128, 131].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 0? Answer only the numeric mass.


**Answer:**

36.0

---

**Prompt:**

A 1D material occupies domain [0, 131] and is divided into old cells:
old cell 0: constant density 14 over [0, 20]
old cell 1: constant density 2 over [20, 27]
old cell 2: constant density 6 over [27, 53]
old cell 3: constant density 9 over [53, 64]
old cell 4: constant density 3 over [64, 77]
old cell 5: constant density 9 over [77, 90]
old cell 6: constant density 4 over [90, 92]
old cell 7: constant density 14 over [92, 96]
old cell 8: constant density 8 over [96, 101]
old cell 9: constant density 13 over [101, 105]
old cell 10: constant density 2 over [105, 111]
old cell 11: constant density 3 over [111, 125]
old cell 12: constant density 8 over [125, 131]
The mesh is conservatively remapped (mass must be preserved) onto new cells with intervals [0, 17], [17, 80], [80, 131].
For each new cell the mass is the integral of old density over the overlap with old cells; with piecewise constant density that is sum of (overlap width x old density).
What is the mass of the new cell at index 0? Answer only the numeric mass.


**Answer:**

238.0

---

