# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`conjecture_entailment`](#conjecture_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_retrieval`](#analogical_case_retrieval) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`stress_constrained_continuation`](#stress_constrained_continuation) · [`table_qa`](#table_qa) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win)

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

## [conjecture_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the premises entail the conjecture.

TPTP source: SET001-3.ax

Background axioms:
- (~member(X1,X2)|~member(X1,X3)|~difference(X4,X2,X3))
- (difference(X1,X2,X3)|member(k(X1,X2,X3),X1)|member(k(X1,X2,X3),X3))
- (member(X1,X3)|~member(X1,X2)|~subset(X2,X3))

Premises:
- (member(k(X1,X2,X3),X3)|difference(X1,X2,X3)|~member(k(X1,X2,X3),X2))

Conjecture: `(difference(X1,X1,X2)|~subset(X3,X4)|~subset(X2,X3)|~difference(X5,X4,X3))`

The answer is `True` (provable) or `False` (not provable).
```

**Answer:**
```
True
```

---

## [tptp_consistency_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Which local single-clause deletions make the fixed axioms satisfiable with the negated theorem?
Answer with ordered, space-separated clause numbers.
Background axioms:
- (X3=X4|~product(X1,X2,X3)|~product(X1,X2,X4))
Negated theorem: `(multiply(identity,X1) != X1)`
Clauses:
1. (product(X1,identity,X1))
2. (product(X1,X2,multiply(X1,X2)))
3. (product(identity,X1,X1))
```

**Answer:**
```
2
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

Term: ((\v0.(((\v1.v0) (\v1.c)) (v0 (d d)))) (((\v0.(v0 v0)) d) (((\v0.(v0 b)) (a b)) ((c c) ((\v0.v0) d)))))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(((d d) (((a b) b) ((c c) d))) (((d d) (((a b) b) ((c c) d))) (d d)))
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
alice is a parent of david.
david is a parent of bruno.
bruno is kind.
clara is not adult.
clara is kind.
alice is a spouse of clara.
For all x, y, if x is a parent of y, then x is an ancestor of y.
Parent relations followed by ancestor relations imply ancestor relations.
From p is a parent of x and p is a parent of y and x is different from y, it follows that x is a sibling of y.
From x is a sibling of y, it follows that y is a sibling of x.
Whenever x is a spouse of y, y is a spouse of x.
Whenever x is a parent of y and x is a sibling of z, z is an aunt or uncle of y.

Hypothesis:
alice is an ancestor of bruno.

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
[0] david trusts bruno.
[1] bruno advises clara.
[2] bruno is careful.
[3] bruno is not approved.
[4] david is approved.
[5] clara is verified.
[6] Whenever x trusts y and y advises z, x helps z.
[7] Whenever x helps z, x is careful.
[8] Whenever x is careful and x is active, x is approved.
[9] People reached when a trusted person trusts someone are approved.
[10] Whenever x is trained and x is trusted, x is not active.
[11] If one person advises a second person, and the second helps a third person, then the first trusts the third.
[12] For all x, if x is careful and x is trusted, then x is not verified.

Hypothesis:
david is careful.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 6 7
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] david is trained.
[1] clara is active.
[2] From x is trained, it follows that x is verified.
[3] Every verified entity is not approved.

Hypothesis:
clara is approved.

Candidate Facts:
[0] david trusts clara.
[1] bruno is trained.
[2] alice is active.
[3] clara is trained.
[4] bruno is approved.
[5] clara is not trained.

Which candidate facts, if added to the premise, make the premise contradict the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
3
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno trusts alice.
alice helps david.
bruno helps alice.
bruno is not careful.
alice is verified.
bruno helps david.
bruno helps clara.
From x trusts y and y helps z, it follows that x advises z.
For all x, z, if x advises z, then x is approved.
Every helps relation creates a trusts relation in the reverse direction.
Whenever x is active and x is approved, x is verified.
Every approved entity that is also active is not trained.
Every trusted entity is active.

Question:
How many entities does david advises?

Answer with one integer.
```

**Answer:**
```
2
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
A: {7, 20, 13, 5, 4, 25, 31, 23}
C: {3, 8, 31, 19, 23, 20, 27, 13}
Evaluate (C-A).
```

**Answer:**
```
{19, 27, 3, 8}
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
a is alpha-linked to c.
b is alpha-linked to a.
c is beta-linked to d.
e is beta-linked to b.
Implies: a is beta-linked to b.

M1
a is alpha-linked to d.
c is alpha-linked to a.
a is beta-linked to d.
d is beta-linked to b.
Implies: a is beta-linked to c.

M2
b is alpha-linked to d.
d is alpha-linked to b.
d is alpha-linked to c.
c is beta-linked to a.
Implies: b is beta-linked to d.

M3
d is alpha-linked to b.
d is alpha-linked to c.
c is beta-linked to a.
c is beta-linked to d.
Implies: a is alpha-linked to c.

Query
u is delta-linked to v.
u is delta-linked to z.
x is delta-linked to y.
x is delta-linked to z.
y is delta-linked to x.
u is gamma-linked to x.
z is gamma-linked to u.
z is gamma-linked to v.
Implies:
```

**Answer:**
```
y is gamma-linked to x.
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: S -> B
R1: B -> 'if'
R2: B -> B 'amount'
R3: B -> D

(STRING)
if amount amount amount amount

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R2 R2 R2 R1
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> B
B -> B 'know'
B -> 'character'

(STRING)
know know know know know

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
>>know<<
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
start -> seq
seq -> 
seq -> expr seq
expr -> '(' seq ')'
expr -> '[' seq ']'
expr -> '<' seq '>'

(PREFIX)
< [ ] < > > < > <

(TEMPLATE)
___ ___ )

(SUFFIX)
<empty>

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
> ( )
```

---

## [stress_constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
Given this CFG and a prefix from a deep derivation, continue it: provide terminals that, appended to the prefix, complete it into a grammatical string.
The answer is the continuation terminals, space-separated.
(GRAMMAR)
S -> WHO AUX NP Vt
S -> WHY AUX NP Adj
WHO -> 'what'
WHO -> 'who'
WHY -> 'why'
WHY -> 'when'
AUX -> 'do'
NP -> 'the' N RC
NP -> 'the' N
RC -> 'that' NP Vt
N -> 'kids'
N -> 'cooks'
Vt -> 'see'
Vt -> 'like'
Vt -> 'find'
Adj -> 'happy'
Adj -> 'sad'
Adj -> 'kind'

(PREFIX)
why do the
```

**Answer:**
```
kids that the kids that the kids see see happy
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
rating,country
2.6,Seychelles
2.1,Finland
3.7,Andorra
1.4,Andorra
3.6,Grenada


SQL: SELECT ROUND(MIN(rating), 2) FROM dataframe

The answer is the result as single value.
```

**Answer:**
```
1.4
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

Start: n2. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n5:70; n6:50. Edges: n0->n6; n1->n5; n2->n3,n5; n3->n6; n4->n5.
Legal player moves now: n3, n5.
The answer is the destination node of the best move.
```

**Answer:**
```
n5
```

---

## [game_forced_win](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

**Prompt:**
```
In this graph game, decide whether player can force a win. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score. A win means final player score is greater than 50.

Start: n1. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:0; n5:20; n6:10. Edges: n0->n5; n1->n4,n6; n2->n4; n3->n4.
The answer is yes or no.
```

**Answer:**
```
no
```

---

