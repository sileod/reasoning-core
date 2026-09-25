## Level 0

### Example 1

Prompt:

Nested compartments c0, c1 (c0 outermost) hold initial token counts [2, 1].
Run 2 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[0, 0]

### Example 2

Prompt:

Nested compartments c0, c1 (c0 outermost) hold initial token counts [4, 1].
Run 2 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[2, 0]

## Level 2

### Example 1

Prompt:

Nested compartments c0, c1, c2, c3 (c0 outermost) hold initial token counts [5, 6, 0, 5].
Active transports (applied in the order stated): 0->1 inward (min of the two moves inward); 2->1 outward (min of the two moves outward).
Division compartments (contents double, capped at 6): [3].
Deferred-dissolution compartments (contents vanish when they reach 0 this round): [0, 3].
Run 1 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[0, 10, 0, 5]

### Example 2

Prompt:

Nested compartments c0, c1, c2, c3 (c0 outermost) hold initial token counts [2, 2, 4, 6].
Active transports (applied in the order stated): 1->2 inward (min of the two moves inward).
Division compartments (contents double, capped at 6): [3].
Deferred-dissolution compartments (contents vanish when they reach 0 this round): [0].
Run 4 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[0, 0, 2, 5]

## Level 5

### Example 1

Prompt:

Nested compartments c0, c1, c2, c3, c4, c5 (c0 outermost) hold initial token counts [8, 8, 7, 0, 1, 5].
Active transports (applied in the order stated): 0->1 inward (min of the two moves inward); 1->2 inward (min of the two moves inward); 2->1 outward (min of the two moves outward); 5->4 outward (min of the two moves outward).
Run 5 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[0, 18, 0, 0, 0, 0]

### Example 2

Prompt:

Nested compartments c0, c1, c2, c3, c4, c5 (c0 outermost) hold initial token counts [4, 8, 7, 5, 6, 7].
Active transports (applied in the order stated): 0->1 inward (min of the two moves inward); 1->0 outward (min of the two moves outward); 2->1 outward (min of the two moves outward); 3->4 inward (min of the two moves inward); 5->4 outward (min of the two moves outward).
Division compartments (contents double, capped at 8): [1].
Deferred-dissolution compartments (contents vanish when they reach 0 this round): [5].
Run 2 round(s). Each round, in order: (1) dissolution set-to-zero, (2) outward transports, (3) inward transports, (4) division, (5) consumption of 1 token from every compartment holding at least 1. Report final token counts as a list [c0, c1, ...].

Answer:

[0, 7, 0, 0, 15, 0]
