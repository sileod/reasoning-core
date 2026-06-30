# 📖 Task Gallery

49 tasks

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`tptp_entailement`](#tptp_entailement) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_retrieval`](#analogical_case_retrieval) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_equivalence`](#table_equivalence) · [`table_statistics`](#table_statistics) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate 0 - 6.
The answer is a number.
```

**Answer:**
```
-6
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
A jar holds 3 beads. 10 more beads added; then 10 beads removed; then tripled. How many beads are in the jar now? Answer with a number.
```

**Answer:**
```
9
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X2 + 17 = 3
  X2 + 17 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
No solution
```

---

## [lean_missing_proof_line_selection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Fill `__ANSWER__` with one listed Lean proof line. Mathlib is imported.
The answer is the line number.

THEOREM:
theorem ex (p q r : Prop) (h0 : p → q) : p ∧ r → q ∧ r := by
  intro h
  __ANSWER__

LINES:
1. simp
2. intro x hx
3. exact ⟨h0 h.1, h.2⟩
4. rfl
5. exact h0
6. intro h
```

**Answer:**
```
3
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex (s t u : Set Int) (h0 : s ⊆ u) : t ∪ s ⊆ t ∪ u := by
  ?

CANDIDATE:
exact h0
```

**Answer:**
```
False
```

---

## [tptp_entailement](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the premises entail the conjecture.

TPTP source: LCL002-1.ax

Background axioms:
- (implies(implies(not(X1),not(X2)),implies(X2,X1))=truth)
- (not(truth)=falsehood)
- (or(X1,X2)=or(X2,X1))
- (or(X1,X2)=implies(not(X1),X2))
- (implies(implies(X1,X2),X2)=implies(implies(X2,X1),X1))
- (or(or(X1,X2),X3)=or(X1,or(X2,X3)))

Premises:
- (implies(implies(X1,X2),implies(implies(X2,X3),implies(X1,X3)))=truth)

Conjecture: `(implies(not(X1),not(implies(X2,not(X3))))=implies(implies(X3,not(X2)),X1))`

The answer is `True` (provable) or `False` (not provable).
```

**Answer:**
```
False
```

---

## [tptp_consistency_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Which local single-clause deletions make the fixed axioms satisfiable with the negated theorem?
Answer with ordered, space-separated clause numbers.
Background axioms:
- (product(X1,X2,X3)|~product(X2,X1,X3))
- (product(X1,X2,X3)|~product(X1,X4,X5)|~product(X4,X6,X2)|~product(X5,X6,X3))
- (product(multiplicative_identity,X1,X1)|~defined(X1))
Negated theorem: `(~product(multiplicative_identity,multiplicative_identity,multiplicative_identity))`
Clauses:
1. (defined(multiplicative_identity))
2. (product(multiplicative_inverse(X1),X1,multiplicative_identity)|sum(additive_identity,X1,additive_identity)|~defined(X1))
3. (product(X1,X2,multiply(X1,X2))|~defined(X1)|~defined(X2))
```

**Answer:**
```
1
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: E=(-3, -2); G=(4/5, -52/5); N=(3, 5); O=(-57/5, 9/5); P=(3, 4); T=(4, -3); V=(-1, 0).
Definitions: G is the reflection of N across line TE. O is the reflection of G across line EP.
Question: Is point T on segment VG?
Answer is either yes or no.
```

**Answer:**
```
no
```

---

## [metamath_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_metamath.py)

**Prompt:**
```
Using only these premises and rules, does the conjecture follow?
Use only the listed premises and rules. No hidden background facts.
Rules may only rename variables, not substitute compound terms.
The answer is True or False.

Premises:
1. ctx => P2(x, D1)
2. ctx => P3(F1(x), C0)

Allowed Rules:
r1: ctx => P2(x, D1) ==> ctx => P2(x, D2)
r2: ctx => P2(x, D2); ctx => P3(F1(x), C0) ==> ctx => P3(x, C0)

Conjecture:
ctx => P3(x, C0)
```

**Answer:**
```
True
```

---

## [metamath_core_select](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_metamath.py)

**Prompt:**
```
Which option is sufficient to derive the conjecture?
Use only the listed premises and rules. No hidden background facts.
Rules may only rename variables, not substitute compound terms.
The answer is A, B, C, or D.

Premises:
1. P1(x, D1)
2. P1(y, D2)
3. P2(x, F1(y, C1))

Rule Catalog:
- r1: ctx => P1(x, D3) ==> ctx => P5(x, F3(x))
- r2: P2(x, y); P2(x, z) ==> P2(y, z)
- r3: P1(x, D2); P2(y, F1(x, C1)) ==> P1(y, D2)
- r4: P1(x, D1); P3(x, C0) ==> P3(F2(x), C0)
- r5: P1(x, D2) ==> P3(x, C0)

Conjecture:
P3(F2(x), C0)

Options:
A. [r1, r3, r5]
B. [r2, r4, r5]
C. [r3, r4, r5]
D. [r3, r5]
```

**Answer:**
```
C
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: ((\_5.(\v0.(_5 (\v1.(b (\v2.((\_1.(\v1.((\_4._1) c))) ((\_2.(_2 a)) (\_0.v0))))))))) (\_3._3))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(\v0.(\v1.(b (\v2.(\v1.v0)))))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- or(true,X) -> true
- and(true,X) -> X
- if(false,X,Y) -> Y
- or(X,false) -> X
- not(not(X)) -> X

Term:
and(true,if(and(or(if(true,b,true),false),b),c,and(true,eq(b,and(false,b)))))

The answer is the normal form.
```

**Answer:**
```
if(and(if(true,b,true),b),c,eq(b,and(false,b)))
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor f is independently true with probability 0.6.
Factor b is independently true with probability 0.4.
The observation holds exactly when (factor f or factor b).
We observe it.
Which hidden fact values form the most probable complete explanation?

Hidden fact values:
0. b
1. not b
2. f
3. not f

Choose one value for each hidden factor. Answer with space-separated indexes.
```

**Answer:**
```
1 2
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A deck contains 2 red cards and 4 blue cards.
Two cards are drawn without replacing the first card.
Which statement is more likely?
A: both selected cards are red.
B: both selected cards are blue.

The answer is exactly one of: A, B, equal.
```

**Answer:**
```
B
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
Mackenzie is the only person in the room.
all quiet people in the room are old
Mackenzie is not golf tagged
everyone anywhere either is not old and not quiet or is not juliet tagged or both
Katelyn is quiet
“The lighthouse on Cape Sorrow does not glow green.” or “No square cloud is over Silver Lake.” but not both

Hypothesis:
Katelyn is not old

Does the premise entail the hypothesis? The answer is yes, no, or maybe.
```

**Answer:**
```
maybe
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] Craig is the only person in the room.
[1] everyone in the room is foxtrot tagged
[2] everyone in the room who is not uniform tagged is not a quiet person
[3] everyone in the room is mike tagged
[4] Craig is quiet
[5] everyone in the room who is tango tagged is quiet and is romeo tagged
Hypothesis:
Craig is not not not quiet

Which statements in the premise contradict the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
4
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno is a parent of alice.
alice is a parent of david.
clara is a sibling of bruno.
alice helps bruno.
bruno is careful.
clara is patient.
Whenever x is a parent of y, x is an ancestor of y.
Whenever x is a parent of y and y is an ancestor of z, x is an ancestor of z.
For all p, x, y, if p is a parent of x and p is a parent of y and x is different from y, then x is a sibling of y.
From x is a sibling of y, it follows that y is a sibling of x.
Whenever x is a spouse of y, y is a spouse of x.
For all x, y, z, if x is a parent of y and x is a sibling of z, then z is an aunt or uncle of y.

Hypothesis:
clara is an aunt or uncle of alice.

Does the premise entail the hypothesis? The answer is yes, no, or maybe.
```

**Answer:**
```
yes
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] map is inside box.
[1] box is inside lamp.
[2] key is blocked.
[3] lamp is fixed.
[4] key is visible.
[5] lamp is left of box.
[6] From x is left of y, it follows that y is right of x.
[7] Whenever x is above y, y is below x.
[8] For all x, y, if x is inside y, then y contains x.
[9] From x is inside y and y is inside z, it follows that x is inside z.
[10] Whenever x is left of y and y is left of z, x is left of z.
[11] When one person is above a second person and the second is above a third person, the first is above the third.
[12] For all x, y, if x is disjoint from y, then y is disjoint from x.

Hypothesis:
lamp does not contain map.

Which premise statements are necessary to contradict the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 8 9
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] clara is careful.
[1] alice is verified.
[2] Every careful entity is trained.
[3] Every trained entity is active.

Hypothesis:
bruno is active.

Candidate Facts:
[0] bruno is not careful.
[1] alice helps clara.
[2] david trusts clara.
[3] alice is active.
[4] david is careful.
[5] bruno is careful.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
5
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
clara trusts david.
david advises alice.
clara helps david.
clara is not verified.
bruno is verified.
clara is active.
alice is active.
For all x, y, z, if x trusts y and y advises z, then x helps z.
For all x, z, if x helps z, then x is trained.
Whenever x is approved, x is trained.
Whenever x trusts y, y does not advises x.
For all x, y, if x helps y and y is active, then x is approved.
For all x, y, z, if x helps y and y trusts z, then x advises z.

Question:
How many entities are approved?

Answer with one integer.
```

**Answer:**
```
1
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
Objects:
object_1

Actions:
action_0(x0)
  Requires: (not fluent_0)
  Effect: fluent_0
action_1(x0)
  Requires: fluent_0
  Effect: not fluent_0
action_2(x0)
  Effect: fluent_0

Initial state:
True values: None

Goal:
fluent_0
Hint: Reference solution has 1 actions (but it may not be optimal).

Action format example: action_0(object1 object2).
The answer is the plan, one action per line.
```

**Answer:**
```
action_0(object_1)
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {876, 871, 875, 874, 879, 878, 880}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{872, 873, 877}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: [3, 7, 1, 16, 13, 4, 1, 8, 1, 9]
How many times does 1 appear? The answer is a number.
```

**Answer:**
```
3
```

---

## [set_expression](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
A: {11, 6, 3, 17, 19, 32, 16, 29}
C: {1, 23, 20, 17, 11, 15, 2, 29}
Evaluate (A^C).
```

**Answer:**
```
{1, 15, 16, 19, 2, 20, 23, 3, 32, 6}
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *, **.
Use n.
Sequence: [-2, -1, 0, 1, 2, 3, 4, 5]
Initial terms: []
The answer is the RHS only.
```

**Answer:**
```
-2 + n
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E3 is the 4th-newest.
- E0 is the 5th-newest.
- E1 is newer than E2.
- E4 is newer than E1.

Which object is the 4th-oldest?
The answer is one object label.
```

**Answer:**
```
E1
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- A is above C.
- B is below A.
- B is below C.
- B is right of A.
- C is left of A.
- B is right of C.
- A starts at (3, 4).

Steps:
1. A moves by (-1, 0).

What is the final coordinate of A? The answer is (x, y).
```

**Answer:**
```
(2, 4)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: black
- b2: red
- b3: green
- b4: green

Initial State:
- b1 is in x1
- b2 is in x1
- b3 is in x3
- b4 is in x2

Moves:
- Move b4 from x2 to x3.
- Move b3 from x3 to x2.
- Transfer everything in x3 into x2.
- Transfer b4 from x2 into x1.
Where is b1 now? The answer is a box tag, like x1.
```

**Answer:**
```
x1
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A kind quiet lawyer named Mark avoided a loud tall writer named Mary.
(2) A loud old pilot named Jane met him.
(3) A kind tall nurse named Adam thanked her.
(4) The writer praised a kind young pilot named Ben.
(5) Jane met him.
(6) He avoided a kind quiet doctor named Luke.

In sentence 6, what does the subject expression 'He' refer to?
The answer is the person's name.
```

**Answer:**
```
Ben
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
4x4 grid. Each row and column contains 1..4 once.
Clues:
- r2c3 = 3
- r4c1 = 4
- r2c2 = 4
- r3c1 = 2

What is r2c1?
Answer with one number.
```

**Answer:**
```
1
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Find the lexicographically smallest shortest directed path from node 5 to node 0.
Answer with space-separated nodes, or `None` if no path exists.

Graph:
0:; 1: 1->2 1->5; 2: 2->1 2->3; 3: 3->0 3->2; 4: 4->5; 5:
```

**Answer:**
```
None
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
digraph { 0->3; 1->5; 2->4; 3->0; 4->1; 5->2 }

Queries:
[(1, 2)]
```

**Answer:**
```
2
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
List all ancestors of node 2.
Order them so predecessors come before successors, with lexicographic tie-breaks.
Answer with space-separated indexes.

Graph:
0: 0->4; 1:; 2:; 3: 3->2; 4: 4->2; 5:
```

**Answer:**
```
0 3 4
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 5-character string that fully matches the regular expression: \d|[WVS]+
```

**Answer:**
```
SWVVW
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'b', 'bb'
Negative: 'a', 'aba', 'bdd', 'cbdca', 'ccaa', 'd', 'dc', 'dd'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
b+
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = (b)bbc
B = cc
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
No
```

---

## [analogical_case_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed, and each link name may also have its direction consistently reversed.

M0
a is alpha-linked to d.
b is alpha-linked to e.
e is alpha-linked to c.
e is gamma-linked to c.
Implies: c is gamma-linked to e.

M1
e is alpha-linked to d.
c is beta-linked to a.
d is beta-linked to b.
a is gamma-linked to d.
Implies: d is beta-linked to a.

M2
a is alpha-linked to b.
c is alpha-linked to a.
d is alpha-linked to b.
b is beta-linked to a.
Implies: d is beta-linked to a.

M3
c is alpha-linked to b.
d is beta-linked to b.
e is beta-linked to b.
a is gamma-linked to d.
Implies: d is alpha-linked to b.

Query
u is delta-linked to x.
z is epsilon-linked to v.
v is gamma-linked to z.
x is gamma-linked to v.
y is gamma-linked to v.
y is gamma-linked to x.
z is gamma-linked to v.
z is gamma-linked to y.
Implies:
```

**Answer:**
```
x is epsilon-linked to v.
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: start -> seq
R1: seq -> 
R2: seq -> expr seq
R3: expr -> '(' seq ')'
R4: expr -> '[' seq ']'
R5: expr -> '<' seq '>'

(STRING)
( < > [ ] ) ( ) < > [ ]

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R3 R2 R5 R1 R2 R4 R1 R1 R2 R3 R1 R2 R5 R1 R2 R4 R1 R1
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> 'international'
D -> 'direction' D

(STRING)
direction direction direction international direction

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
international >>direction<<
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> 'respond'
D -> D 'when'

(PREFIX)
respond when

(TEMPLATE)
when ___ ___

(SUFFIX)
<empty>

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
when when when
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
product|revenue
Draw|509,32
Poor|998,28
Glass|226,93
Range|115,46
General|469,89


SQL: SELECT COUNT(*) FROM dataframe WHERE revenue > 501.43399999999997

The answer is the result as single value.
```

**Answer:**
```
2
```

---

## [table_equivalence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Do these tables contain the same data?
Ignore row order, column order, and table syntax. Match values by column name.

Table A:
customer	company
Dylan Thompson	Adams and Sons
Katie Taylor	Burch and Sons
Veronica Sawyer	Green Group
Mikayla Lee	Mcneil, Rivera and Pugh
Robert Mann DDS	Wolf, Carter and Martinez


Table B:
- customer: Mikayla Lee
  company: Mcneil, Rivera and Pugh
- customer: Robert Mann DDS
  company: Wolf, Carter and Martinez
- customer: Veronica Sawyer
  company: Green Group
- customer: Dylan Thompson
  company: Adams and Sons
- customer: Katie Taylor
  company: Burch and Sons


Answer yes or no.
```

**Answer:**
```
yes
```

---

## [table_statistics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Table:
x0: 0.561; x1: 0.601; x2: 0.026; x3: 1.547; x4: -1.444
x0: -1.539; x1: -1.575; x2: -1.508; x3: -0.376; x4: -0.025
x0: 1.098; x1: 1.235; x2: 0.84; x3: 1.045; x4: 0.802
x0: -0.019; x1: -0.069; x2: -0.775; x3: 1.434; x4: 0.976
x0: 0.577; x1: 0.709; x2: 1.154; x3: 0.069; x4: 0.89
x0: 1.452; x1: 1.456; x2: -0.222; x3: 1.067; x4: 0.243
x0: -0.49; x1: -0.654; x2: 0.84; x3: -0.001; x4: 0.813
x0: -0.601; x1: -0.659; x2: 1.142; x3: 0.235; x4: -1.041
x0: 0.952; x1: 0.943; x2: 1.401; x3: -0.026; x4: 1.195
x0: 0.546; x1: 0.47; x2: 0.483; x3: -0.854; x4: 2.048
x0: 0.552; x1: 0.396; x2: 1.181; x3: 0.017; x4: -1.634
x0: -0.91; x1: -0.92; x2: 0.807; x3: -0.841; x4: -1.97

Find:
column name most associated with column x0

Metric:
absolute Pearson correlation

Answer with only the identifier.
```

**Answer:**
```
x1
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: amber quiet delta vector
Operations:
- sort descending
- reverse
Answer with the final string.
```

**Answer:**
```
   aabcdeeeeilmoqrrtttuv
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(h: list, i: str) -> str:
    print(i)
    print(i)
    a = f"val={5}"
    a = 0 // 6
    return i
def f1(i: str) -> str:
    print(i)
    return i
def endpoint(x0: list, x1: str) -> str:
    return f0(x0, x1)

```
Call: `endpoint([2], 'zb')`
The answer is `OK` if it runs successfully; otherwise the exception class name.
````

**Answer:**
```
OK
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict the value returned by this Python call.
```python
def f0(n: list) -> list:
    a = [m * m for m in range(5, 11)]
    return a
def f1(h: str) -> int:
    print(h)
    a = 8
    return a + 3
def endpoint(x0: list) -> list:
    return f0(x0)

```
Call: `endpoint([1, -1])`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
[25, 36, 49, 64, 81, 100]
```

---

## [code_input_deduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Find the smallest integer x in [-6, 9] such that `endpoint(x) == target`.
Answer with the integer.

```python
def f0(o: int) -> int:
    o -= 6
    return o + 3


def endpoint(x):
    return f0(x) % 4

```

Target: 0
````

**Answer:**
```
-5
```

---

## [game_best_move](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

**Prompt:**
```
In this graph game, choose player's best move. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score.

Start: n0. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:80; n5:90; n6:40. Edges: n0->n1,n4; n1->n6; n2->n3; n3->n5,n6.
Legal player moves now: n1, n4.
The answer is the destination node of the best move.
```

**Answer:**
```
n4
```

---

## [game_forced_win](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

**Prompt:**
```
In this graph game, decide whether player can force a win. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score. A win means final player score is greater than 50.

Start: n0. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n5:40; n6:0. Edges: n0->n1,n5; n1->n2,n4; n2->n6; n3->n6; n4->n6.
The answer is yes or no.
```

**Answer:**
```
no
```

---

