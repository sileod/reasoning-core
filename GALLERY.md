# 📖 Task Gallery

52 tasks

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`mgu_implied_equality`](#mgu_implied_equality) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`logic_formalization`](#logic_formalization) · [`multistep_nli`](#multistep_nli) · [`defeasible_nli`](#defeasible_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_retrieval`](#analogical_case_retrieval) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_equivalence`](#table_equivalence) · [`table_statistics`](#table_statistics) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win) · [`theory_of_mind`](#theory_of_mind) · [`qualitative_causal`](#qualitative_causal) · [`program_synthesis`](#program_synthesis)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

Compositional arithmetics with int/bool, varied operators, number theory.

**Prompt:**
```
Evaluate -15 + -4.
The answer is a number.
```

**Answer:**
```
-19
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
A jar holds some stamps. quadrupled; then 9 more stamps added. The jar now holds 53 stamps. How many stamps did it start with? Answer with a number.
```

**Answer:**
```
11
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 + X2 - 8 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
Multiple solutions
```

---

## [lean_missing_proof_line_selection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Fill `__ANSWER__` with one listed Lean proof line. Mathlib is imported.
The answer is the line number.

THEOREM:
theorem ex (s t u : Set Int) (h0 : t ⊆ s) : t ∪ u ⊆ s ∪ u := by
  __ANSWER__

LINES:
1. simp
2. assumption
3. rfl
4. intro h
5. exact h0
6. exact Set.union_subset_union h0 subset_rfl
```

**Answer:**
```
6
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex : 0 ≤ (2 : Int) ^ 2 := by
  ?

CANDIDATE:
exact sq_nonneg (2 : Int)
```

**Answer:**
```
True
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: C=(-3, -4); F=(-2, 2); J=(4, 3); M=(3, -3); N=(5, 0); S=(-2, 13); U=(-4, 5).
Definitions: J is the reflection of C across line MF. S is the 90-degree counterclockwise rotation of J about U.
Question: Which point is closer to S: J or C?
Answer is one of: J, C, tie.
```

**Answer:**
```
J
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
1. P1(x, D1)
2. P1(y, D2)

Allowed Rules:
r1: P1(x, D1); P1(y, D1) ==> P4(P3(C0, x), P3(y, F1(y, x)))
r2: P1(x, D2) ==> P1(x, D1)

Conjecture:
P2(F1(C0, x), x)
```

**Answer:**
```
False
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

Rule Catalog:
- r1: P1(x, D1); P1(y, D1) ==> P3(P2(x, F1(y)), P2(y, F1(x)))
- r2: P1(x, D2) ==> P1(x, D1)
- r3: P1(x, D1); P1(y, D1) ==> P1(F2(x, y), D1)
- r4: ctx => P1(x, D3); ctx => P5(F3(x, C2), C0) ==> ctx => P5(x, C0)

Conjecture:
P3(P2(x, F1(y)), P2(y, F1(x)))

Options:
A. [r1, r4]
B. [r2]
C. [r1, r2]
D. [r1, r3]
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

Term: ((\_5.(\v0.(((\_4.(((\_3.v0) _5) (v0 (_4 d)))) (\_1.v0)) (\v1.(a ((\_2.(\v0.((\_0.v1) (_2 b)))) d)))))) c)

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(\v0.((v0 (v0 v0)) (\v1.(a (\v0.v1)))))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- if(false,X,Y) -> Y
- or(X,X) -> X
- or(X,false) -> X
- or(true,X) -> true
- and(false,X) -> false
- and(X,X) -> X
- or(false,X) -> X
- and(X,true) -> X

Term:
if(b,and(if(c,b,a),b),and(or(not(if(false,b,true)),and(true,true)),or(not(true),true)))

The answer is the normal form.
```

**Answer:**
```
if(b,and(if(c,b,a),b),or(not(true),true))
```

---

## [mgu_implied_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Do the equations force the candidate equality under their most general unifier?
The equations are guaranteed to be unifiable.
Answer yes or no.

Equations:
- g(x0) = g(a)

Candidate:
x0 = a
```

**Answer:**
```
yes
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor a is independently true with probability 0.6.
Factor d is independently true with probability 0.1.
The observation holds exactly when (factor a or factor d).
We observe it.
Which hidden fact values form the most probable complete explanation?

Hidden fact values:
0. a
1. not a
2. d
3. not d

Choose one value for each hidden factor. Answer with space-separated indexes.
```

**Answer:**
```
0 3
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A jar contains 6 green marbles and 3 yellow marbles.
Two marbles are picked without replacing the first marble.
Which statement is more likely?
A: the first selected marble is green.
B: the first selected marble is yellow.

The answer is exactly one of: A, B, equal.
```

**Answer:**
```
A
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
Roy is the only person in the room.
Travis is papa tagged
all old people in the room are old
not everyone in the room either is not charlie tagged or is not an old person or both
all quiet people in the room are old
Kyle is not old

Hypothesis:
Roy is not not old

Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
Yes
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] there is a room.
[1] everyone in the room is not a quiet person
[2] everyone in the room is not an old person if he is yankee tagged
[3] Robert who is lima tagged is alpha tagged
[4] everyone in the room is an old person if he is lima tagged
[5] everyone outside the room is oscar tagged
Hypothesis:
Robert is not lima tagged

Which statements in the premise contradict the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
3
```

---

## [logic_formalization](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
English:
Melissa is sierra tagged
Michelle is not old

TPTP:
~(~((sierra_tagged(melissa))&
(~old(michelle))))

Does the TPTP denotation match the English? The answer is True or False.
```

**Answer:**
```
True
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
david trusts alice.
alice is trained.
david advises alice.
alice is approved.
clara is verified.
clara trusts david.
bruno is trusted.
A person is trusted when a person trusts a trained person.
All things that are trusted are approved.
If a verified person trusts someone, then that other person is active.
Every advises relation creates a helps relation in the reverse direction.
A person is active when a person advises a trusted person.
Anyone who is approved and trusted is not verified.

Hypothesis:
david is verified.

Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
No
```

---

## [defeasible_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
clara is trained.
bruno is trained.
bruno is flagged.
clara is bird.
bruno is bird.
bruno is penguin.
clara helps bruno.
bruno is careful.
david is blocked.
alice is not ab bird.
alice is careful.
From x is trained and it cannot be shown that x is flagged, it follows that x is trusted.
From x is trusted and it cannot be shown that x is blocked, it follows that x is approved.
Every flagged entity is not trusted.
If x is not trusted, and it cannot be shown that x is blocked, then x is not approved.
From x is penguin, it follows that x is ab bird.
Whenever x is bird and it cannot be shown that x is ab bird, x is approved.

Hypothesis:
bruno is approved.

Some rules use phrases like 'unless X can be shown'. This means the rule applies only when that exception is not derivable from the premise. This is different from a classical 'is not' fact.
Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
No
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] clara helps david.
[1] david is careful.
[2] clara trusts david.
[3] clara trusts bruno.
[4] bruno helps clara.
[5] alice is approved.
[6] david is verified.
[7] A person is trusted when a person helps a careful person.
[8] Every trusted entity is approved.
[9] From x advises y and y trusts z, it follows that x does not stand in the helps relation to z.
[10] Whenever x trusts y and y advises z, x does not stand in the helps relation to z.
[11] All things that are active are approved.
[12] From x advises y and x is active, it follows that y is trained.

Hypothesis:
clara is not approved.

Which premise statements are necessary to contradict the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 7 8
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] clara is trained.
[1] alice is trained.
[2] Being trained implies being verified.
[3] Every verified entity is trusted.

Hypothesis:
bruno is trusted.

Candidate Facts:
[0] bruno is not trained.
[1] david helps bruno.
[2] david is active.
[3] bruno is trained.
[4] clara is careful.
[5] bruno helps clara.

Which smallest set of candidate facts, if added to the premise, make the premise entail the hypothesis?
Do not include candidate facts that are not needed.
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
alice helps bruno.
bruno trusts david.
david is active.
alice is trained.
alice helps clara.
bruno helps clara.
david does not stand in the advises relation to clara.
If one person trusts a second person, and the second helps a third person, then the first advises the third.
For all x, z, if x advises z, then x is active.
From x helps y and y advises z, it follows that x trusts z.
For all x, if x is careful, then x is trusted.
Whenever x is careful, x is approved.
Whenever x advises y and y is verified, x is careful.

Question:
How many entities can be shown to be trusted?

Answer with one integer.
```

**Answer:**
```
0
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
Objects:
object_1, object_2, object_3, object_4

Actions:
action_0(x0)
  Effect: not fluent_2(x0), fluent_1(x0)

Initial state:
True values: fluent_2(object_3)

Goal:
fluent_1(object_3)

Action format example: action_0(object1 object2).
The answer is a shortest valid plan, one action per line.
```

**Answer:**
```
action_0(object_3)
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {688, 684, 686, 685, 682, 689, 691, 683}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{687, 690}
```

---

## [set_expression](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
A = {29, 5, 19, 30, 18, 26, 20, 13}
B = {19, 27, 20, 26, 8, 29, 9, 5}
Evaluate len((A & B)).
```

**Answer:**
```
5
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer U[n]. Max recurrence degree: 1. Ops: +, -, *, **.
Use U[n - 1] and n.
Sequence: [-3, 5, -1, 7, 1, 9, 3, 11]
Initial terms: [-3]
The answer is the RHS only.
```

**Answer:**
```
2*n - U[n - 1]
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E4 is the 5th-newest.
- E3 is immediately newer than E2.
- E0 is immediately newer than E1.
- E3 is the newest.

Which object is the 3rd-newest?
The answer is one object label.
```

**Answer:**
```
E0
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- C is right of B.
- A is above C.
- A is in the same column as B.
- B is in the same row as C.
- C is right of A.
- B is below A.

Steps:
1. C jumps to A's position offset by (2, 0).

What is the final Manhattan distance between A and C? The answer is an integer.
```

**Answer:**
```
2
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: red
- b2: green
- b3: black
- b4: black

Initial State:
- b1 is in x3
- b2 is in x2
- b3 is in x3
- b4 is in x2

Moves:
- Move b1 from x3 to x2.
- Move all contents of x3 to x2.
- Transfer b3 from x2 into x1.
- Relocate b3 from x1 to x3.
Where is b3 now? The answer is a box tag, like x1.
```

**Answer:**
```
x3
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A stern tall pilot named Rose greeted a kind tall teacher named Alan.
(2) Rose helped him.
(3) He called a kind young pilot named Lily.
(4) He watched a loud old engineer named Jane.
(5) Lily called Alan.
(6) A tall young lawyer named Ben met her.
(7) She met an old tall writer named Paul.

In sentence 7, what does the subject expression 'She' refer to?
The answer is the person's name.
```

**Answer:**
```
Lily
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
4x4 grid. Each row and column contains 1..4 once.
Clues:
- r4c2 = 2
- r2c1 = 2
- r2c3 = 1
- r1c2 = 4

What is r2c2?
Answer with one number.
```

**Answer:**
```
3
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Find the shortest directed path from node 0 to node 3. If several paths are tied, return the lexicographically smallest one. Answer with space-separated nodes, or `None` if no path exists.

Graph:
digraph { 0->3; 1->5; 3->0; 3->2; 3->4; 5->1; 5->2 }
```

**Answer:**
```
0 3
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
0: 0->3; 1: 1->1; 2: 2->4; 3: 3->2; 4: 4->0; 5: 5->5

Queries:
[(1, 1)]
```

**Answer:**
```
1
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
List all ancestors of node 2.
Order them so predecessors come before successors, with lexicographic tie-breaks.
Answer with space-separated indexes.

Graph:
Nodes [0, 1, 2, 3, 4, 5] and directed edges: (0, 2), (1, 5), (3, 0), (4, 3).
```

**Answer:**
```
4 3 0
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 5-character string that fully matches the regular expression: \\?\w\w+
```

**Answer:**
```
ÉkûkÑ
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'ab', 'c'
Negative: 'a', 'abcc', 'adca', 'bc', 'cac', 'cca', 'cccb', 'dbdc'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
ab|c
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = abac
B = aa|a
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
Memory cases list facts and a conclusion.
A case may match after consistent renaming of objects and links; each link may also be consistently reversed.
Which memory case matches the query? Answer with only its index.

M0
Facts:
a is alpha-linked to c.
a is beta-linked to b.
c is beta-linked to b.
d is beta-linked to a.
Conclusion: c is beta-linked to a.

M1
Facts:
a is alpha-linked to d.
b is alpha-linked to a.
b is beta-linked to c.
c is beta-linked to a.
Conclusion: a is alpha-linked to b.

M2
Facts:
b is alpha-linked to a.
c is alpha-linked to b.
b is beta-linked to a.
c is beta-linked to a.
Conclusion: a is alpha-linked to b.

Query facts:
u is delta-linked to y.
y is delta-linked to x.
z is delta-linked to u.
u is epsilon-linked to y.
z is epsilon-linked to y.
x is gamma-linked to z.
```

**Answer:**
```
M2
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: S -> B
R1: B -> 'big'
R2: B -> 'right' B
R3: D -> C

(STRING)
right right right right right big

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R2 R2 R2 R2 R1
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
start -> seq
seq -> 
seq -> expr seq
expr -> '(' seq ')'
expr -> '[' seq ']'
expr -> '<' seq '>'

(STRING)
< > ] ]

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
> >>]<<
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
expr -> '⟨' seq '⟩'
expr -> '⟦' seq '⟧'
expr -> '⟪' seq '⟫'

