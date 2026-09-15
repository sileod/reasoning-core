# Samples for rotation_system_face_tracing (P011v1)

## Level 0

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 3. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 2 1 3
vertex 1: 2 0
vertex 2: 1 0 3
vertex 3: 2 0
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

3 3 4

---

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 3. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 2 3 1
vertex 1: 2 3 0
vertex 2: 1 0 3
vertex 3: 1 0 2
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

4 8

---

## Level 2

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 5. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 2 3 4
vertex 1: 2 4 3 5
vertex 2: 0 3 1
vertex 3: 4 1 5 2 0
vertex 4: 1 0 3 5
vertex 5: 1 3 4
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

4 6 12

---

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 5. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 1 3
vertex 1: 4 3 0
vertex 2: 4
vertex 3: 0 4 1
vertex 4: 3 1 2 5
vertex 5: 4
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

14

---

## Level 5

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 8. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 6 8 3 2
vertex 1: 8 6 3
vertex 2: 3 0
vertex 3: 2 0 5 1
vertex 4: 7 6
vertex 5: 8 3
vertex 6: 4 1 0
vertex 7: 4
vertex 8: 1 5 0
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

3 4 4 4 9

---

### Prompt

A graph is embedded on the plane with vertices labeled 0 through 8. For every vertex, its neighbors are listed in counterclockwise cyclic order as they appear around that vertex. There are no loops or parallel edges.
vertex 0: 7 3
vertex 1: 4 7
vertex 2: 5
vertex 3: 8 0 4 7 6
vertex 4: 1 3
vertex 5: 8 2
vertex 6: 8 3
vertex 7: 1 3 8 0
vertex 8: 6 5 7 3
Enumerate every face of this embedding. A face is bounded by a closed walk found by the next-edge rule: start from any directed dart (u,v), then after reaching v leave along the neighbor that comes immediately after u in v's cyclic neighbor list, continuing until the dart repeats. Include the outer face. A bridge edge is traversed in both directions and bounds a face of length 2.
Report the lengths of all faces as a single list separated by single spaces, in nondecreasing order. Example: if the face lengths are {3, 4, 3} the answer is: 3 3 4

Answer

3 8 13

---
