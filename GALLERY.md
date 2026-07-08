# 📖 Task Gallery

50 tasks

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_line`](#lean_missing_line) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`unification_entailment`](#unification_entailment) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`logic_formalization`](#logic_formalization) · [`multistep_nli`](#multistep_nli) · [`defeasible_nli`](#defeasible_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`grid_navigation`](#grid_navigation) · [`reference_tracking`](#reference_tracking) · [`belief_tracking`](#belief_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_matching`](#analogical_case_matching) · [`parsing_derivation`](#parsing_derivation) · [`syntax_error_detection`](#syntax_error_detection) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_equivalence`](#table_equivalence) · [`table_statistics`](#table_statistics) · [`string_transduction`](#string_transduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win) · [`qualitative_causal_reasoning`](#qualitative_causal_reasoning) · [`code_analysis`](#code_analysis) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`program_synthesis`](#program_synthesis)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

Compositional arithmetics with float/int/bool, varied operators, number theory.

**Prompt:**
```
Evaluate (-4.1) + 1 + (bit_count(44)).
The answer is a number.
```

**Answer:**
```
-0.1
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

Solve relational and process math word problems involving objects and values.

**Prompt:**
```
Wei has 8 fewer apples than Iris. Ravi has a quarter as many apples as Iris. Iris has 12 apples. How many apples does Wei have? Answer with s a number.
```

**Answer:**
```
4
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

Solve systems of linear equations or detect inconsistent/underdetermined systems.

**Prompt:**
```
Solve the following system of equations for the variable 'X1'.

System:
  -2*X1 + X2 - 36 = 0

The answer is the value of X1, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
Multiple solutions
```

---

## [lean_missing_line](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

Select the correct proof line to fill a hole in a compilation-checked Lean proof.

**Prompt:**
```
Fill `__ANSWER__` with one listed Lean proof line. Mathlib is imported.
The answer is the line number.

THEOREM:
theorem ex (p0 p1 p2 : Prop) (h0 : p0 → p1) (h1 : p1 → p2) : p0 → p2 := by
  __ANSWER__

LINES:
1. rfl
2. simp
3. exact h0
4. intro x hx
5. exact h1
6. tauto
```

**Answer:**
```
6
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

Determine if a candidate proof body successfully closes a theorem in Lean.

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex (p2 p4 : Prop) : p2 → (p2 ∨ p4) := by
  ?

CANDIDATE:
linarith
```

**Answer:**
```
False
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

Answer geometry queries about point intersections, angles, and distances.

**Prompt:**
```
Given points: C=(-1, -4); D=(1, 1); H=(3, 1); K=(-192/25, -69/25); P=(-4, 0); T=(1, 0); U=(-67/25, -44/25).
Definitions: U is the projection of D onto line CP. K is the translation of P by vector DU.
Question: Is point H on segment KT?
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
r1: ctx => P2(x, D1) ==> ctx => P2(x, D3)
r2: ctx => P2(x, D3); ctx => P3(F1(x), C0) ==> ctx => P3(x, C0)

Conjecture:
ctx => P2(x, D2)
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
2. P1(y, D1)

Rule Catalog:
- r1: P1(x, D2); P1(y, D2) ==> P3(P2(F1(x), y), P2(F1(y), x))
- r2: ctx => P1(x, D2) ==> ctx => P3(P5(x, C0), P5(F1(x), C0))
- r3: P1(x, D1) ==> P1(x, D2)
- r4: ctx => P1(x, D2); ctx => P1(y, D2) ==> ctx => P2(F3(F2(x, y), x), y)

Conjecture:
P3(P2(F1(x), y), P2(F1(y), x))

Options:
A. [r1, r3]
B. [r3, r4]
C. [r2, r3]
D. [r3]
```

**Answer:**
```
A
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

Reduce lambda calculus terms to normal form with renaming and shadowing.

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: ((\_4.((((\_5._4) (\v0.v0)) ((\_3.a) c)) (\v0.v0))) (\_2.((\_0.((\_1._2) _2)) b)))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(a (\v0.v0))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

Normalize term rewrite systems under boolean, list, logic, or path rules.

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- join(X,dot) -> X
- parent(join(X,Y)) -> X
- join(root,X) -> norm(X)
- base(join(X,Y)) -> Y
- norm(norm(X)) -> norm(X)
- join(join(X,Y),Z) -> join(X,join(Y,Z))

Term:
parent(join(join(join(root,base(norm(c))),dot),dot))

The answer is the normal form.
```

**Answer:**
```
norm(base(norm(c)))
```

---

## [unification_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

Decide if an equality is implied by the most general unifier of equations.

**Prompt:**
```
Do the equations force the candidate equality under their most general unifier?
The equations are guaranteed to be unifiable.
Answer yes or no.

Equations:
- g(x0) = g(c)

Candidate:
x0 = g(c)
```

**Answer:**
```
no
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

Find the most probable configuration of hidden variables given evidence.

**Prompt:**
```
Factor d is independently true with probability 0.1.
Factor a is independently true with probability 0.7.
The observation holds exactly when (factor d and factor a).
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
0 2
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

Predict the most probable outcome or select hidden factor values in ProbLog.

**Prompt:**
```
A tray contains 7 white tiles and 7 black tiles.
Two tiles are selected without replacing the first tile.
Which statement is more likely?
A: the first selected tile is white.
B: the first selected tile is black.

The answer is exactly one of: A, B, equal.
```

**Answer:**
```
equal
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

First-order logic natural language inference via automated theorem proving.

**Prompt:**
```
Premise:
there is a room.
all quiet people in the room are old
Teresa is alpha tagged
Tracy is not echo tagged
Tracy and Teresa are respectively old and quiet
no old person outside the room is old

Hypothesis:
Tracy is quiet

Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
Maybe
```

---

## [logic_formalization](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

Translate natural language premises into formal first-order logic formulas.

**Prompt:**
```
English:
Connor is not quiet
more than one person in the room is old

TPTP:
(((~quiet(connor))&
((?[X,Y]:(in_the_room(X)&in_the_room(Y)&(old(X)&old(Y))&(X!=Y)))))|fresh_condition(fresh_object))

Does the TPTP denotation match the English? The answer is True or False.
```

**Answer:**
```
False
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Multi-hop natural language inference over chained logic facts and rules.

**Prompt:**
```
Premise:
clara trusts bruno.
bruno is careful.
clara trusts alice.
alice is careful.
david is approved.
bruno advises alice.
clara is careful.
bruno does not stand in the helps relation to david.
Whenever x trusts y and y is careful, x is trusted.
Being trusted implies being trained.
Every careful entity that is also trusted is trained.
Whenever x is trusted and x is verified, x is not approved.
Every trained entity that is also approved is not trusted.
From x helps y, it follows that y does not stand in the advises relation to x.

Hypothesis:
clara is not trained.

Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
No
```

---

## [defeasible_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

NLI using defeasible logic rules and negation as failure.

**Prompt:**
```
Premise:
david is trained.
clara is trained.
clara is blocked.
david is bird.
clara is bird.
clara is penguin.
david helps clara.
clara is careful.
bruno is flagged.
alice is ab bird.
bruno is trained.
From x is trained and it cannot be shown that x is blocked, it follows that x is trusted.
For all x, if x is trusted and it cannot be shown that x is flagged, then x is approved.
From x is blocked, it follows that x is not trusted.
If x is not trusted, and it cannot be shown that x is flagged, then x is not approved.
For all x, if x is trained and it cannot be shown that x is flagged, then x is careful.
For all x, if x is penguin, then x is ab bird.
For all x, if x is bird and it cannot be shown that x is ab bird, then x is approved.

Hypothesis:
clara is not approved.

Some rules use phrases like 'unless X can be shown'. This means the rule applies only when that exception is not derivable from the premise. This is different from a classical 'is not' fact.
Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
Yes
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Retrieve the specific premise indexes required to prove a logical hypothesis.

**Prompt:**
```
Premise:
[0] bruno trusts alice.
[1] alice is careful.
[2] bruno advises alice.
[3] clara is verified.
[4] bruno is active.
[5] clara trusts david.
[6] alice trusts david.
[7] If a person trusts a careful person, then that person is trusted.
[8] From x is trusted, it follows that x is trained.
[9] Being careful implies being trusted.
[10] Being approved implies being trained.
[11] Whenever x trusts y and y advises z, x helps z.
[12] From x advises y, it follows that y does not stand in the helps relation to x.

Hypothesis:
bruno is trained.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 7 8
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Find the missing facts from candidates to satisfy a target hypothesis.

**Prompt:**
```
Premise:
[0] alice helps clara.
[1] alice is trained.
[2] From x helps y and y is approved, it follows that x is verified.
[3] For all x, if x is verified, then x is careful.

Hypothesis:
alice is careful.

Candidate Facts:
[0] david is approved.
[1] clara is not approved.
[2] clara is verified.
[3] clara is careful.
[4] clara is approved.
[5] david is verified.

Which smallest set of candidate facts, if added to the premise, make the premise entail the hypothesis?
Do not include candidate facts that are not needed.
Answer with space-separated indexes.
```

**Answer:**
```
4
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Answer multi-step logical reasoning queries over rule-based theories.

**Prompt:**
```
Premise:
david advises alice.
alice trusts clara.
david helps alice.
clara is approved.
clara does not stand in the advises relation to bruno.
bruno is trained.
bruno is verified.
For all x, y, z, if x advises y and y trusts z, then x helps z.
For all x, z, if x helps z, then x is active.
People reached when a careful person advises someone are trusted.
Whenever x trusts y, y helps x.
For all x, y, if x trusts y and x is active, then y is trained.
Being active implies being not verified.

Question:
Which entities can be shown to be trusted?

Answer with names in alphabetical order, comma-separated, or 'none'.
```

**Answer:**
```
none
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

Generate action plans to achieve goals in domains like Blocksworld.

**Prompt:**
```
Objects:
object_1, object_2, object_3, object_4, object_5

Actions:
action_1(x0)
  Effect: fluent_0, fluent_3(x0)

Initial state:
True values: None

Goal:
fluent_3(object_5)

Action format example: action_0(object1 object2).
The answer is a shortest valid plan, one action per line.
```

**Answer:**
```
action_1(object_5)
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

Identify missing elements from a shuffled sequence defined by set intension.

**Prompt:**
```
Set_A: {98, 100, 97, 94, 101, 92, 93}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{95, 96, 99}
```

---

## [set_expression](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

Evaluate complex set expressions involving union, intersection, and nested lists.

**Prompt:**
```
A = {7, 23, 15, 17, 12, 1, 6, 2}
C = {6, 16, 3, 13, 1, 28, 18, 27}
Evaluate (C - (C & A)).
```

**Answer:**
```
{3, 13, 16, 18, 27, 28}
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

Induce recurrence relations from visible terms of a numeric sequence.

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *, **.
Use n.
Sequence: [-4, -2, 0, 2, 4, 6, 8, 10]
Initial terms: []
The answer is the RHS only.
```

**Answer:**
```
-4 + 2*n
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

Solve qualitative spatial and temporal reasoning problems over algebras.

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E4 is the newest.
- E2 is newer than E0.
- E1 is newer than E2.
- E1 is newer than E3.

Which object is the 2nd-newest?
The answer is one object label.
```

**Answer:**
```
E1
```

---

## [grid_navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grid_navigation.py)

Infer object grid coordinates from spatial relations and step actions.

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- A starts at (2, 2).
- A is above B.
- A is above C.
- C is left of A.
- B is in the same column as C.
- B is above C.
- A is right of B.

Steps:
1. A and C swap positions.

What is the final coordinate of C? The answer is (x, y).
```

**Answer:**
```
(2, 2)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

Track locations of balls in boxes across moves, swaps, and coreferences.

**Prompt:**
```
Inventory:
- b1: red
- b2: white
- b3: blue
- b4: white

Initial State:
- b1 is in x1
- b2 is in x2
- b3 is in x3
- b4 is in x1

Moves:
- Transfer b2 from x2 into x1.
- Move b3 from x3 to x2.
- Move all contents of x2 to x1.
- Relocate b1 from x1 to x3.
Where is b3 now? The answer is a box tag, like x1.
```

**Answer:**
```
x1
```

---

## [belief_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/belief_tracking.py)

Track agent beliefs, locations, and actions for Theory of Mind scenarios.

**Prompt:**
```
Rules: People see what happens in their room. For walking, people in the old or new room see it. When someone is told a location, the listener believes it. People keep old beliefs about events they did not see.

Start: Alice is in the study. Bob is in the study. Carol is in the study. The drawer and box are in the kitchen. The tin and bag are in the study. The key is in the bag. The coin is in the box.

Story: Bob puts the key in the tin. Alice puts the key in the bag. Carol puts the key in the tin. Bob walks to the kitchen. Bob puts the coin in the drawer. Carol puts the key in the bag.

Question: Where does Bob think the key is?

Answer with one container name.
```

**Answer:**
```
tin
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

Resolve multi-hop entity coreference chains and pronouns in natural text.

**Prompt:**
```
(1) A quiet stern engineer named Sam watched a kind loud teacher named Noah.
(2) A kind young pilot named Alan met Noah.
(3) Noah called the pilot.
(4) Sam watched Noah.
(5) The teacher questioned an old stern chef named Mary.
(6) The teacher helped her.
(7) An old tall engineer named Adam helped her.

In sentence 7, what does the object expression 'her' refer to?
The answer is the person's name.
```

**Answer:**
```
Mary
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

Solve constraint satisfaction problems (grids, attributes, linear) using Z3.

**Prompt:**
```
4x4 grid. Each row and column contains 1..4 once.
Clues:
- r3c2 = 2
- r4c3 = 2
- r3c1 = 3
- r2c3 = 1

What is r3c3?
Answer with one number.
```

**Answer:**
```
4
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

Find the shortest path or cost in weighted and unweighted directed graphs.

**Prompt:**
```
Find the shortest directed path from node 0 to node 2. If several paths are tied, return the lexicographically smallest one. Answer with space-separated nodes, or `None` if no path exists.

Graph:
Directed Edges: 0->2, 0->5, 1->5, 2->4, 3->0
```

**Answer:**
```
0 2
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

Determine the k-th successor of a node in a permutation digraph topology.

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
Adjacency Dictionary (source to targets): {0: [2], 1: [5], 2: [4], 3: [0], 4: [1], 5: [3]}

Queries:
[(3, 2)]
```

**Answer:**
```
2
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

Resolve recursive node prerequisites in directed acyclic graphs (DAGs).

**Prompt:**
```
List all ancestors of node 4.
Order them so predecessors come before successors, with lexicographic tie-breaks.
Answer with space-separated indexes.

Graph:
digraph { 0->4; 2->0; 2->1; 2->4; 2->5; 3->4; 5->0; 5->3 }
```

**Answer:**
```
2 5 0 3
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

Produce a string that matches a specified regular expression pattern.

**Prompt:**
```
The answer is a 1-character string that fully matches the regular expression: [^Yfw]*
```

**Answer:**
```
o
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

Reason about regular expression equivalence, containment, and witnesses.

**Prompt:**
```
A = c|a+
B = bbc?
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
No
```

---

## [analogical_case_matching](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

Retrieve analogical cases matching query objects, links, and logical facts.

**Prompt:**
```
Memory cases list facts and a conclusion.
A case may match after consistent renaming of objects and links; each link may also be consistently reversed.
Which memory case matches the query? Answer with only its index.

M0
Facts:
b is alpha-linked to d.
c is beta-linked to e.
d is beta-linked to b.
e is beta-linked to a.
Conclusion: a is beta-linked to b.

M1
Facts:
d is alpha-linked to c.
a is beta-linked to c.
b is beta-linked to a.
e is beta-linked to b.
Conclusion: d is beta-linked to e.

M2
Facts:
d is alpha-linked to a.
a is beta-linked to c.
b is beta-linked to c.
c is beta-linked to b.
Conclusion: e is beta-linked to d.

Query facts:
u is delta-linked to y.
v is delta-linked to y.
z is epsilon-linked to u.
u is gamma-linked to v.
v is gamma-linked to y.
y is gamma-linked to x.
```

**Answer:**
```
M1
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Determine the derivation production rule sequence parsing a given string.

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
[ [ ] ] [ ( ) ] < > [ ]

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R4 R2 R4 R1 R1 R2 R4 R2 R3 R1 R1 R2 R5 R1 R2 R4 R1 R1
```

---

## [syntax_error_detection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Locate syntax errors or grammatical perturbations in generated sentences.

**Prompt:**
```
(GRAMMAR)
S -> D
D -> 'open'
D -> D 'ability'

(STRING)
open ability ability open ability

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
ability >>open<<
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Fill in blank tokens within a grammar-constrained sentence with prefix/suffix context.

**Prompt:**
```
(GRAMMAR)
S -> C
C -> 'small'
C -> 'small' C

(PREFIX)
<empty>

(TEMPLATE)
small ___ small ___ ___

(SUFFIX)
small

Fill in the 3 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 5 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
small small small small small
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

Answer queries on tabular data by executing SQL queries over dataframes.

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
company|qty
Gay-Campbell|2.66E2
Martinez-Howe|5.4E1
Ramirez PLC|3.82E2
Cain, Hendrix and Johnson|4.66E2
Andersen, Mendez and Norris|2.6E1


SQL: SELECT COUNT(DISTINCT company) FROM dataframe

The answer is the result as single value.
```

**Answer:**
```
5
```

---

## [table_equivalence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

Decide if two rendered tables are semantically equivalent under mutations.

**Prompt:**
```
Do these tables contain the same data?
Ignore row order, column order, and table syntax. Match values by column name.

Table A:
| price   | qty    |
|:--------|:-------|
| 103,48  | 937.00 |
| 24,26   | 648.00 |
| 131,57  | 428.00 |
| 499,12  | 526.00 |
| 136,94  | 428.00 |

Table B:
qty,price
428.00,"136,94"
648.00,"24,26"
428.00,"131,57"
526.00,"499,12"
937.00,"103,48"


Answer yes or no.
```

**Answer:**
```
yes
```

---

## [table_statistics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

Compute statistical metrics (Pearson correlation, eta2, NMI) on tables.

**Prompt:**
```
Table:
x0	x1	x2	x3
-1.23	-1.13	0.75	1.8
0.65	0.65	0.85	0.71
-0.26	-0.3	-2.22	1.11
0.58	0.55	-0.57	-1.03
-0.86	-0.92	-1.52	-0.69
-0.09	-0.16	1.87	0.02
0.04	-0.01	-0.45	-0.23
1.33	1.27	0.28	1.75
0.38	0.57	0.67	0.48


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

Apply string transduction operations including Caesar cipher and rotation.

**Prompt:**
```
String: cceccaaa
Operations:
- caesar shift by 3
- replace c with b
Answer with the final string.
```

**Answer:**
```
ffhffddd
```

---

## [game_best_move](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

Determine the minimax-optimal move for a player in a finite graph-based game.

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

Decide if a player can force a win from a given state in a graph-based game.

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

## [qualitative_causal_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qualitative_causal_reasoning.py)

Perform qualitative causal reasoning (increase, decrease, ambiguous) on graphs.

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

## [code_analysis](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_analysis.py)

Analyze toy finite-state Python-like programs with CTL temporal formulas.

**Prompt:**
````
Program:
```python
import random

phase, x = 'idle', 0

def step():
    global phase, x
    if phase == 'idle':
        phase = 'wait'
    elif phase == 'wait':
        x = min(x + 1, 1)
    else:
        phase = 'idle'
```

Reachable states:
s0=(phase=idle, x=0); s2=(phase=wait, x=0); s3=(phase=wait, x=1)

Predicates:
p0 := x == 0
p1 := phase == 'wait'
p2 := phase == 'idle'

Property:
some next step can reach a state where p0

Question: Considering all possible random choices, does the property hold from the initial state?
Answer with exactly Yes or No.
````

**Answer:**
```
Yes
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

Predict if a given Python code snippet runs successfully or raises an exception.

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(i: list, l: int) -> int:
    print(l)
    print(l)
    return l + 3
def f1(d: int, c: int) -> str:
    d = 4 * 7
    c = "cat"
    return c
def endpoint(x0: list, x1: int) -> int:
    return f0(x0, x1)

```
Call: `endpoint([], 2)`
The answer is `OK` if it runs successfully; otherwise the exception class name.
````

**Answer:**
```
OK
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

Predict the return value or stdout of executing generated Python code blocks.

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