(PREFIX)
[ ]

(TEMPLATE)
___ ⟧ ___

(SUFFIX)
) ⟨ ⟩

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
⟦ ⟧ (
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
| rating   | price   |
|:---------|:--------|
| 3.70     | 3.481E2 |
| 2.30     | 5.653E1 |
| 4.90     | 1.6E2   |
| 2.60     | 4.822E2 |
| 2.80     | 4.596E2 |

SQL: SELECT COUNT(*) FROM dataframe WHERE price > 197.646

The answer is the result as single value.
```

**Answer:**
```
3
```

---

## [table_equivalence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Do these tables contain the same data?
Ignore row order, column order, and table syntax. Match values by column name.

Table A:
price,job
"30,8",Equities trader
"439,68",Race relations officer
"438,59",Video editor
"373,96",Human resources officer
"84,06",Regulatory affairs officer


Table B:
price: 438,59; job: Video editor
price: 439,68; job: Race relations officer
price: 30,8; job: Equities trader
price: 373,96; job: Human resources officer

Answer yes or no.
```

**Answer:**
```
no
```

---

## [table_statistics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Table:
row_id,x0,x1,x2,x3
R0,-0.48,-3.13,0.45,-0.52
R1,-0.55,-3.16,0.39,-0.5
R2,-0.93,-0.83,-1.46,0.91
R3,1.48,-0.03,0.32,-0.68
R4,-0.06,-0.69,-2.76,-2.2
R5,1.31,0.55,-0.22,-0.13
R6,-0.06,0.44,-0.24,1.3
R7,-1.75,1.22,2.25,0.42
R8,-1.28,-1.83,-1.49,-1.95


Find:
row_id most associated with row R0

Metric:
Pearson correlation over numeric columns

Answer with only the identifier.
```

**Answer:**
```
R1
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: ddbbaedd
Operations:
- sort descending
- reverse
Answer with the final string.
```

**Answer:**
```
abbdddde
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(x: str) -> list:
    a = 0
    print(a)
    return f1(x)
def f1(s: str) -> list:
    a = f1(s)
    return a
def endpoint(x0: str) -> list:
    return f0(x0)

```
Call: `endpoint('azy')`
The answer is `OK` if it runs successfully; otherwise the exception class name.
````

**Answer:**
```
RecursionError
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict the value returned by this Python call.
```python
def f0(l: int) -> int:
    print(l)
    return l * 6
def f1(a: str) -> int:
    b = 3
    print(b)
    return b
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(-1)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
-6
```

---

## [code_input_deduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Find the smallest integer x in [-6, 9] such that `endpoint(x) == target`.
Answer with the integer.

```python
def f0(a: int) -> int:
    a *= 4
    return a


def endpoint(x):
    return f0(x) % 5

```

Target: 4
````

**Answer:**
```
-4
```

---

## [game_best_move](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

**Prompt:**
```
In this graph game, choose player's best move. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score.

Start: n2. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:0; n5:0; n6:20. Edges: n0->n3,n5; n1->n2,n4; n2->n4,n6; n3->n4,n6.
Legal player moves now: n4, n6.
The answer is the destination node of the best move.
```

**Answer:**
```
n6
```

---

## [game_forced_win](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

**Prompt:**
```
In this graph game, decide whether player can force a win. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score. A win means final player score is greater than 50.

Start: n2. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Terminal player scores: n4:50; n5:40; n6:70. Edges: n0->n1; n1->n4; n2->n4,n6; n3->n4,n6.
The answer is yes or no.
```

**Answer:**
```
yes
```

---

## [theory_of_mind](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/theory_of_mind.py)

**Prompt:**
```
Rules: People see what happens in their room. For walking, people in the old or new room see it. When someone hears a location sentence, the listener believes that sentence, even if it is wrong. People keep old beliefs about events they did not see. For nested beliefs, use only events seen by every person in the belief chain.

Start: Alice is in the kitchen. Bob is in the kitchen. Carol is in the study. The drawer and box are in the kitchen. The tin and bag are in the study. The key is in the tin. The coin is in the tin.

Story: Alice walks to the study. Bob walks to the study. Bob puts the key in the bag. Bob walks to the kitchen. Carol puts the coin in the bag. Alice puts the key in the tin.

Question: Where does Carol think the key is?

Answer with one container name.
```

**Answer:**
```
tin
```

---

## [qualitative_causal](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qualitative_causal.py)

**Prompt:**
```
cause | effect | sign
X4 | X8 | decrease
X6 | X8 | increase
X7 | X4 | increase
X7 | X5 | increase
X9 | X5 | increase

If we intervene to increase X9, what happens to X5?
Answer with one of: increase, decrease, no_effect, ambiguous.
```

**Answer:**
```
increase
```

---

## [program_synthesis](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_program_synthesis.py)

**Prompt:**
```
Write f(s: str) -> str.

Target: return the minimum-cost StringFrag-v1 expression matching the examples.

Always allowed: s, string literals "", " ", "-", "_", and integer literals 0, 1, 2, 3.
Allowed operators for this problem:
- concat: str + str
- find: str.find(str)
- sub: int - int
- lt: int < int
Bounds: strings have length <= 64; integers are between -16 and 64. Use Python string semantics.
Cost: AST nodes, then operator-count tuple in this global order (concat, substr, replace1, ite, len, find, add, sub, contains, eq_str, lt, not), then source length, then lexicographic source order.

Examples:
f('aa') = 'aaaa '
f('-') = '-- '

Return only:
def f(s: str) -> str:
    return <expression>
```

**Answer:**
```
def f(s: str) -> str:
    return ((s + s) + " ")
```

---

