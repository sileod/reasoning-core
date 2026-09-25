## Level 0

### Example 1

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[((o))] = 1
A[(o)] = -1
A[(oo)] = 1
A[o] = -1

Series B:
B[((o))] = 0
B[(o)] = -1
B[(oo)] = 0
B[o] = 1

Query tree Q = (o).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: -2

### Example 2

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[((o))] = -1
A[(o)] = 1
A[(oo)] = -1
A[o] = 1

Series B:
B[((o))] = -1
B[(o)] = 0
B[(oo)] = 0
B[o] = 1

Query tree Q = (o).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: 2

## Level 2

### Example 1

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[((((o))))] = -3
A[(((o)))] = -3
A[(((o))o)] = 3
A[(((o)o))] = 0
A[(((oo)))] = -2
A[((o)(o))] = 0
A[((o))] = -2
A[((o)o)] = -2
A[((o)oo)] = -3
A[((oo))] = -1
A[((oo)o)] = 0
A[((ooo))] = 1
A[(o)] = 3
A[(oo)] = 1
A[(ooo)] = -3
A[(oooo)] = 1
A[o] = -3

Series B:
B[((((o))))] = -2
B[(((o)))] = 1
B[(((o))o)] = -1
B[(((o)o))] = -1
B[(((oo)))] = 3
B[((o)(o))] = 3
B[((o))] = -3
B[((o)o)] = 2
B[((o)oo)] = -1
B[((oo))] = -2
B[((oo)o)] = -2
B[((ooo))] = 1
B[(o)] = 0
B[(oo)] = 3
B[(ooo)] = -1
B[(oooo)] = -1
B[o] = 3

Query tree Q = (oo).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: -7/2

### Example 2

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[((((o))))] = 3
A[(((o)))] = 3
A[(((o))o)] = -3
A[(((o)o))] = -1
A[(((oo)))] = 0
A[((o)(o))] = 2
A[((o))] = 1
A[((o)o)] = 0
A[((o)oo)] = 1
A[((oo))] = -3
A[((oo)o)] = 0
A[((ooo))] = 0
A[(o)] = -1
A[(oo)] = 2
A[(ooo)] = -3
A[(oooo)] = 1
A[o] = 3

Series B:
B[((((o))))] = 0
B[(((o)))] = 2
B[(((o))o)] = -1
B[(((o)o))] = 0
B[(((oo)))] = -2
B[((o)(o))] = 0
B[((o))] = -1
B[((o)o)] = 1
B[((o)oo)] = 0
B[((oo))] = 0
B[((oo)o)] = 1
B[((ooo))] = -3
B[(o)] = 0
B[(oo)] = -2
B[(ooo)] = 2
B[(oooo)] = 3
B[o] = -1

Query tree Q = ((o)o).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: -7/2

## Level 5

### Example 1

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[(((((o)))))] = -1
A[((((o))))] = 0
A[((((o)))o)] = 2
A[((((o))o))] = 2
A[((((o)o)))] = 5
A[((((oo))))] = 3
A[(((o)(o)))] = 5
A[(((o))(o))] = 3
A[(((o)))] = 4
A[(((o))o)] = -3
A[(((o))oo)] = 1
A[(((o)o))] = -5
A[(((o)o)o)] = -4
A[(((o)oo))] = 4
A[(((oo)))] = 2
A[(((oo))o)] = 6
A[(((oo)o))] = -5
A[(((ooo)))] = 0
A[((o)(o))] = 0
A[((o)(o)o)] = 1
A[((o)(oo))] = 1
A[((o))] = 1
A[((o)o)] = -4
A[((o)oo)] = 2
A[((o)ooo)] = -3
A[((oo))] = -5
A[((oo)o)] = -4
A[((oo)oo)] = 6
A[((ooo))] = 0
A[((ooo)o)] = -5
A[((oooo))] = -3
A[(o)] = 0
A[(oo)] = -2
A[(ooo)] = -2
A[(oooo)] = -5
A[(ooooo)] = -2
A[o] = -2

