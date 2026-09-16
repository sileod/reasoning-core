# Level 0

### Example

Domain D = {0, 1}. The quantifier prefix is: for every universal assignment there exists an existential assignment; after the universals u0..u1 are fixed, the existentials e0..e1 are chosen in linear order, each e[j] able to see the universals u0..u[j].
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [1, 0, 1, 0] | C1(u0,u1,e1) = [0, 1, 1, 0, 1, 0, 0, 1]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** 0;0->0;1 | 0;1->0;0 | 1;0->0;0 | 1;1->0;1

### Example

Domain D = {0, 1}. The quantifier prefix is: for every universal assignment there exists an existential assignment; after the universals u0..u1 are fixed, the existentials e0..e1 are chosen in linear order, each e[j] able to see the universals u0..u[j].
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [0, 1, 1, 0] | C1(u0,u1,e1) = [1, 0, 0, 1, 1, 0, 1, 0]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** 0;0->1;0 | 0;1->1;1 | 1;0->0;0 | 1;1->0;0



# Level 2

### Example

Domain D = {0, 1, 2}. The quantifier prefix is: for every universal assignment there exists an existential assignment; branching independence: each existential group depends on one dedicated universal and the groups commit simultaneously.
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [1, 0, 0, 1, 0, 0, 1, 0, 0] | C1(u1,e1) = [0, 1, 0, 0, 1, 0, 0, 0, 1]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** 0;0->0;1 | 0;1->0;1 | 0;2->0;2 | 1;0->0;1 | 1;1->0;1 | 1;2->0;2 | 2;0->0;1 | 2;1->0;1 | 2;2->0;2

### Example

Domain D = {0, 1, 2}. The quantifier prefix is: for every universal assignment there exists an existential assignment; branching independence: each existential group depends on one dedicated universal and the groups commit simultaneously.
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [1, 0, 0, 0, 1, 0, 0, 0, 1] | C1(u1,e1) = [0, 0, 1, 1, 0, 0, 0, 0, 1]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** 0;0->0;2 | 0;1->0;0 | 0;2->0;2 | 1;0->1;2 | 1;1->1;0 | 1;2->1;2 | 2;0->2;2 | 2;1->2;0 | 2;2->2;2



# Level 5

### Example

Domain D = {0, 1, 2}. The quantifier prefix is: for every universal assignment there exists an existential assignment; slashed independence: each existential e[j] depends on u[j] and on all earlier existentials, independent of every other universal.
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [1, 0, 0, 1, 0, 0, 0, 1, 0] | C1(u1,e0,e1) = [0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0] | C2(u2,e0,e1,e2) = [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** 0;0;0->0;2;1 | 0;0;1->0;2;1 | 0;0;2->0;2;0 | 0;1;0->0;1;0 | 0;1;1->0;1;1 | 0;1;2->0;1;0 | 0;2;0->0;0;1 | 0;2;1->0;0;1 | 0;2;2->0;0;1 | 1;0;0->0;2;1 | 1;0;1->0;2;1 | 1;0;2->0;2;0 | 1;1;0->0;1;0 | 1;1;1->0;1;1 | 1;1;2->0;1;0 | 1;2;0->0;0;1 | 1;2;1->0;0;1 | 1;2;2->0;0;1 | 2;0;0->1;2;2 | 2;0;1->1;2;2 | 2;0;2->1;2;0 | 2;1;0->1;2;2 | 2;1;1->1;2;2 | 2;1;2->1;2;0 | 2;2;0->1;2;2 | 2;2;1->1;2;2 | 2;2;2->1;2;0

### Example

Domain D = {0, 1, 2}. The quantifier prefix is: for every universal assignment there exists an existential assignment; slashed independence: each existential e[j] depends on u[j] and on all earlier existentials, independent of every other universal.
Formula clauses (each is a boolean truth table over its listed arguments, values in increasing order, least-significant last; the conjunction of all clauses must hold):
C0(u0,e0) = [0, 1, 0, 1, 0, 0, 1, 0, 0] | C1(u1,e0,e1) = [1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1] | C2(u2,e0,e1,e2) = [0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1] | C3(u2) = [0, 1, 1]
The universal player wins if some universal assignment makes the conjunction false for every existential choice; the existential player wins otherwise, choosing one existential value per universal assignment.
Name the winner. If the existential player wins, give its strategy as a table mapping each universal assignment to the chosen existential values, rows sorted lexicographically and joined by ' | ', each row of the form 'u0;u1->e0;e1'. If the universal player wins, output the single word UNIVERSAL.


**Answer:** UNIVERSAL



