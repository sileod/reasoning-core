# Level 0
## Example 1
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0}
  x1: {0, 1, 2}
  x2: {0}
  x3: {0}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 0|0; 0|1
  x2--x3: none (no pairs allowed at all)

After full propagation some variables' domains become empty (a wipeout). Give the sorted comma-separated indices of exactly the variables whose domain is empty at the arc-consistent fixed point.
Answer format: the letter 'w', a colon, then the sorted indices, e.g. w:1,4

**Answer:**
w:2,3

## Example 2
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0, 1, 2}
  x1: {0, 1}
  x2: {0, 1, 2}
  x3: {0, 1}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 1|0
  x0--x2: 0|2; 1|0; 1|1; 1|2; 2|1
  x1--x2: 0|1; 1|0; 1|1
  x2--x3: 0|0; 1|0; 1|1; 2|0; 2|1

Give every variable's surviving domain after arc-consistency, as comma-separated sorted values per variable, variables joined by '|' in index order. An empty domain is written as nothing between bars.
Answer format example: with x0={0,2}, x1 empty, x2={1}, the answer is: 0,2||1

**Answer:**
1|0|1|0,1

# Level 2
## Example 1
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0}
  x1: {0, 1, 2, 3}
  x2: {0, 1, 2, 3, 4}
  x3: {0, 1, 2}
  x4: {0, 1, 2, 3, 4, 5}
  x5: {0, 1, 2, 3}
  x6: {0, 1}
  x7: {0, 1, 2, 3}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 0|1
  x0--x3: 0|0
  x0--x6: 0|0
  x0--x7: 0|3
  x1--x2: 0|2; 1|0
  x1--x4: 0|1; 0|3; 0|4; 1|2; 1|3; 1|4; 2|0; 2|2; 2|3; 3|2
  x1--x5: 0|0; 0|1; 1|0; 1|2; 2|1; 2|3; 3|0; 3|1
  x1--x6: 1|0; 2|0
  x2--x3: 0|0; 0|1; 1|1; 1|2; 2|0; 3|1; 4|1
  x2--x6: 0|0; 1|0; 2|0; 3|1
  x2--x7: 0|2; 0|3; 1|0; 2|0; 2|1; 2|3; 3|0; 4|0
  x3--x4: 0|4; 1|2; 1|3; 1|4; 1|5; 2|3; 2|5
  x3--x5: 0|1; 0|2
  x3--x7: 0|3; 1|1; 1|2; 2|2
  x4--x5: 0|0; 0|1; 0|2; 1|1; 1|3; 2|2; 3|0; 3|2; 4|0; 4|1; 4|2; 4|3; 5|0
  x4--x6: 3|0; 4|0
  x5--x6: 2|0
  x6--x7: 0|0; 0|1; 0|3; 1|2

Give every variable's surviving domain after arc-consistency, as comma-separated sorted values per variable, variables joined by '|' in index order. An empty domain is written as nothing between bars.
Answer format example: with x0={0,2}, x1 empty, x2={1}, the answer is: 0,2||1

**Answer:**
0|1|0|0|4|2|0|3

## Example 2
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0}
  x1: {0, 1, 2, 3, 4}
  x2: {0}
  x3: {0}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 0|0; 0|2
  x2--x3: none (no pairs allowed at all)

After full propagation some variables' domains become empty (a wipeout). Give the sorted comma-separated indices of exactly the variables whose domain is empty at the arc-consistent fixed point.
Answer format: the letter 'w', a colon, then the sorted indices, e.g. w:1,4

**Answer:**
w:2,3

