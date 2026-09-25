## Level 0

### Example 1

**Prompt:**

An MLL proof structure is described by these links (the n{id} are formula nodes; leaves carry atom labels and are paired by axiom links; '⊗' is a tensor and '⪯' is a par link, each with two premises and one conclusion): axiom 0: n0--n5 [b]; axiom 1: n2--n3 [a]; axiom 2: n4--n1 [b]; par P0: n0 ⪯ n1 -> n6; par P1: n3 ⪯ n2 -> n7; par P2: n4 ⪯ n5 -> n8; tensor: n7 ⊗ n6 -> n9; tensor: n9 ⊗ n8 -> n10. A switching keeps, for every ⪯ (par) link, exactly one of its two premise edges (0 = keep the first premise, 1 = keep the second premise); tensor and axiom edges are always kept. The par links appear in order P0, P1, ... The structure is a proof net only if every switching is acyclic. A switching assignment is a bit string, position i for Pi. Find a switching that is cyclic, proving this is NOT a proof net, and return the lexicographically smallest such bit string. Answer with that bit string only.


**Answer:**

100


### Example 2

**Prompt:**

An MLL proof structure is described by these links (the n{id} are formula nodes; leaves carry atom labels and are paired by axiom links; '⊗' is a tensor and '⪯' is a par link, each with two premises and one conclusion): axiom 0: n0--n3 [b]; axiom 1: n2--n1 [b]; axiom 2: n4--n5 [a]; par P0: n1 ⪯ n5 -> n8; par P1: n6 ⪯ n7 -> n9; par P2: n8 ⪯ n9 -> n10; tensor: n2 ⊗ n4 -> n6; tensor: n3 ⊗ n0 -> n7. A switching keeps, for every ⪯ (par) link, exactly one of its two premise edges (0 = keep the first premise, 1 = keep the second premise); tensor and axiom edges are always kept. The par links appear in order P0, P1, ... The structure is a proof net only if every switching is acyclic. A switching assignment is a bit string, position i for Pi. Find a switching that is cyclic, proving this is NOT a proof net, and return the lexicographically smallest such bit string. Answer with that bit string only.


**Answer:**

000


## Level 2

### Example 1

**Prompt:**

An MLL proof structure is described by these links (axiom links pair atoms of the same label; '⊗' is tensor and '⪯' is par, each with two premises and one conclusion): axiom 0: n0--n7 [c]; axiom 1: n2--n3 [d]; axiom 2: n4--n5 [a]; axiom 3: n6--n1 [c]; par P0: n0 ⪯ n1 -> n8; par P1: n11 ⪯ n9 -> n12; par P2: n12 ⪯ n5 -> n13; par P3: n13 ⪯ n7 -> n14; tensor: n2 ⊗ n6 -> n9; tensor: n8 ⊗ n3 -> n10; tensor: n10 ⊗ n4 -> n11. A switching keeps, for every ⪯ (par) link, exactly one premise edge; the structure is a proof net only if every switching is acyclic. This structure is NOT a proof net. Swapping the atom endpoints of two axiom links (which must carry the same atom label) can restore correctness so that every switching is acyclic. Axiom links are numbered 0,1,... in the order listed above. Return the canonical repair, the lexicographically smallest pair {i,j} with i<j of same-label axiom links whose swap makes every switching acyclic, as 'swap i j'.


**Answer:**

swap 0 3


### Example 2

**Prompt:**

