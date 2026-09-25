# Samples: team_semantics_evaluation (P011v1)

Two prompt/answer examples at each of levels 0, 2 and 5. Answers are verbatim.

## Level 0
### Example 1
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1}.

A literal (u=w) is satisfied by a team iff every row has u=w, and (u!=w) iff every row has u!=w.  The split disjunction phi⊗psi is satisfied iff the rows can be shared out into a nonempty left part satisfying phi and a nonempty right part satisfying psi.  Under STRICT semantics no row may be in both parts; under LAX semantics a row may be in both parts, and the two parts together must use up every row.

Team rows:
  1. p=0 q=0 u=1 v=0
  2. p=1 q=1 u=1 v=1

This problem uses LAX semantics.
Formula: (u!=v) ⊗ (p=q)

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: Yes

### Example 2
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1}.

Write X⊥Y for the independence atom: it is satisfied exactly when every combination of an X-tuple that occurs and a Y-tuple that occurs appears together in some row.

Team rows:
  1. a=0 b=0
  2. a=0 b=1
  3. a=1 b=0
  4. a=1 b=1

This atom has a single semantics (strict and lax coincide).
Formula: a ⊥ b

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: Yes

## Level 2
### Example 1
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1}.

A literal (u=w) is satisfied by a team iff every row has u=w, and (u!=w) iff every row has u!=w.  The split disjunction phi⊗psi is satisfied iff the rows can be shared out into a nonempty left part satisfying phi and a nonempty right part satisfying psi.  Under STRICT semantics no row may be in both parts; under LAX semantics a row may be in both parts, and the two parts together must use up every row.

Team rows:
  1. p=0 q=0 u=1 v=0

This problem uses LAX semantics.
Formula: (u=v) ⊗ (p!=q)

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: No

### Example 2
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1}.

A literal (u=w) is satisfied by a team iff every row has u=w, and (u!=w) iff every row has u!=w.  The formula ∃x phi is satisfied iff there is a team over the base variables plus x, agreeing with the given team on the base variables, whose rows satisfy phi.  Under STRICT semantics each given row is extended by exactly one value of x; under LAX semantics a given row may be extended by one or by several different values of x.

Team rows:
  1. u=0 v=0

This problem uses LAX semantics.
Formula: ∃x (x!=v)

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: Yes

## Level 5
### Example 1
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1,2}.

Write X⊆Y for the inclusion atom: it is satisfied exactly when each row's tuple of Y-values occurs as the X-tuple of some row.

Team rows:
  1. a=0 b=2 c=0
  2. a=1 b=1 c=0
  3. a=2 b=2 c=0
  4. a=1 b=0 c=0
  5. a=2 b=2 c=2
  6. a=1 b=0 c=1
  7. a=0 b=1 c=2

This atom has a single semantics (strict and lax coincide).
Formula: b ⊆ a

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: Yes

### Example 2
Prompt:
```text
In team semantics a formula is evaluated over a finite team: a set of assignments (rows) that map each variable to a value in {0,1,2}.

Write X⊥Y for the independence atom: it is satisfied exactly when every combination of an X-tuple that occurs and a Y-tuple that occurs appears together in some row.

Team rows:
  1. a=0 b=0 c=1
  2. a=1 b=0 c=1
  3. a=1 b=1 c=2

This atom has a single semantics (strict and lax coincide).
Formula: b,c ⊥ a

Determine whether the team is a model of the formula. Write Yes for a model, No otherwise.
```
Answer: No
