## Level 0

### Example 1

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p1, p2, p4, p0, p5, p3
Initial facts: {p0, p1, p2, p3, p4, p5}

Actions (precondition -> adds; deletes):
  f0: pre {p1} -> add {p1}, del {p4}
  f1: pre {} -> add {p2, p0}, del {p2}
  f2: pre {} -> add {p1, p0}, del {}
  f3: pre {} -> add {p1, p0}, del {p0}
  f4: pre {p1, p0} -> add {p4, p0}, del {}
  f5: pre {p1, p0} -> add {p1, p4}, del {p1}

Goal facts: {p3, p5}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: 0

### Example 2

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p1, q0, p3, q1, p2, p0
Initial facts: {}

Actions (precondition -> adds; deletes):
  c0_0: pre {} -> add {p1}, del {}
  gA: pre {p1} -> add {q0}, del {}
  c2_0: pre {} -> add {p3}, del {}
  gB: pre {p3} -> add {q1}, del {}

Goal facts: {q0, q1}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: 2


## Level 2

### Example 1

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p0, p3, q1, q3, p2, p1, q2, q0
Initial facts: {}

Actions (precondition -> adds; deletes):
  c0_0: pre {} -> add {p0}, del {}
  gA: pre {p0} -> add {p3}, del {}
  c2_0: pre {} -> add {q1}, del {}
  gB: pre {q1} -> add {q3}, del {}

Goal facts: {p3, q3}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: 2

### Example 2

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p6, p3, p5, p0, p7, p2, p1, p4
Initial facts: {p0, p1, p2, p4, p5, p7}

Actions (precondition -> adds; deletes):
  aG: pre {} -> add {p6}, del {p3}
  aH: pre {} -> add {p3}, del {p6}
  f0: pre {p2} -> add {p4}, del {p5}
  f1: pre {} -> add {p5}, del {p4}
  f2: pre {p7, p2} -> add {p7}, del {p7}
  f3: pre {} -> add {p7}, del {}
  f4: pre {p0, p2} -> add {p0}, del {p1}
  f5: pre {} -> add {p1}, del {p0}
  f6: pre {p7, p2} -> add {p7, p4}, del {p4}
  f7: pre {p5, p2} -> add {p4}, del {p5}
  f8: pre {} -> add {p0, p4}, del {}
  f9: pre {} -> add {p7}, del {}

Goal facts: {p3, p6}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: -1


## Level 5

### Example 1

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p6, p4, p7, p0, p8, p3, p9, p2, p5, p1, q0
Initial facts: {}

Actions (precondition -> adds; deletes):
  c0_0: pre {} -> add {p6}, del {}
  c0_1: pre {p6} -> add {p4}, del {}
  c0_2: pre {p4} -> add {p7}, del {}
  c0_3: pre {p7} -> add {p0}, del {}
  gA: pre {p0} -> add {p8}, del {}
  c5_0: pre {} -> add {p3}, del {}
  c5_1: pre {p3} -> add {p9}, del {}
  c5_2: pre {p9} -> add {p2}, del {}
  c5_3: pre {p2} -> add {p5}, del {}
  gB: pre {p5} -> add {p1}, del {}

Goal facts: {p1, p8}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: 5

### Example 2

Prompt:

A planning graph over facts grows level by level; level zero holds exactly the initial facts. At each level an action is added only if all its preconditions are present at that level and are pairwise non-mutex. Two added actions are mutex if one interferes with the other (their add/delete sets overlap, or one deletes an add of the other), or if a precondition of one is mutex with a precondition or effect of the other. In the added level, fact p is mutex with fact q if one of the added actions adds p and deletes q (or adds q and deletes p), or if the pair was already mutex at the previous level, or if every added action that adds p is mutex with every added action that adds q. An already non-mutex pair of simultaneously present facts stays non-mutex at the next level.

All facts: p3, p5, p7, p6, p8, p4, q0, p2, p1, p9, p0
Initial facts: {}

Actions (precondition -> adds; deletes):
  c0_0: pre {} -> add {p3}, del {}
  c0_1: pre {p3} -> add {p5}, del {}
  c0_2: pre {p5} -> add {p7}, del {}
  c0_3: pre {p7} -> add {p6}, del {}
  gA: pre {p6} -> add {p8}, del {}
  c5_0: pre {} -> add {p4}, del {}
  c5_1: pre {p4} -> add {q0}, del {}
  c5_2: pre {q0} -> add {p2}, del {}
  c5_3: pre {p2} -> add {p1}, del {}
  gB: pre {p1} -> add {p9}, del {}

Goal facts: {p8, p9}

Report the 0-based level index of the first level at which all goal facts are present and pairwise non-mutex. If no level ever satisfies this, output -1.

Answer: 5

