
## Level 0

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation below supplies the initial tree; the remaining operations are intended for later, in order. A 'substitute X' replaces a frontier node whose parent category is X with an initial tree rooted at X. An 'adjoin Y' replaces an internal node labeled Y with an auxiliary tree rooted at Y. Apply the operations in order, skipping any that cannot be applied.
Operations: substitute VP; adjoin VP.
After the longest legal prefix of these operations, which is the next operation to attempt? Give its action string exactly as written in the list, e.g. 'adjoin VP'.

Answer: adjoin VP

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation below supplies the initial tree; each later operation is applied in turn. A 'substitute X' operation replaces a frontier node whose parent category is X with an initial tree rooted at X. An 'adjoin Y' operation replaces an internal node labeled Y with an auxiliary tree rooted at Y, which has the same root and a single foot leaf and therefore preserves the category. An operation that cannot be applied is skipped.
Operations: substitute NP; substitute S.
Give the final derived yield (every leaf, left to right) as a space-separated terminal string, e.g. 'a b c'.

Answer: b


## Level 2

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation below supplies the initial tree; the remaining operations are intended for later, in order. A 'substitute X' replaces a frontier node whose parent category is X with an initial tree rooted at X. An 'adjoin Y' replaces an internal node labeled Y with an auxiliary tree rooted at Y. Apply the operations in order, skipping any that cannot be applied.
Operations: substitute VP; substitute S; substitute S; adjoin VP.
After the longest legal prefix of these operations, which is the next operation to attempt? Give its action string exactly as written in the list, e.g. 'adjoin VP'.

Answer: adjoin VP

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation below supplies the initial tree; the remaining operations are intended for later, in order. A 'substitute X' replaces a frontier node whose parent category is X with an initial tree rooted at X. An 'adjoin Y' replaces an internal node labeled Y with an auxiliary tree rooted at Y. Apply the operations in order, skipping any that cannot be applied.
Operations: substitute NP; substitute S; substitute S; adjoin S; substitute VP.
After the longest legal prefix of these operations, which is the next operation to attempt? Give its action string exactly as written in the list, e.g. 'adjoin VP'.

Answer: substitute VP


## Level 5

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation below supplies the initial tree; the remaining operations are intended for later, in order. A 'substitute X' replaces a frontier node whose parent category is X with an initial tree rooted at X. An 'adjoin Y' replaces an internal node labeled Y with an auxiliary tree rooted at Y. Apply the operations in order, skipping any that cannot be applied.
Operations: substitute NP; adjoin NP; adjoin S; adjoin S; substitute S; adjoin S; adjoin NP; adjoin NP.
After the longest legal prefix of these operations, which is the next operation to attempt? Give its action string exactly as written in the list, e.g. 'adjoin VP'.

Answer: adjoin NP

In a tree-adjoining grammar, trees grow by substitution and adjunction. The first operation supplies the initial tree; the rest are applied in order. A 'substitute X' replaces a frontier node whose parent is X with an initial tree rooted at X. An 'adjoin Y' replaces an internal node labeled Y with an auxiliary tree rooted at Y. An operation that cannot be applied is skipped.
Operations: substitute NP; adjoin NP; substitute VP; substitute S; adjoin VP; adjoin NP; adjoin NP; adjoin VP; adjoin VP.
Can every operation be applied in its given order? Answer yes or no.

Answer: yes