# Level 5
## Example 1
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0, 1, 2, 3, 4, 5}
  x1: {0, 1, 2, 3, 4, 5, 6}
  x2: {0, 1, 2, 3, 4, 5}
  x3: {0, 1, 2, 3, 4, 5}
  x4: {0, 1, 2}
  x5: {0, 1, 2, 3, 4, 5}
  x6: {0, 1, 2}
  x7: {0, 1, 2, 3}
  x8: {0, 1, 2}
  x9: {0, 1}
  x10: {0}
  x11: {0, 1, 2}
  x12: {0, 1, 2, 3, 4, 5}
  x13: {0}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 0|0; 0|5; 1|2; 1|6; 2|0; 2|2; 2|3; 2|5; 2|6; 3|1; 3|2; 3|4; 3|6; 4|0; 4|3; 5|1
  x0--x2: 0|0; 0|1; 0|3; 0|4; 2|0; 2|1; 2|2; 2|5; 3|0; 4|0; 4|1; 4|2; 4|3; 4|5; 5|5
  x0--x3: 0|0; 0|1; 0|2; 0|5; 1|0; 1|1; 1|3; 2|0; 2|1; 2|5; 3|1; 3|2; 3|4; 4|0; 4|3; 4|4; 4|5; 5|2; 5|3; 5|4; 5|5
  x0--x4: 2|0; 2|1; 3|1; 3|2; 4|2; 5|0
  x0--x5: 0|1; 0|2; 0|3; 0|5; 1|4; 2|0; 2|1; 2|4; 3|1; 3|3; 4|0; 4|1; 4|2; 4|4; 5|1
  x0--x6: 1|0; 1|1; 1|2; 3|0; 3|1; 3|2; 4|2; 5|0
  x0--x9: 1|0; 1|1; 2|0; 3|1; 5|1
  x0--x10: 0|0; 3|0; 5|0
  x0--x11: 0|0; 0|1; 1|0; 1|1; 1|2; 2|1; 3|1; 3|2; 4|2; 5|2
  x1--x2: 0|2; 1|1; 2|3; 3|0; 3|2; 3|3; 3|5; 5|3; 5|5; 6|0; 6|1; 6|5
  x1--x4: 0|0; 1|2; 2|1; 3|0; 3|2; 4|1; 4|2; 5|0; 5|1; 6|1; 6|2
  x1--x6: 0|0; 0|1; 1|0; 1|2; 2|1; 4|1; 5|2; 6|0
  x1--x8: 0|2; 1|1; 3|1; 4|1; 5|2; 6|0
  x1--x10: 2|0; 6|0
  x1--x11: 0|1; 0|2; 1|0; 3|1; 4|0; 6|0; 6|1
  x2--x3: 0|0; 0|2; 0|4; 0|5; 1|0; 1|1; 1|2; 2|1; 2|4; 3|3; 4|0; 4|1; 4|4; 5|1; 5|3; 5|5
  x2--x4: 0|1; 0|2; 3|1; 3|2; 4|1; 4|2; 5|0
  x2--x6: 0|0; 0|1; 2|0; 2|1; 4|1; 5|0; 5|1
  x2--x9: 0|0; 0|1; 2|0; 4|0; 5|1
  x2--x10: 0|0; 1|0; 3|0; 4|0
  x2--x12: 0|2; 0|3; 0|4; 1|2; 1|3; 2|2; 2|5; 3|4; 4|3; 4|5; 5|4
  x3--x4: 0|1; 1|2; 2|1; 2|2; 4|1; 5|2
  x3--x5: 0|1; 0|4; 1|2; 1|3; 1|5; 2|1; 2|5; 3|2; 3|4; 4|0; 4|2; 5|1; 5|2; 5|3
  x3--x6: 2|0; 2|2; 3|1
  x3--x7: 1|1; 2|0; 2|2; 2|3; 3|3; 4|1; 4|3; 5|2
  x3--x10: 2|0; 3|0; 5|0
  x4--x5: 0|0; 0|1; 0|3; 1|2; 2|1; 2|2; 2|5
  x4--x6: 0|0; 0|2; 1|0; 2|0
  x4--x8: 0|0; 1|1; 1|2; 2|0; 2|2
  x4--x12: 0|4; 0|5; 1|0; 1|2; 2|2; 2|4; 2|5
  x4--x13: 2|0
  x5--x6: 0|0; 1|0; 1|2; 3|0; 4|0; 4|2; 5|2
  x5--x7: 1|0; 1|1; 1|2; 2|2; 4|0; 4|3; 5|1; 5|2
  x5--x8: 0|1; 1|0; 5|0; 5|2
  x5--x9: 0|0; 1|0; 1|1; 2|1; 4|1
  x5--x11: 0|0; 1|1; 3|0; 3|2; 4|0; 5|0
  x6--x7: 0|0; 2|0; 2|3
  x6--x11: 0|1; 1|0; 2|0; 2|1
  x6--x13: 0|0; 2|0
  x7--x8: 0|0; 0|2; 1|2; 2|2
  x7--x10: 0|0; 2|0
  x7--x11: 0|0; 0|1; 0|2; 1|2; 2|1
  x7--x12: 0|1; 0|2; 0|3; 0|5; 1|2; 1|3; 1|4; 1|5; 2|2; 2|3; 2|5; 3|0; 3|4
  x8--x9: 0|1; 1|0; 1|1
  x8--x10: 0|0; 1|0
  x8--x11: 0|0; 0|1
  x8--x12: 0|0; 0|1; 0|2; 0|3; 1|3; 1|4; 2|2; 2|3; 2|5
  x8--x13: 0|0; 2|0
  x9--x10: 0|0; 1|0
  x9--x11: 1|1; 1|2
  x9--x12: 0|0; 0|2; 0|4; 1|0; 1|2; 1|5
  x9--x13: 1|0
  x10--x11: 0|1
  x11--x12: 0|3; 1|0; 1|2; 1|4; 2|1; 2|4
  x11--x13: 0|0; 1|0
  x12--x13: 0|0; 2|0

