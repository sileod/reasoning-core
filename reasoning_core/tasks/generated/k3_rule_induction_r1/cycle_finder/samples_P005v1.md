# Samples for P005v1 functional_graph_cycle_finding

## Level 0

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7} by the following successor rules: f(0) = 6, f(1) = 2, f(2) = 1, f(3) = 3, f(4) = 7, f(5) = 6, f(6) = 1, f(7) = 3. Starting from the element 5, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

1 2 2

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7} by the following successor rules: f(0) = 0, f(1) = 1, f(2) = 3, f(3) = 4, f(4) = 7, f(5) = 7, f(6) = 5, f(7) = 6. Starting from the element 6, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

6 0 3

## Level 2

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13} by the following successor rules: f(0) = 13, f(1) = 9, f(2) = 13, f(3) = 9, f(4) = 4, f(5) = 3, f(6) = 10, f(7) = 7, f(8) = 6, f(9) = 3, f(10) = 0, f(11) = 7, f(12) = 8, f(13) = 12. Starting from the element 9, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

9 0 2

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13} by the following successor rules: f(0) = 3, f(1) = 6, f(2) = 9, f(3) = 6, f(4) = 5, f(5) = 8, f(6) = 9, f(7) = 10, f(8) = 3, f(9) = 7, f(10) = 4, f(11) = 2, f(12) = 8, f(13) = 10. Starting from the element 6, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

6 0 8

## Level 5

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22} by the following successor rules: f(0) = 20, f(1) = 13, f(2) = 0, f(3) = 4, f(4) = 14, f(5) = 12, f(6) = 14, f(7) = 10, f(8) = 7, f(9) = 8, f(10) = 18, f(11) = 6, f(12) = 13, f(13) = 11, f(14) = 16, f(15) = 5, f(16) = 9, f(17) = 15, f(18) = 17, f(19) = 8, f(20) = 5, f(21) = 5, f(22) = 0. Starting from the element 17, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

17 0 14

### Prompt

A function f is defined on the set of integers {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22} by the following successor rules: f(0) = 1, f(1) = 3, f(2) = 1, f(3) = 4, f(4) = 5, f(5) = 2, f(6) = 19, f(7) = 11, f(8) = 5, f(9) = 1, f(10) = 11, f(11) = 15, f(12) = 9, f(13) = 19, f(14) = 22, f(15) = 20, f(16) = 19, f(17) = 21, f(18) = 12, f(19) = 15, f(20) = 12, f(21) = 19, f(22) = 0. Starting from the element 0, iterate f repeatedly. Report three integers separated by spaces: the entry point (first value at which the trajectory enters the cycle), the tail length (number of iterates before the entry point, counting the start as iterate 0), and the cycle length. Format: '<entry> <tail> <cycle>'.

### Answer

1 1 5
