## Level 0

### Example 1

**Prompt:**

The variables are x1 through x3.
The CNF formula is:
(x1 or x2 or x3); (x1 or x2); (~x1 or x2)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
Decide whether the formula is satisfiable. Answer exactly SAT or UNSAT.

**Answer:** SAT

### Example 2

**Prompt:**

The variables are x1 through x3.
The CNF formula is:
(~x1 or ~x2); (~x2 or x3); (x2 or ~x3)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
List the literals chosen as branch decisions during the search, in the order made (including a backtracked attempt), comma-separated: 'x2' means set x2 true and '~x1' means set x1 false, e.g. 'x2,~x1,x3'. Exclude unit-propagation and pure-literal assignments.

**Answer:** x2

## Level 2

### Example 1

**Prompt:**

The variables are x1 through x5.
The CNF formula is:
(~x2 or x4); (~x1 or x3); (~x3 or x4); (~x3 or ~x4); (x1 or x5); (~x1 or x5); (x2 or ~x5)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
List the literals chosen as branch decisions during the search, in the order made (including a backtracked attempt), comma-separated: 'x2' means set x2 true and '~x1' means set x1 false, e.g. 'x2,~x1,x3'. Exclude unit-propagation and pure-literal assignments.

**Answer:** x1,~x1

### Example 2

**Prompt:**

The variables are x1 through x5.
The CNF formula is:
(x1 or x4); (x2 or ~x5); (~x1 or ~x3); (~x2 or x5); (~x3 or x4); (~x4 or ~x5); (~x4 or x5); (x4); (x3 or ~x4); (~x4 or x5)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
The formula is unsatisfiable. Report the first clause that becomes false during the search, the conflicting clause, as its literals sorted by variable index and comma-separated like '~x1,x3'.

**Answer:** ~x4,x5

## Level 5

### Example 1

**Prompt:**

The variables are x1 through x8.
The CNF formula is:
(x1 or ~x4 or x7); (~x6 or ~x8); (~x1 or x5 or x8); (x1 or ~x3); (~x7); (x1 or ~x3 or ~x5); (x3 or ~x6); (x7 or x8); (x1 or ~x7); (x7 or ~x8); (x5 or ~x7 or ~x8); (x1 or ~x3 or x4); (~x3 or x5 or x7); (~x4 or x5 or x6); (~x3 or x7); (x2 or ~x4)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
The formula is unsatisfiable. Report the first clause that becomes false during the search, the conflicting clause, as its literals sorted by variable index and comma-separated like '~x1,x3'.

**Answer:** x7,~x8

### Example 2

**Prompt:**

The variables are x1 through x8.
The CNF formula is:
(x7 or x8); (x3 or ~x6); (~x2 or x3); (~x1 or ~x3 or x6); (~x6 or ~x8); (x1 or x5 or ~x6); (x5 or x7 or x8); (x4 or x5 or ~x7); (x7 or ~x8); (~x2 or ~x5); (~x5 or ~x6); (~x1 or ~x6 or ~x8); (x3 or ~x5 or x6)
Run the DPLL algorithm: repeatedly propagate unit clauses, eliminate pure literals, and branch on the lowest-index unassigned variable, trying true before false and backtracking on conflict.
The formula is satisfiable. Report the satisfying assignment DPLL produces in increasing variable order, as a comma-separated list where each variable is x<k>=T or x<k>=F, e.g. 'x1=T,x2=F,x3=T'. A variable not fixed by the search is set false.

**Answer:** x1=T,x2=F,x3=T,x4=T,x5=F,x6=T,x7=T,x8=F