Give every variable's surviving domain after arc-consistency, as comma-separated sorted values per variable, variables joined by '|' in index order. An empty domain is written as nothing between bars.
Answer format example: with x0={0,2}, x1 empty, x2={1}, the answer is: 0,2||1

**Answer:**
3|6|0|2|2|1|0|0|0|1|0|1|2|0

## Example 2
**Prompt:**
We have finite-domain variables and binary constraints, each constraint listing which pairs of values are allowed together. Apply arc-consistency (AC-3 style) by removing values that have no supporting partner in a neighbour's domain, and keep propagating until the network stops changing.
Variables and their current domains:
  x0: {0, 1, 2, 3, 4, 5, 6}
  x1: {0, 1, 2}
  x2: {0, 1, 2, 3, 4, 5}
  x3: {0, 1, 2, 3, 4}
  x4: {0, 1, 2, 3}
  x5: {0, 1, 2, 3, 4}
  x6: {0, 1}
  x7: {0, 1, 2, 3}
  x8: {0, 1}
  x9: {0, 1, 2, 3, 4, 5}
  x10: {0, 1}
  x11: {0, 1, 2}
  x12: {0}
  x13: {0, 1, 2, 3, 4}
Constraints, as allowed pairs 'a|b' meaning x_i=a with x_j=b:
  x0--x1: 0|0; 1|2; 3|0; 3|1; 3|2; 5|0; 6|0; 6|2
  x0--x3: 0|0; 1|0; 1|4; 3|1; 4|4; 5|1; 6|3
  x0--x4: 0|2; 1|2; 2|2; 2|3; 3|2; 4|1; 4|2; 5|0; 5|1; 5|2; 5|3; 6|1; 6|3
  x0--x7: 0|0; 0|1; 0|2; 1|2; 2|0; 2|1; 2|2; 2|3; 3|2; 3|3; 4|1; 4|2; 5|3; 6|1; 6|2
  x0--x9: 0|0; 0|1; 0|2; 0|5; 2|1; 2|5; 3|4; 3|5; 4|2; 5|0; 5|2; 5|5; 6|3; 6|4
  x0--x11: 3|2; 6|0; 6|2
  x0--x13: 0|0; 0|1; 0|2; 0|3; 2|1; 2|4; 3|0; 4|0; 4|3; 4|4; 5|2; 5|3; 6|3
  x1--x2: 0|1; 0|5; 1|3; 1|5; 2|1; 2|2; 2|4
  x1--x4: 0|0; 0|3; 1|3; 2|1; 2|2; 2|3
  x1--x5: 0|3; 0|4; 1|2; 2|0; 2|3
  x1--x6: 1|1; 2|1
  x1--x8: 0|1; 2|0
  x1--x9: 0|5; 1|0; 1|1; 1|4; 1|5; 2|0; 2|1; 2|2; 2|3
  x1--x10: 1|1; 2|0
  x1--x12: 1|0; 2|0
  x2--x3: 0|4; 1|0; 1|2; 1|4; 2|1; 2|2; 3|1; 3|2; 3|4; 4|0; 4|3; 4|4; 5|0; 5|1
  x2--x4: 0|3; 1|1; 1|2; 3|0; 4|0; 4|3; 5|1; 5|3
  x2--x6: 2|0; 3|0; 4|0; 4|1; 5|0; 5|1
  x2--x7: 0|0; 1|0; 1|2; 1|3; 3|0; 3|2; 3|3; 4|0; 4|1; 4|2; 4|3; 5|0; 5|3
  x2--x8: 3|0; 4|0; 5|0
  x2--x9: 0|0; 0|2; 0|3; 1|1; 1|2; 2|1; 2|5; 4|1; 4|3; 5|0; 5|1; 5|3
  x2--x10: 1|0; 2|0; 4|0
  x2--x12: 1|0; 2|0; 4|0; 5|0
  x2--x13: 0|1; 0|3; 1|0; 1|1; 1|2; 1|3; 1|4; 3|2; 3|4; 4|3; 4|4; 5|1; 5|2
  x3--x4: 0|1; 0|2; 0|3; 1|1; 1|2; 2|2; 3|3; 4|1; 4|2
  x3--x5: 0|3; 1|1; 1|3; 1|4; 2|1; 2|4; 3|1; 3|3; 4|1
  x3--x6: 0|1; 3|0; 3|1
  x3--x8: 0|1; 1|1; 3|0; 4|0
  x3--x12: 0|0; 2|0; 3|0
  x3--x13: 0|2; 0|3; 1|2; 1|3; 1|4; 2|4; 3|0; 3|2; 3|3; 4|0; 4|1; 4|2; 4|4
  x4--x5: 0|0; 0|1; 0|3; 0|4; 1|0; 1|2; 2|0; 2|3; 3|2; 3|3
  x4--x6: 0|0; 1|0; 1|1; 3|1
  x4--x7: 1|1; 2|1; 3|0; 3|2
  x4--x8: 0|1; 1|0; 3|0
  x4--x9: 0|0; 0|1; 0|2; 2|1; 2|2; 2|4; 3|0; 3|3
  x4--x11: 0|1; 1|2; 2|1; 2|2; 3|0; 3|2
  x4--x12: 0|0; 3|0
  x5--x6: 2|0; 2|1; 3|1; 4|1
  x5--x8: 0|0; 1|0; 3|0
  x5--x9: 0|2; 0|4; 1|0; 1|1; 1|2; 1|3; 1|4; 2|4; 3|0; 3|1; 3|3; 3|4; 4|3; 4|4
  x5--x11: 1|0; 1|1; 2|2; 3|1; 3|2
  x5--x13: 0|0; 0|3; 2|2; 2|4; 3|1; 3|3; 3|4; 4|3; 4|4
  x6--x7: 1|0; 1|2
  x6--x9: 0|0; 0|4; 0|5; 1|2; 1|3; 1|5
  x6--x10: 0|0; 1|0
  x6--x12: 0|0; 1|0
  x6--x13: 1|0; 1|3; 1|4
  x7--x8: 2|0; 2|1
  x7--x10: 0|0; 1|1; 2|0; 3|0
  x7--x11: 1|0; 2|0; 2|2; 3|2
  x8--x9: 0|3; 0|4; 0|5; 1|1
  x8--x10: 0|0
  x8--x11: 0|0; 0|2
  x8--x13: 0|3; 0|4; 1|0; 1|3
  x9--x10: 0|1; 3|0; 3|1; 5|1
  x9--x11: 0|2; 2|2; 3|1; 3|2; 5|1; 5|2
  x9--x12: 1|0; 3|0; 4|0; 5|0
  x9--x13: 0|2; 0|4; 1|0; 2|1; 2|3; 2|4; 3|3; 3|4; 4|0; 4|1; 4|2; 5|0; 5|2; 5|3; 5|4
  x10--x11: 0|0; 0|2; 1|0
  x10--x13: 0|2; 0|3; 1|0; 1|3; 1|4
  x11--x12: 1|0; 2|0
  x11--x13: 0|1; 0|2; 1|4; 2|0; 2|1; 2|3; 2|4
  x12--x13: 0|1; 0|3; 0|4

Give every variable's surviving domain after arc-consistency, as comma-separated sorted values per variable, variables joined by '|' in index order. An empty domain is written as nothing between bars.
Answer format example: with x0={0,2}, x1 empty, x2={1}, the answer is: 0,2||1

**Answer:**
6|2|4|3|3|3|1|2|0|3|0|2|0|3
