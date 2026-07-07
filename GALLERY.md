# 📖 Task Gallery

49 tasks

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`tptp_entailment`](#tptp_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_retrieval`](#analogical_case_retrieval) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_equivalence`](#table_equivalence) · [`table_statistics`](#table_statistics) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

- hash: `598d63b9e4e18438`
- modified: 1782205256

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

- hash: `598d63b9e4e18438`
- modified: 1782205256

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

- hash: `78d5fb6a6a43144b`
- modified: 1781597560

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

- hash: `58e7849f9da75921`
- modified: 1782137662

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

- hash: `58e7849f9da75921`
- modified: 1782137662

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

## [tptp_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

- hash: `fec294d568b6b0db`
- modified: 1782825144

**Prompt:**
```
Decide if the premises entail the conjecture.

TPTP source: SET001-2.ax

Background axioms:
- (member(X4,X3)|~intersection(X1,X2,X3)|~member(X4,X2)|~member(X4,X1))

Premises:
- (subset(X1,X2)|~member(member_of_1_not_of_2(X1,X2),X2))
- (subset(X1,X2)|member(member_of_1_not_of_2(X1,X2),X1))
- (member(X4,X1)|~intersection(X1,X2,X3)|~member(X4,X3))

Conjecture: `(subset(X1,X2)|~intersection(X2,X3,X4)|~intersection(X1,X1,X4))`

The answer is `True` (provable) or `False` (not provable).
```

**Answer:**
```
True
```

---

## [tptp_consistency_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

- hash: `fec294d568b6b0db`
- modified: 1782825144

**Prompt:**
```
Which local single-clause deletions make the fixed axioms satisfiable with the negated theorem?
Answer with ordered, space-separated clause numbers.
Background axioms:
- (member(empty_set,infinity))
Negated theorem: `(~little_set(empty_set))`
Clauses:
1. (little_set(infinity))
2. (X1=empty_set|member(f26(X1),X1)|~little_set(X1))
3. (~member(X1,empty_set))
4. (little_set(X1)|~member(X1,X2))
```

**Answer:**
```
4
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

- hash: `f8127b77dad7e9a5`
- modified: 1782201844

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

- hash: `3ceb928c8bf291be`
- modified: 1782388471

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

- hash: `3ceb928c8bf291be`
- modified: 1782388471

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

- hash: `da074542ea9f5644`
- modified: 1782724716

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: ((\v0.((((\v0.v0) v0) (\v1.(\v2.c))) ((\v1.(v0 v1)) (\v1.c)))) (\v0.(((v0 d) (v0 v0)) v0)))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
((c (\v1.(\v2.c))) ((c c) (\v1.c)))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

- hash: `da074542ea9f5644`
- modified: 1782724716

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

- hash: `5cbfb535441c3474`
- modified: 1782216487

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

- hash: `5cbfb535441c3474`
- modified: 1782216487

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

- hash: `12f4bc7c02e5a38a`
- modified: 1782732731

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

- hash: `12f4bc7c02e5a38a`
- modified: 1782732731

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

- hash: `3cd7ee827f337ad5`
- modified: 1782726858

**Prompt:**
```
Premise:
bruno is trained.
bruno is trusted.
david does not advises alice.
clara advises bruno.
david is verified.
bruno does not helps alice.
Anyone who is trained and trusted is approved.
Being approved implies being verified.
From x is trusted and x is careful, it follows that x is approved.
From x trusts y and y advises z, it follows that x helps z.
For all x, y, if x advises y and y is active, then x is approved.
From x trusts y, it follows that y helps x.
From x helps y, it follows that y advises x.

Hypothesis:
clara is active.

Does the premise entail the hypothesis? The answer is yes, no, or maybe.
```

**Answer:**
```
maybe
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

- hash: `3cd7ee827f337ad5`
- modified: 1782726858

**Prompt:**
```
Premise:
[0] alice advises david.
[1] david helps clara.
[2] alice is not careful.
[3] david is not verified.
[4] bruno is not trusted.
[5] david is trained.
[6] Whenever x advises y and y helps z, x trusts z.
[7] From x trusts z, it follows that x is active.
[8] If a person is active and trusted, then that person is trained.
[9] If a person is active and careful, then that person is not trusted.
[10] Every active entity is verified.
[11] Anyone who is careful and trained is approved.
[12] When a person helps a verified person, that person is active.

Hypothesis:
alice is verified.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 6 7 10
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

- hash: `3cd7ee827f337ad5`
- modified: 1782726858

**Prompt:**
```
Premise:
[0] clara is trained.
[1] david is active.
[2] Being trained implies being trusted.
[3] Whenever x is trusted, x is not careful.

Hypothesis:
david is careful.

Candidate Facts:
[0] david is not trained.
[1] bruno is trained.
[2] david is trained.
[3] clara helps bruno.
[4] david is careful.
[5] clara advises alice.

Which candidate facts, if added to the premise, make the premise contradict the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
2
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

- hash: `3cd7ee827f337ad5`
- modified: 1782726858

**Prompt:**
```
Premise:
david advises alice.
alice trusts bruno.
david trusts alice.
alice is trusted.
clara is careful.
clara does not advises bruno.
clara is active.
For all x, y, z, if x advises y and y trusts z, then x helps z.
From x helps z, it follows that x is verified.
Whenever x helps y, y trusts x.
Whenever x helps y and y advises z, x trusts z.
When one person trusts a second person and the second advises a third person, the first helps the third.
Every approved entity that is also trained is trusted.

Question:
How many entities does bruno helps?

Answer with one integer.
```

**Answer:**
```
1
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

- hash: `605ba8997eee08d6`
- modified: 1781623594

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

- hash: `657c1f4a98174d26`
- modified: 1782727190

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

- hash: `657c1f4a98174d26`
- modified: 1782727190

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

- hash: `657c1f4a98174d26`
- modified: 1782727190

**Prompt:**
```
A: {31, 32, 10, 30, 13, 28, 9, 3}
C: {31, 32, 10, 29, 13, 28, 24, 3}
Evaluate (C-A).
```

**Answer:**
```
{24, 29}
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

- hash: `a679ad1ed8e7af35`
- modified: 1782139541

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

- hash: `dfb4735cbfb91ec8`
- modified: 1781531927

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

- hash: `0dc49fa006513b1c`
- modified: 1782206321

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

- hash: `a9e1b0e524cba840`
- modified: 1782226060

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

- hash: `0041bfe25ab3f138`
- modified: 1781614559

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

- hash: `c7a3b3f988a39f91`
- modified: 1782121546

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

- hash: `9b2bff9ec2756810`
- modified: 1782206211

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

- hash: `9b2bff9ec2756810`
- modified: 1782206211

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

- hash: `9b2bff9ec2756810`
- modified: 1782206211

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

- hash: `62304483baa971f1`
- modified: 1782721155

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

- hash: `62304483baa971f1`
- modified: 1782721155

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

- hash: `62304483baa971f1`
- modified: 1782721155

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

- hash: `4b703eedcda1b4ca`
- modified: 1782725645

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed, and each link name may also have its direction consistently reversed.

M0
a is alpha-linked to c.
a is alpha-linked to d.
c is beta-linked to a.
d is beta-linked to b.
Implies: a is gamma-linked to b.

M1
c is alpha-linked to a.
d is alpha-linked to a.
d is alpha-linked to b.
c is beta-linked to d.
Implies: a is beta-linked to d.

M2
a is alpha-linked to c.
b is alpha-linked to c.
c is alpha-linked to b.
a is beta-linked to b.
Implies: c is beta-linked to b.

M3
c is alpha-linked to b.
a is beta-linked to c.
b is beta-linked to a.
c is beta-linked to a.
Implies: c is alpha-linked to a.

Query
v is delta-linked to u.
z is delta-linked to v.
v is epsilon-linked to x.
v is gamma-linked to x.
v is gamma-linked to y.
x is gamma-linked to u.
x is gamma-linked to y.
z is gamma-linked to u.
Implies:
```

**Answer:**
```
y is epsilon-linked to x.
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

- hash: `efadf8019399e2dc`
- modified: 1782808254

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

- hash: `efadf8019399e2dc`
- modified: 1782808254

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

- hash: `efadf8019399e2dc`
- modified: 1782808254

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

- hash: `830dbc7a45a4813d`
- modified: 1782811519

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
- qty: '320.00'
  price: 316,32
- qty: '769.00'
  price: 156,18
- qty: '464.00'
  price: 27,43
- qty: '619.00'
  price: 102,76
- qty: '398.00'
  price: 420,4


SQL: SELECT * FROM dataframe ORDER BY qty DESC LIMIT 3

The answer is the result as CSV format (rows separated by newlines, values by commas). Do not include column headers..
```

**Answer:**
```
769.00,"156,18"
619.00,"102,76"
464.00,"27,43"
```

---

## [table_equivalence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

- hash: `830dbc7a45a4813d`
- modified: 1782811519

**Prompt:**
```
Do these tables contain the same data?
Ignore row order, column order, and table syntax. Match values by column name.

Table A:
revenue,city
"30,41",Mariachester
"917,62",East Nathan
"30,19",New Annbury
"813,74",Wilsonport
"900,59",West Tiffanyton


Table B:
revenue	city
813,74	Wilsonport
917,62	East Nathan
30,41	Mariachester
30,19	New Annbury
900,59	West Tiffanyton


Answer yes or no.
```

**Answer:**
```
yes
```

---

## [table_statistics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

- hash: `830dbc7a45a4813d`
- modified: 1782811519

**Prompt:**
```
Table:
x0,x1,x2,x3
-0.76,-0.77,0.42,-0.77
-1.46,-1.5,-0.93,0.34
-1.1,-1.18,0.31,-0.48
-0.96,-0.92,-1.18,-2.57
-0.14,-0.14,-0.15,-1.23
1.33,1.46,0.39,1.53
-0.85,-0.93,1.24,0.04
-0.94,-0.87,1.23,1.22
-1.26,-1.25,-3.54,-0.37


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

- hash: `5dcd3d204957fbfe`
- modified: 1782201607

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

- hash: `83ade9ed89f0b7ee`
- modified: 1782290178

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

- hash: `83ade9ed89f0b7ee`
- modified: 1782290178

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

- hash: `83ade9ed89f0b7ee`
- modified: 1782290178

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

- hash: `ebd1ce65f6b44ed5`
- modified: 1782745346

**Prompt:**
```
In this graph game, choose player's best move. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score.

Start: n0. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:60; n5:0; n6:0. Edges: n0->n1,n2; n1->n4; n2->n5; n3->n4,n5.
Legal player moves now: n1, n2.
The answer is the destination node of the best move.
```

**Answer:**
```
n1
```

---

## [game_forced_win](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

- hash: `ebd1ce65f6b44ed5`
- modified: 1782745346

**Prompt:**
```
In this graph game, decide whether player can force a win. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score. A win means final player score is greater than 50.

Start: n0. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:20; n5:100; n6:10. Edges: n0->n1,n6; n1->n3; n2->n5; n3->n4,n6.
The answer is yes or no.
```

**Answer:**
```
no
```

---

