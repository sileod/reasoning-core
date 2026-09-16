# Samples for hyperedge_replacement_derivation (P006v1)

Each example states a hyperedge-replacement grammar (arity, productions), the
start context edges and the addressed nonterminal edges; the answer is the
sorted final edge list after replacing every nonterminal edge in address order.

## Level 0

### Example 1

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 2: an A edge is written A(a0, a1) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 4 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1], internal [i0], edges: (b0, i0, z); (b0, b1, x); (b1, i0, x)

Start graph vertices are 1..3. Context edges:
  (3, 1, z); (1, 2, y)

Replace the nonterminal edges in this address order:
 - A(2, 1)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,2,y);(1,4,x);(2,1,x);(2,4,z);(3,1,z)

### Example 2

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 2: an A edge is written A(a0, a1) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 4 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1], internal [], edges: (b0, b0, z); (b1, b0, y)

Start graph vertices are 1..3. Context edges:
  (3, 2, x); (3, 2, y)

Replace the nonterminal edges in this address order:
 - A(1, 2)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,1,z);(2,1,y);(3,2,x);(3,2,y)

## Level 2

### Example 1

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 2: an A edge is written A(a0, a1) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 6 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1], internal [i0, i1], edges: (b1, i0, y); (b0, i1, x); (i1, i1, x); (i1, i0, z); (i0, i0, y)
P2: boundary [b0, b1], internal [i0], edges: (b0, i0, x); (b0, i0, y); (i0, i0, z); (b0, i0, x)

Start graph vertices are 1..5. Context edges:
  (2, 1, x); (1, 5, x); (1, 3, z); (3, 4, z)

Replace the nonterminal edges in this address order:
 - A(1, 5)
 - A(1, 3)
 - A(1, 4)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,3,z);(1,5,x);(1,6,x);(1,6,x);(1,6,y);(1,8,x);(1,10,x);(2,1,x);(3,4,z);(3,7,y);(4,9,y);(6,6,z);(7,7,y);(8,7,z);(8,8,x);(9,9,y);(10,9,z);(10,10,x)

### Example 2

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 2: an A edge is written A(a0, a1) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 6 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1], internal [i0, i1], edges: (b0, i0, y); (b1, i1, y); (i1, b1, y); (i1, b0, y); (i1, b0, y)
P2: boundary [b0, b1], internal [], edges: (b1, b0, y); (b0, b1, x); (b0, b1, z)

Start graph vertices are 1..5. Context edges:
  (2, 1, y); (3, 1, y); (5, 3, y); (1, 2, x)

Replace the nonterminal edges in this address order:
 - A(2, 5)
 - A(5, 1)
 - A(4, 5)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,2,x);(1,7,y);(2,1,y);(2,5,x);(2,5,z);(3,1,y);(4,8,y);(5,2,y);(5,3,y);(5,6,y);(5,9,y);(7,1,y);(7,5,y);(7,5,y);(9,4,y);(9,4,y);(9,5,y)

## Level 5

### Example 1

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 3: an A edge is written A(a0, a1, a2) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1, b2]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1, a2) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 10 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1, b2], internal [], edges: (b0, b0, x); (b0, b0, z); (b0, b0, x); (b2, b2, z)
P2: boundary [b0, b1, b2], internal [i0, i1], edges: (b1, i0, x); (b0, i1, z); (b1, i0, z); (b0, b1, y); (i1, i1, x); (b0, b0, x)

Start graph vertices are 1..9. Context edges:
  (4, 8, x); (3, 9, y); (8, 7, x); (7, 5, z); (3, 9, y); (9, 1, z); (5, 8, z)

Replace the nonterminal edges in this address order:
 - A(5, 9, 4)
 - A(8, 4, 1)
 - A(5, 2, 4)
 - A(1, 9, 2)
 - A(6, 2, 5)
 - A(6, 4, 3)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,1,x);(1,1,z);(1,9,y);(1,11,z);(2,12,x);(2,12,z);(3,9,y);(3,9,y);(4,4,z);(4,4,z);(4,8,x);(4,14,x);(4,14,z);(5,5,x);(5,5,x);(5,5,x);(5,5,x);(5,5,z);(5,5,z);(5,8,z);(6,2,y);(6,4,y);(6,6,x);(6,6,x);(6,13,z);(6,15,z);(7,5,z);(8,7,x);(8,8,x);(8,8,x);(8,8,z);(9,1,z);(9,10,x);(9,10,z);(11,11,x);(13,13,x);(15,15,x)

### Example 2

**Prompt:**

You have a hyperedge-replacement grammar. Terminal edge labels are drawn from the set {x, y, z}. There is one nonterminal A of arity 3: an A edge is written A(a0, a1, a2) and its tentacles attach at the listed vertices. The boundary of every A-production is [b0, b1, b2]; internal fresh vertices introduced by a replacement are i0, i1, ... in the order listed.

Replacing an A edge A(a0, a1, a2) removes the nonterminal and adds each production edge (u, v, l), substituting boundary b_k by the k-th attachment a_k and internal i_j by a new vertex. New vertices are numbered consecutively starting at 10 across replacements in the address order, and within one replacement in internal-node order. The context edges stay in the final graph.

Productions for A:
P1: boundary [b0, b1, b2], internal [i0, i1], edges: (b2, i0, y); (b2, i1, x); (i0, b1, x); (b2, b2, y); (i0, b1, y); (i0, i1, y)
P2: boundary [b0, b1, b2], internal [], edges: (b0, b2, y); (b1, b0, y); (b1, b1, z); (b0, b1, z)

Start graph vertices are 1..9. Context edges:
  (8, 7, y); (4, 1, x); (7, 8, z); (8, 5, z); (9, 5, z); (4, 8, z); (7, 1, x)

Replace the nonterminal edges in this address order:
 - A(5, 2, 3)
 - A(5, 1, 7)
 - A(4, 5, 6)
 - A(8, 1, 9)
 - A(5, 1, 4)
 - A(5, 9, 1)

Give the final sorted list of all edges (context plus every introduced edge), each as (source, target, label), sorted lexicographically by (source, target, label) and separated by ';'. Source and target are vertex numbers and the label is x, y or z. Example answer format: (1,2,x);(3,3,y); isolate the answer on its own final line.

**Answer:**

(1,1,z);(1,8,y);(3,3,y);(3,10,y);(3,11,x);(4,1,x);(4,4,y);(4,5,z);(4,6,y);(4,8,z);(4,14,y);(4,15,x);(5,1,y);(5,4,y);(5,5,z);(5,9,z);(7,1,x);(7,7,y);(7,8,z);(7,12,y);(7,13,x);(8,1,z);(8,5,z);(8,7,y);(8,9,y);(9,5,y);(9,5,z);(9,9,z);(10,2,x);(10,2,y);(10,11,y);(12,1,x);(12,1,y);(12,13,y);(14,1,x);(14,1,y);(14,15,y)