Series B:
B[(((((o)))))] = -3
B[((((o))))] = 0
B[((((o)))o)] = 2
B[((((o))o))] = -4
B[((((o)o)))] = -1
B[((((oo))))] = 2
B[(((o)(o)))] = 3
B[(((o))(o))] = 3
B[(((o)))] = -5
B[(((o))o)] = 2
B[(((o))oo)] = -5
B[(((o)o))] = -1
B[(((o)o)o)] = 1
B[(((o)oo))] = 4
B[(((oo)))] = -5
B[(((oo))o)] = 0
B[(((oo)o))] = -5
B[(((ooo)))] = -1
B[((o)(o))] = 6
B[((o)(o)o)] = -6
B[((o)(oo))] = -5
B[((o))] = 4
B[((o)o)] = -5
B[((o)oo)] = 1
B[((o)ooo)] = -4
B[((oo))] = 1
B[((oo)o)] = -4
B[((oo)oo)] = -2
B[((ooo))] = 2
B[((ooo)o)] = -1
B[((oooo))] = 1
B[(o)] = 4
B[(oo)] = -3
B[(ooo)] = 4
B[(oooo)] = -1
B[(ooooo)] = -2
B[o] = -5

Query tree Q = (oooo).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: -865/12

### Example 2

We use rooted trees with unlabeled nodes and unordered children, encoded canonically: a leaf is `o`, and a node whose children have encodings c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and a root with three leaf children is `(ooo)`.

A tree series assigns an integer coefficient to each finite rooted tree. Given two integer tree series A and B, the coefficient (A∘B)[T] of their composition on a tree T is the sum, over every admissible cut of T, of the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). An admissible cut chooses a set of edges no two of which lie on a common root-to-leaf path; it splits T into a pruned tree P (the part containing the root) and a forest F of the remaining rooted trees. aut(F) is the product, over each distinct child-tree appearing m times in F, of m! (the automorphism factor of the unordered forest). The empty cut (choose no edges) is included.

Series A:
A[(((((o)))))] = -1
A[((((o))))] = -5
A[((((o)))o)] = -6
A[((((o))o))] = 5
A[((((o)o)))] = 1
A[((((oo))))] = -5
A[(((o)(o)))] = 2
A[(((o))(o))] = -2
A[(((o)))] = 6
A[(((o))o)] = -1
A[(((o))oo)] = -2
A[(((o)o))] = 1
A[(((o)o)o)] = -5
A[(((o)oo))] = 2
A[(((oo)))] = -6
A[(((oo))o)] = -6
A[(((oo)o))] = -4
A[(((ooo)))] = 4
A[((o)(o))] = -6
A[((o)(o)o)] = -4
A[((o)(oo))] = -4
A[((o))] = 1
A[((o)o)] = 2
A[((o)oo)] = -4
A[((o)ooo)] = -1
A[((oo))] = -6
A[((oo)o)] = 1
A[((oo)oo)] = 2
A[((ooo))] = 0
A[((ooo)o)] = 4
A[((oooo))] = -6
A[(o)] = 6
A[(oo)] = 5
A[(ooo)] = -3
A[(oooo)] = 4
A[(ooooo)] = 1
A[o] = 0

Series B:
B[(((((o)))))] = 5
B[((((o))))] = -3
B[((((o)))o)] = 5
B[((((o))o))] = 3
B[((((o)o)))] = 4
B[((((oo))))] = -1
B[(((o)(o)))] = 4
B[(((o))(o))] = 0
B[(((o)))] = 5
B[(((o))o)] = 2
B[(((o))oo)] = 4
B[(((o)o))] = 0
B[(((o)o)o)] = 4
B[(((o)oo))] = -3
B[(((oo)))] = -3
B[(((oo))o)] = 5
B[(((oo)o))] = 4
B[(((ooo)))] = -1
B[((o)(o))] = 1
B[((o)(o)o)] = 6
B[((o)(oo))] = -5
B[((o))] = -4
B[((o)o)] = 5
B[((o)oo)] = -3
B[((o)ooo)] = 2
B[((oo))] = 2
B[((oo)o)] = -1
B[((oo)oo)] = -5
B[((ooo))] = -1
B[((ooo)o)] = -5
B[((oooo))] = -4
B[(o)] = 6
B[(oo)] = 6
B[(ooo)] = -3
B[(oooo)] = -2
B[(ooooo)] = -1
B[o] = 5

Query tree Q = (((o)o)).
Compute (A∘B)[Q]. Give the answer as a reduced fraction p/q, or as a plain integer p when it is integral (e.g. -13/6 or 7).

Answer: 399/2
