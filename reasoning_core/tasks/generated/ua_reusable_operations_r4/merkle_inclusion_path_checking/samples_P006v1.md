# Merkle inclusion path checking - variant 1 (P006v1)

## Level 0

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 97
Leaf value: 92
Level 1: sibling on side R, sibling value 9, stated node value 80
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 80|valid

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 97
Leaf value: 38
Level 1: sibling on side R, sibling value 25, stated node value 37
Level 2: sibling on side L, sibling value 31, stated node value 14
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 14|valid

## Level 2

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 277
Leaf value: 143
Level 1: sibling on side L, sibling value 125, stated node value 126
Level 2: sibling on side L, sibling value 232, stated node value 260
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 260|valid

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 277
Leaf value: 57
Level 1: sibling on side R, sibling value 142, stated node value 27
Level 2: sibling on side R, sibling value 170, stated node value 34
Level 3: sibling on side L, sibling value 29, stated node value 190
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 252|3

## Level 5

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 547
Leaf value: 319
Level 1: sibling on side L, sibling value 425, stated node value 468
Level 2: sibling on side L, sibling value 151, stated node value 437
Level 3: sibling on side L, sibling value 12, stated node value 431
Level 4: sibling on side R, sibling value 76, stated node value 52
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 52|valid

### Example

A Merkle tree inclusion path from a leaf to the root lists each level on the way up.
Every level has a sibling value sitting on one side of the path node, and a stated value that the path node is claimed to have at that level.
Starting from the leaf value, combine the current value with the sibling into a parent node using (current*31 + sibling) mod M when the sibling is on the left (L), and (sibling*31 + current) mod M when the sibling is on the right (R). The result of one level is the current value of the next. Recompute the whole path using only the leaf and the given siblings (ignore the stated values when combining), then compare each level's computed value against that level's stated value. The stated value of the top level is the stated root.
Modulus M: 547
Leaf value: 12
Level 1: sibling on side R, sibling value 118, stated node value 388
Level 2: sibling on side R, sibling value 89, stated node value 412
Level 3: sibling on side L, sibling value 281, stated node value 472
Level 4: sibling on side L, sibling value 71, stated node value 481
Level 5: sibling on side R, sibling value 433, stated node value 229
Level 6: sibling on side R, sibling value 413, stated node value 183
Answer the recomputed root, a pipe '|', then the first level (1-indexed) where your computed value differs from that level's stated value, or the word 'valid' if every level matches. Example: '441|valid' or '441|2'.

**Answer:** 451|6

