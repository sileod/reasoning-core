### Level 0
**Prompt**
Here is a rooted tree whose tips carry one state each from the set {A..B}; every internal node also gets one state. The parsimony score is the number of branches whose two endpoint states differ. Find the minimum parsimony score over all ways to label the internal nodes. Answer with a single positive integer.
Tree: node14->(node13->(node10->(tip4=B, tip3=B), node8->(tip1=A, tip7=B)), node12->(tip0=A, node11->(node9->(tip6=A, tip2=B), tip5=A)))
**Answer**
3

**Prompt**
Different optimal (minimum-change) labelings may assign different states to the root of this tree. Give one state that can validly be placed at the root in some optimal labeling. Answer with a single letter.
Tree: node14->(node13->(node12->(tip4=A, node10->(tip0=B, tip2=A)), node11->(tip3=A, node8->(tip6=A, tip7=B))), node9->(tip5=B, tip1=B))
**Answer**
A

### Level 2
**Prompt**
Tip states are drawn from {A..C}. A root state is 'valid' if it can be assigned to the root in some optimal (minimum-change) labeling. List every valid root state in ascending order, separated by commas with no spaces.
Tree: node14->(node13->(tip5=B, node12->(node11->(node9->(node8->(tip7=C, tip2=C), tip0=A), tip3=B), node10->(tip1=A, tip6=B))), tip4=A)
**Answer**
A,B

**Prompt**
Tip states are drawn from {A..C}. A root state is 'valid' if it can be assigned to the root in some optimal (minimum-change) labeling. List every valid root state in ascending order, separated by commas with no spaces.
Tree: node14->(node13->(node11->(tip4=C, tip7=C), node9->(tip1=A, tip5=B)), node12->(tip0=C, node10->(node8->(tip3=A, tip6=C), tip2=A)))
**Answer**
A,C

### Level 5
**Prompt**
Tip states are drawn from {A..D}. A root state is 'valid' if it can be assigned to the root in some optimal (minimum-change) labeling. List every valid root state in ascending order, separated by commas with no spaces.
Tree: node14->(tip2=A, node13->(tip7=D, node12->(node11->(node8->(tip4=B, tip6=D), node10->(tip3=B, node9->(tip5=A, tip0=A))), tip1=B)))
**Answer**
A,B,D

**Prompt**
Different optimal (minimum-change) labelings may assign different states to the root of this tree. Give one state that can validly be placed at the root in some optimal labeling. Answer with a single letter.
Tree: node14->(node12->(tip7=C, node11->(tip0=A, tip6=B)), node13->(node10->(tip4=A, node9->(tip5=C, node8->(tip1=C, tip2=B))), tip3=D))
**Answer**
A