An MLL proof structure is described by these links (axiom links pair atoms of the same label; '⊗' is tensor and '⪯' is par, each with two premises and one conclusion): axiom 0: n0--n1 [c]; axiom 1: n2--n7 [d]; axiom 2: n4--n5 [a]; axiom 3: n6--n3 [d]; par P0: n4 ⪯ n5 -> n8; par P1: n6 ⪯ n7 -> n10; par P2: n12 ⪯ n9 -> n13; par P3: n13 ⪯ n1 -> n14; tensor: n2 ⊗ n0 -> n9; tensor: n8 ⊗ n10 -> n11; tensor: n11 ⊗ n3 -> n12. A switching keeps, for every ⪯ (par) link, exactly one premise edge; the structure is a proof net only if every switching is acyclic. This structure is NOT a proof net. Swapping the atom endpoints of two axiom links (which must carry the same atom label) can restore correctness so that every switching is acyclic. Axiom links are numbered 0,1,... in the order listed above. Return the canonical repair, the lexicographically smallest pair {i,j} with i<j of same-label axiom links whose swap makes every switching acyclic, as 'swap i j'.


**Answer:**

swap 1 3


## Level 5

### Example 1

**Prompt:**

An MLL proof structure is described by these links (the n{id} are formula nodes; leaves carry atom labels and are paired by axiom links; '⊗' is a tensor and '⪯' is a par link, each with two premises and one conclusion): axiom 0: n0--n7 [b]; axiom 1: n2--n3 [a]; axiom 2: n4--n5 [c]; axiom 3: n6--n1 [b]; axiom 4: n8--n9 [d]; axiom 5: n10--n11 [c]; axiom 6: n12--n13 [c]; par P0: n1 ⪯ n0 -> n17; par P1: n15 ⪯ n3 -> n18; par P2: n18 ⪯ n9 -> n19; par P3: n12 ⪯ n13 -> n20; par P4: n16 ⪯ n11 -> n21; par P5: n7 ⪯ n14 -> n22; par P6: n21 ⪯ n22 -> n23; tensor: n4 ⊗ n10 -> n14; tensor: n8 ⊗ n2 -> n15; tensor: n5 ⊗ n6 -> n16; tensor: n17 ⊗ n23 -> n24; tensor: n20 ⊗ n19 -> n25; tensor: n25 ⊗ n24 -> n26. A switching keeps, for every ⪯ (par) link, exactly one of its two premise edges (0 = keep the first premise, 1 = keep the second premise); tensor and axiom edges are always kept. The par links appear in order P0, P1, ... The structure is a proof net only if every switching is acyclic. A switching assignment is a bit string, position i for Pi. Find a switching that is cyclic, proving this is NOT a proof net, and return the lexicographically smallest such bit string. Answer with that bit string only.


**Answer:**

0000000


### Example 2

**Prompt:**

An MLL proof structure is described by these links (axiom links pair atoms of the same label; '⊗' is tensor and '⪯' is par, each with two premises and one conclusion): axiom 0: n0--n1 [b]; axiom 1: n2--n3 [c]; axiom 2: n4--n5 [d]; axiom 3: n6--n7 [c]; axiom 4: n8--n13 [b]; axiom 5: n10--n11 [e]; axiom 6: n12--n9 [b]; par P0: n2 ⪯ n3 -> n16; par P1: n13 ⪯ n12 -> n20; par P2: n18 ⪯ n17 -> n22; par P3: n19 ⪯ n7 -> n23; par P4: n5 ⪯ n23 -> n24; par P5: n24 ⪯ n22 -> n25; par P6: n21 ⪯ n25 -> n26; tensor: n0 ⊗ n8 -> n14; tensor: n10 ⊗ n6 -> n15; tensor: n11 ⊗ n4 -> n17; tensor: n1 ⊗ n15 -> n18; tensor: n14 ⊗ n16 -> n19; tensor: n9 ⊗ n20 -> n21. A switching keeps, for every ⪯ (par) link, exactly one premise edge; the structure is a proof net only if every switching is acyclic. This structure is NOT a proof net. Swapping the atom endpoints of two axiom links (which must carry the same atom label) can restore correctness so that every switching is acyclic. Axiom links are numbered 0,1,... in the order listed above. Return the canonical repair, the lexicographically smallest pair {i,j} with i<j of same-label axiom links whose swap makes every switching acyclic, as 'swap i j'.


**Answer:**

swap 4 6

