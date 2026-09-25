## Level 0

### Example 1 (level 0)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..6):[(1..4):[3,2,1,4],(5..6):[5,6]]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 3,2,1,4,5,6

### Example 2 (level 0)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..6):[1,(2..6):[3,2,5,4,6]]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 1,3,2,5,4,6

## Level 2

### Example 1 (level 2)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..14):[(1..2):[1,2],(3..14):[(3..7):[6,4,5,7,3],(8..14):[14,12,10,8,13,9,11]]]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 1,2,6,4,5,7,3,14,12,10,8,13,9,11

### Example 2 (level 2)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..14):[1,(2..7):[(2..6):[4,2,6,3,5],7],(8..14):[(8..10):[9,8,10],(11..13):[13,11,12],14]]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 1,4,2,6,3,5,7,9,8,10,13,11,12,14

## Level 5

### Example 1 (level 5)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..26):[(1..12):[(1..4):[(1..2):[1,2],(3..4):[3,4]],(5..12):[5,(6..8):[6,7,8],(9..12):[11,10,12,9]]],(13..26):[(13..22):[(13..15):[14,15,13],(16..21):[21,19,20,16,17,18],22],(23..26):[(23..24):[23,24],(25..26):[26,25]]]]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 1,2,3,4,5,6,7,8,11,10,12,9,14,15,13,21,19,20,16,17,18,22,23,24,26,25

### Example 2 (level 5)

A nested permutation block (lo..hi):[c1,c2,...] expands into a permutation of the integers {lo,...,hi}. The block's parent ranks determine its value range (its lo..hi), and the children's order determines the internal order. A bare integer is a singleton leaf that expands to itself. Flatten the whole expression left-to-right into one permutation of 1..N.

Expand this block:
(1..26):[(1..25):[(1..16):[(1..7):[6,2,3,5,4,1,7],(8..16):[8,14,15,12,9,11,13,16,10]],(17..25):[(17..20):[17,20,18,19],(21..25):[22,21,23,24,25]]],26]

Answer with the expanded permutation as a comma-separated list of integers, e.g. for (1..3):[2,1,3] the answer is 2,1,3.

**Answer:** 6,2,3,5,4,1,7,8,14,15,12,9,11,13,16,10,17,20,18,19,22,21,23,24,25,26

