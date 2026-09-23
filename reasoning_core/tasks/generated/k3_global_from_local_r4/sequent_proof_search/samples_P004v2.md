### Level 0

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: u, s, u |- ((s and u) and u)
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
3

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: v |- v
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
1
### Level 2

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: x |- x
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
1

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: q, r, v, (q or (q and w)) |- ((q and (r and q)) and v)
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
4
### Level 5

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: v, x, (u or (u and x)), h |- ((u and x) or (h or v))
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
3

Prompt:
We work with single-conclusion propositional sequents Gamma |- A, where Gamma is the ordered left side (a comma-separated list of formulas) and A is the single formula on the right. Formulas are built from atoms and the connectives and / or, each fully parenthesized: (X and Y) is the conjunction and (X or Y) the disjunction of X and Y with X on the left and Y on the right.

A finished derivation tree is built from a sequent by this deterministic procedure, reapplied until no rule applies; we want the number of leaves of that tree.

For a right conjunction A = (X and Y): split into two children Gamma |- X and Gamma |- Y (both premises are followed).
For a right disjunction A = (X or Y): follow only the first premise Gamma |- X (the right disjunction keeps the first disjunct).
If A is an atom p and p is listed in Gamma: this is an axiom leaf; it contributes exactly one leaf and nothing more is done.
Otherwise A is an atom p not present in Gamma: scan Gamma from left to right and, at the first formula that is a conjunction or disjunction, apply a left rule, then start again from the left. For a conjunct (X and Y) replace it in place by the two formulas X, Y (one premise). For a disjunct (X or Y) branch into two children: one with that formula replaced in place by X, and one with it replaced in place by Y (two premises, both counted).

Sequent: a, u, (z or (z and x)), z, (p or (p and p)), p |- ((z and (u and z)) and ((p and a) and p))
Count every axiom leaf of the finished tree. The answer is the integer leaf count.

Answer:
6
