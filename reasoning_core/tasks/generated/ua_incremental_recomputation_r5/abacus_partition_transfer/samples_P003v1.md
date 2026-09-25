## Level 0

### Example 1

**Prompt:**

A beta set of 4 distinct bead positions (1, 7, 9, 10) is placed on an abacus with 2 runners, one runner per residue class mod 2: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 10
runner 1: 1, 7, 9

**Answer:** core=0,1,3,5;quot=5;0,3,4;orig=1->1,7->3,9->5,10->0

### Example 2

**Prompt:**

A beta set of 4 distinct bead positions (4, 7, 8, 11) is placed on an abacus with 2 runners, one runner per residue class mod 2: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 4, 8
runner 1: 7, 11

**Answer:** core=0,1,2,3;quot=2,4;3,5;orig=4->0,7->1,8->2,11->3

## Level 2

### Example 1

**Prompt:**

A beta set of 6 distinct bead positions (5, 6, 10, 13, 19, 20) is placed on an abacus with 2 runners, one runner per residue class mod 2: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 6, 10, 20
runner 1: 5, 13, 19

**Answer:** core=0,1,2,3,4,5;quot=3,5,10;2,6,9;orig=5->1,6->0,10->2,13->3,19->5,20->4

### Example 2

**Prompt:**

A beta set of 6 distinct bead positions (3, 5, 7, 11, 13, 18) is placed on an abacus with 2 runners, one runner per residue class mod 2: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 18
runner 1: 3, 5, 7, 11, 13

**Answer:** core=0,1,3,5,7,9;quot=9;1,2,3,5,6;orig=3->1,5->3,7->5,11->7,13->9,18->0

## Level 5

### Example 1

**Prompt:**

A beta set of 9 distinct bead positions (4, 13, 17, 18, 19, 20, 21, 27, 31) is placed on an abacus with 3 runners, one runner per residue class mod 3: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 18, 21, 27
runner 1: 4, 13, 19, 31
runner 2: 17, 20

**Answer:** core=0,1,2,3,4,5,6,7,10;quot=6,7,9;1,4,6,10;5,6;orig=4->1,13->4,17->2,18->0,19->7,20->5,21->3,27->6,31->10

### Example 2

**Prompt:**

A beta set of 9 distinct bead positions (1, 12, 19, 21, 22, 23, 26, 29, 32) is placed on an abacus with 3 runners, one runner per residue class mod 3: a bead at position p sits on runner p mod r at row floor(p/r). Each bead is labelled by its starting position. Slide every bead up on its own runner as far as it can go (row by row) to form the r-core; the quotient records, for each runner, the original rows of that runner's beads (a list of runner beta sets). The core beta set is the set of bead positions after sliding. Report the r-core beta set, the quotient as a list of runner beta sets, and every bead's core position, as:
core=<core positions, ascending, comma-separated>;quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, ascending comma-separated, 0 if the runner is empty);orig=<label->corepos, for each label ascending, comma-separated>.
Runners:
runner 0: 12, 21
runner 1: 1, 19, 22
runner 2: 23, 26, 29, 32

**Answer:** core=0,1,2,3,4,5,7,8,11;quot=4,7;0,6,7;7,8,9,10;orig=1->1,12->0,19->4,21->3,22->7,23->2,26->5,29->8,32->11
