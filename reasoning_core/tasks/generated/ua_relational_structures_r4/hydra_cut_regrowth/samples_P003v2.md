# Level 0

## Example 1

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: (((h h h) (h h h)))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 3.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 14

## Example 2

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: (((h h h)) (h h) (h h h))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 3.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 7

# Level 2

## Example 1

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: ((((h h h) (h h h h) h) (h h) ((h)) (h h)) ((h) h (h h h h) (h h h)))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 4, 3.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 55

## Example 2

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: ((((h h) (h h) (h h h) h) h h))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 4, 2.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 32

# Level 5

## Example 1

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: (((((h h h))) h))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 5, 2, 5.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 1

## Example 2

Prompt:

A hydra is a rooted tree of heads. It is written with nested parentheses: each ( ... ) is a body node and each h is a head (a leaf). Siblings are ordered left to right. The root is the outermost ( ... ) group, at depth 0; a head at depth d has d edges to the root.
Hydra rule: to cut a head at depth d, remove that h. If the head's parent is not the root, the parent then regrows d fresh copies of each of its own siblings (the other children of its parent); these copies are attached under the head's grandparent. If the head's parent is the root, nothing regrows.
Starting hydra: (((((h) h) h) ((h) h)) ((h h) (h h h) (h h h h h) h) ((((h h h)) h (h h h))) ((h h h h h) (h h h h h) (h) h h))
Perform cuts in the stated order, each time cutting the leftmost head (scanning left to right) located at the given depth in the tree as it currently stands, at depths: 4, 4, 2.
After all cuts, how many heads (h tokens) remain? Answer with the integer head count.

Answer: 106
