# P011v1 ribbon_surface_surgery samples

## Level 0

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,3 (cycle)
  vertex 1: 1,5 (cycle)
  vertex 2: 2,4 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5)
Operations applied in order:
  1. con(0): contract the edge with sides 0 and 1
  2. band_attach(4,5): new edge with new half-edges 6 after 4 and 7 after 5
  3. band_attach(2,3): new edge with new half-edges 8 after 2 and 9 after 3
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[2,9,4,7,3,8,5,6];g=1
```

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,5 (cycle)
  vertex 1: 1,2 (cycle)
  vertex 3: 3,4 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5)
Operations applied in order:
  1. con(2): contract the edge with sides 2 and 3
  2. con(0): contract the edge with sides 0 and 1
  3. band_attach(5,4): new edge with new half-edges 6 after 5 and 7 after 4
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[4,6,5,7];g=1
```

## Level 2

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,5 (cycle)
  vertex 1: 1,2 (cycle)
  vertex 3: 3,7 (cycle)
  vertex 4: 4,9 (cycle)
  vertex 6: 6,8 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5,6-7,8-9)
Operations applied in order:
  1. split_vertex(5, k=1): split the vertex containing half-edge 5; new half-edges 10 and 11 open the two segments
  2. band_attach(6,3): new edge with new half-edges 12 after 6 and 13 after 3
  3. del(12): delete the edge whose one side is half-edge 12 
  4. band_attach(0,2): new edge with new half-edges 14 after 0 and 15 after 2
  5. split_vertex(9, k=1): split the vertex containing half-edge 9; new half-edges 16 and 17 open the two segments
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[0,15,1,3,6,9,17,5,11,2,14,10,4,16,8,7];g=0
```

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,5 (cycle)
  vertex 1: 1,7 (cycle)
  vertex 2: 2,6 (cycle)
  vertex 3: 3,9 (cycle)
  vertex 4: 4,8 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5,6-7,8-9)
Operations applied in order:
  1. band_attach(9,3): new edge with new half-edges 10 after 9 and 11 after 3
  2. band_attach(10,5): new edge with new half-edges 12 after 10 and 13 after 5
  3. split_vertex(6, k=1): split the vertex containing half-edge 6; new half-edges 14 and 15 open the two segments
  4. band_attach(8,14): new edge with new half-edges 16 after 8 and 17 after 14
  5. split_vertex(10, k=3): split the vertex containing half-edge 10; new half-edges 18 and 19 open the two segments
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[0,4,9,18,11,8,17,7,1,6,15,3,10,13,2,14,16,5,12,19];g=1
```

## Level 5

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,7 (cycle)
  vertex 1: 1,5 (cycle)
  vertex 2: 2,13 (cycle)
  vertex 3: 3,6 (cycle)
  vertex 4: 4,15 (cycle)
  vertex 8: 8,10 (cycle)
  vertex 9: 9,12 (cycle)
  vertex 11: 11,14 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5,6-7,8-9,10-11,12-13,14-15)
Operations applied in order:
  1. con(4): contract the edge with sides 4 and 5
  2. band_attach(15,8): new edge with new half-edges 16 after 15 and 17 after 8
  3. con(6): contract the edge with sides 6 and 7
  4. del(12): delete the edge whose one side is half-edge 12 
  5. del(2): delete the edge whose one side is half-edge 2 
  6. band_attach(16,0): new edge with new half-edges 18 after 16 and 19 after 0
  7. del(8): delete the edge whose one side is half-edge 8 
  8. split_vertex(14, k=1): split the vertex containing half-edge 14; new half-edges 20 and 21 open the two segments
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[0,18,1,14,21,10,16,19,11,20,15,17];g=0
```

### Prompt

```
We model an oriented ribbon surface (fat graph / band decomposition) by its half-edges. Every half-edge has an integer label. Each edge glues two half-edges together as a mate-pair. At each vertex the half-edges are arranged in a counter-clockwise cyclic order; the rotation cycle of a vertex lists them in that order.
The boundary of the surface is read by walking: from a half-edge d, move to its successor s in d's rotation cycle, then jump across the edge to s's mate, then repeat. Each closed walk so obtained is one boundary component, and the half-edge labels in traversal order form that component's list.
The genus is the usual oriented-surface genus of the resulting ribbon surface, determined by its final rotation cycles and mate-pairs through Euler's formula.
Operations (each rule stated once, applied in the listed order): band_attach(a,b) makes a new edge whose two new half-edges n1 and n2 are inserted immediately after half-edge a and immediately after half-edge b in their rotation cycles, and n1,n2 are mates of each other. del(x) deletes the edge whose one side is half-edge x (x and its mate are removed) and splices the two affected rotation cycles so each removed half-edge's counter-clockwise predecessor now points to its successor. con(x) contracts the edge with sides x and x'=mate(x), at distinct vertices U and W; with a=successor(x) in U and b=successor(x') in W, the two vertices merge into one whose rotation joins the two cycles so that b follows the counter-clockwise predecessor of x and a follows that of x'. split_vertex(c,k) cuts vertex V, whose rotation is linearized starting from its smallest half-edge label, at the k-th smallest label c; new half-edge n1 opens the vertex that receives the counter-clockwise segment starting at c (back to just before c), new half-edge n2 opens the vertex that receives the remaining earlier segment, and n1,n2 are mates of the new edge.
Initial rotation cycles (vertex id = smallest half-edge label):
  vertex 0: 0,5 (cycle)
  vertex 1: 1,7 (cycle)
  vertex 2: 2,9 (cycle)
  vertex 3: 3,4 (cycle)
  vertex 6: 6,15 (cycle)
  vertex 8: 8,10 (cycle)
  vertex 11: 11,12 (cycle)
  vertex 13: 13,14 (cycle)
Initial mate-pairs of edges: (0-1,2-3,4-5,6-7,8-9,10-11,12-13,14-15)
Operations applied in order:
  1. split_vertex(5, k=1): split the vertex containing half-edge 5; new half-edges 16 and 17 open the two segments
  2. split_vertex(10, k=1): split the vertex containing half-edge 10; new half-edges 18 and 19 open the two segments
  3. split_vertex(17, k=1): split the vertex containing half-edge 17; new half-edges 20 and 21 open the two segments
  4. del(8): delete the edge whose one side is half-edge 8 
  5. split_vertex(15, k=1): split the vertex containing half-edge 15; new half-edges 22 and 23 open the two segments
  6. band_attach(15,22): new edge with new half-edges 24 after 15 and 25 after 22
  7. del(24): delete the edge whose one side is half-edge 24 
  8. con(4): contract the edge with sides 4 and 5
Give the final boundary components as a list of half-edge labels in traversal order (start each component at its smallest label; order the components by increasing smallest label), and the genus, as a single line in the format: B=[label1,label2,...];g=GENUS
```

### Answer

```
B=[0,20,16,2,3,17,21,1,6,22,14,12,10,19,18,11,13,15,23,7];g=0
```
