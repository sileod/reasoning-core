# 📖 Task Gallery

50 tasks

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_line`](#lean_missing_line) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`planar_geometry_relations`](#planar_geometry_relations) · [`metamath_entailment`](#metamath_entailment) · [`metamath_core_select`](#metamath_core_select) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`unification_entailment`](#unification_entailment) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`logic_formalization`](#logic_formalization) · [`multistep_nli`](#multistep_nli) · [`defeasible_nli`](#defeasible_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`grid_navigation`](#grid_navigation) · [`reference_tracking`](#reference_tracking) · [`belief_tracking`](#belief_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_reasoning`](#regex_reasoning) · [`analogical_case_matching`](#analogical_case_matching) · [`parsing_derivation`](#parsing_derivation) · [`syntax_error_detection`](#syntax_error_detection) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_equivalence`](#table_equivalence) · [`table_statistics`](#table_statistics) · [`string_transduction`](#string_transduction) · [`game_best_move`](#game_best_move) · [`game_forced_win`](#game_forced_win) · [`qualitative_causal_reasoning`](#qualitative_causal_reasoning) · [`code_analysis`](#code_analysis) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`program_synthesis`](#program_synthesis)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

Compositional arithmetics with float/int/bool, varied operators, number theory.

**Prompt:**
```
Evaluate (-11.0 / 11 - -2).
The answer is a number.
```

**Answer:**
```
1
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

Solve relational and process math word problems involving objects and values.

**Prompt:**
```
A jar holds 12 books. 10 more books added; then cut to half. How many books are in the jar now? Answer with a number.
```

**Answer:**
```
11
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

Solve systems of linear equations or detect inconsistent/underdetermined systems.

**Prompt:**
```
Solve the following system of equations for the variable 'X1'.

System:
  2*X1 + 5*X2 - 64 = 0

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
  intro hp
  have hp1 : p1 := h0 hp
  have hp2 : p2 := h1 hp1
  __ANSWER__

LINES:
1. rfl
2. simp
3. intro hp
4. have hp1 : p1 := h0 hp
5. exact hp2
6. have hp2 : p2 := h1 hp1
```

**Answer:**
```
5
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

Determine if a candidate proof body successfully closes a theorem in Lean.

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex (s t u : Set Int) (h0 : s ⊆ t) : u ∪ s ⊆ u ∪ t := by
  ?

CANDIDATE:
decide
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
Given points: E=(-1/2, 0); I=(-1, 1); K=(0, 3/2); L=(-2, -4); M=(25/8, -3/8); N=(2, 3); P=(-7/8, 13/4); V=(-4, 1); X=(-3, -3).
Question: Where is point M relative to directed line PK?
Answer is one of: left, right, on.
```

**Answer:**
```
left
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
2. ctx => P2(x, D2)

Allowed Rules:
r1: ctx => P2(x, D4); ctx => P3(F1(x), x) ==> ctx => P2(x, D2)
r2: ctx => P2(x, D2) ==> ctx => P3(F1(x), x)
r3: ctx => P2(x, D1) ==> ctx => P2(x, D4)
r4: ctx => P2(x, D2) ==> ctx => P4(C0, F2(x, C2))

Conjecture:
ctx => P2(x, D3)
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
2. P2(y, F1(x, C1))
3. P2(F1(x, y), z)

Rule Catalog:
- r1: ctx => P2(x, y) ==> ctx => P4(P1(z, x), P1(z, y))
- r2: P1(x, D1); P2(y, F1(x, C1)) ==> P1(y, D1)
- r3: P1(x, D2); P1(y, D2) ==> P4(P5(x, y), P5(F2(y), F2(x)))
- r4: P1(x, D1); P1(y, D1); P2(F1(x, y), z) ==> P2(F1(y, x), z)

Conjecture:
P2(F1(y, x), z)

Options:
A. [r2, r4]
B. [r1, r4]
C. [r4]
D. [r2, r3]
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

Term: ((\v0.(((\v0.v0) (d a)) (\v1.(\v1.v0)))) (((\v0.(((\v1.a) v0) (v0 v0))) c) ((\v0.(\v1.(\v1.(v0 c)))) v1)))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
((d a) (\x0.(\x1.((a (c c)) (\x2.(\x3.(v1 c)))))))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

Normalize term rewrite systems under boolean, list, logic, or path rules.

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, scan subterm positions outermost-first and left-to-right. Stop at the first position matched by at least one rule, then apply the earliest matching rule in the listed order (position priority first; rule priority second).

Rules:
- mul(0,X) -> 0
- sub(X,X) -> 0
- add(X,0) -> X
- pow(X,0) -> 1
- sub(X,0) -> X

Term:
sub(add(add(mul(mul(1,sub(1,b)),1),0),0),0)

The answer is the normal form.
```

**Answer:**
```
mul(mul(1,sub(1,b)),1)
```

---

## [unification_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

Decide if an equality is implied by the most general unifier of equations.

**Prompt:**
```
Compute a most general unifier of the equations. Apply it to both sides of the candidate equality. Answer yes if the instantiated candidate terms are identical, otherwise answer no. The equations are guaranteed to be unifiable.

Equations:
- g(b) = g(x0)

Candidate:
b = x0
```

**Answer:**
```
yes
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

Find the most probable configuration of hidden variables given evidence.

**Prompt:**
```
Factor f is independently true with probability 0.3.
Factor a is independently true with probability 0.7.
The observation holds exactly when (factor f and factor a).
We observe it.
Which hidden fact values form the most probable complete explanation?

Hidden fact values:
0. a
1. not a
2. f
3. not f

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
A box contains 3 gold balls and 3 silver balls.
Two balls are drawn without replacing the first ball.
Which statement is more likely?
A: both selected balls are gold.
B: both selected balls are silver.

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
James is quiet
all old people in the room are quiet
everyone in the room is papa tagged if he is quiet
all old people in the room are quiet
everyone in the room who is yankee tagged is yankee tagged

Hypothesis:
Evan and Raymond are not quiet

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
all quiet people in the room are quiet
Raymond and Robert are respectively quiet and old

Tptp:
~((![X]:(in_the_room(X)=>(quiet(X)=>quiet(X))))&
((quiet(raymond))&(old(robert))))

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
david trusts bruno.
bruno advises clara.
david helps bruno.
david advises alice.
bruno is careful.
bruno trusts david.
clara is trusted.
Trusts relations followed by advises relations imply helps relations.
From x helps z, it follows that x is approved.
Anyone who is careful and active is not trained.
Anyone who is careful and verified is not active.
From x is trained, it follows that x is approved.
From x is trusted and x is approved, it follows that x is not trained.

Hypothesis:
bruno is approved.

Is the hypothesis true given the premise? The answer is Yes, No, or Maybe.
```

**Answer:**
```
Yes
```

---

## [defeasible_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

NLI using defeasible logic rules and negation as failure.

**Prompt:**
```
Premise:
bruno is trained.
alice is trained.
alice is blocked.
bruno is bird.
alice is bird.
alice is penguin.
bruno helps alice.
alice is careful.
clara is not flagged.
david is careful.
If x is trained, and it cannot be shown that x is blocked, then x is trusted.
By default, if x is trusted, then x is approved, unless it can be shown that x is flagged.
Being blocked implies being not trusted.
By default, if x is not trusted, then x is not approved, unless it can be shown that x is flagged.
By default, if x helps y and y is careful, then x is trusted, unless it can be shown that y is blocked.
By default, if x is trained, then x is careful, unless it can be shown that x is flagged.

Hypothesis:
bruno is approved.
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
[0] bruno advises alice.
[1] alice helps bruno.
[2] bruno advises david.
[3] david is not trusted.
[4] clara trusts alice.
[5] bruno is careful.
[6] alice is careful.
[7] alice is trusted.
[8] Whenever x advises y and y helps z, x trusts z.
[9] From x trusts z, it follows that x is trusted.
[10] If a person is active and trusted, then that person is not trained.
[11] For all x, if x is approved and x is careful, then x is trained.
[12] Whenever x is approved, x is trusted.
[13] From x is approved and x is verified, it follows that x is active.

Hypothesis:
bruno is trusted.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 8 9
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Find the missing facts from candidates to satisfy a target hypothesis.

**Prompt:**
```
Premise:
[0] clara is active.
[1] david is verified.
[2] Every active entity is careful.
[3] From x is careful, it follows that x is trusted.

Hypothesis:
david is trusted.

Candidate Facts:
[0] bruno helps clara.
[1] david is active.
[2] david is not active.
[3] alice is active.
[4] clara is approved.
[5] david advises bruno.

Which smallest set of candidate facts, if added to the premise, make the premise entail the hypothesis?
Do not include candidate facts that are not needed.
Answer with space-separated indexes.
```

**Answer:**
```
1
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

Answer multi-step logical reasoning queries over rule-based theories.

**Prompt:**
```
Premise:
david is a parent of bruno.
bruno is a parent of clara.
clara is an aunt or uncle of david.
bruno is not trusted.
david is not patient.
bruno is not kind.
From x is a parent of y, it follows that x is an ancestor of y.
Whenever x is a parent of y and y is an ancestor of z, x is an ancestor of z.
For all p, x, y, if p is a parent of x and p is a parent of y and x is different from y, then x is a sibling of y.
If one person is a sibling of another, then the second is a sibling of the first.
For all x, y, if x is a spouse of y, then y is a spouse of x.
For all x, y, z, if x is a parent of y and x is a sibling of z, then z is an aunt or uncle of y.

Question:
How many entities can be shown to be minor?

Answer with one integer.
```

**Answer:**
```
0
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

Generate action plans to achieve goals in domains like Blocksworld.

**Prompt:**
```
Objects:
object_1

Actions:
action_0(x0, x1)
  Effect: fluent_0(x1, x0)

Initial state:
True values: None
All facts not listed under True values are false.

Goal:
fluent_0(object_1, object_1)

Action format example: action_0(object1 object2).
The answer is a shortest valid plan, one action per line.
```

**Answer:**
```
action_0(object_1, object_1)
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

Identify missing elements from a shuffled sequence defined by set intension.

**Prompt:**
```
Answer with the missing elements in the ordered span of {528, 529, 532, 526, 525, 524, 533, 527} as a Python set.
```

**Answer:**
```
{530, 531}
```

---

## [set_expression](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

Evaluate complex set expressions involving union, intersection, and nested lists.

**Prompt:**
```
B = {13, 1, 19, 5, 21, 32, 14, 20}
C = {27, 21, 7, 24, 1, 20, 5, 28}
Evaluate ((C ^ B) - C).
```

**Answer:**
```
{13, 14, 19, 32}
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

Infer the canonical recurrence in a bounded polynomial DSL.

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *.
Use n. Give the simplified polynomial RHS.
Sequence: [-252, -315, -378, -441, -504, -567, -630, -693]
The answer is the RHS only.
```

**Answer:**
```
-63 * n - 252
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

Solve qualitative spatial and temporal reasoning problems over algebras.

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E3 is immediately newer than E4.
- E1 is newer than E3.
- E0 is the newest.
- E2 is newer than E1.

Which object is the 4th-newest?
The answer is one object label.
```

**Answer:**
```
E3
```

---

## [grid_navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grid_navigation.py)

Infer object grid coordinates from spatial relations and step actions.

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- A starts at (3, 2).
- B is in the same row as A.
- B is left of C.
- B starts at (1, 2).
- C is above A.
- B is below C.
- B is left of A.
- C is right of A.

Steps:
1. A moves by (0, 2).

What is the final coordinate of A? The answer is (x, y).
```

**Answer:**
```
(3, 4)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

Track locations of balls in boxes across moves, swaps, and coreferences.

**Prompt:**
```
Inventory:
- b1: green
- b2: black
- b3: black
- b4: blue

Initial State:
- b1 is in x1
- b2 is in x2
- b3 is in x3
- b4 is in x1

Moves:
- Transfer b2 from x2 into x1.
- Move it from x1 to x2.
- Move b2 from x2 to x3.
- Transfer everything in x3 into x2.
Where is b4 now? The answer is a box tag, like x1.
```

**Answer:**
```
x1
```

---

## [belief_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/belief_tracking.py)

Track ordered beliefs through observation and communication.

**Prompt:**
```
Starting locations are common knowledge. When the story says a listener accepts a location, that location becomes the listener's belief. Belief reports update the stated attribution. Unseen events and undelivered messages do not change beliefs.

Start: The ticket starts in the vase.

Story: Bob moves the ticket to the vase. No one else sees the move. Bob moves the ticket to the basket. Unknown to the others, Frank watches through a window. Bob moves the ticket to the tray. Unknown to the others, Frank watches through a window. Bob moves the ticket to the vase. Unknown to the others, Frank watches through a window. The ticket falls into the tray. Nobody sees this happen. Bob sends Frank the message "The ticket is in the tray", but it is not delivered.

Question: Where does Frank think the ticket is?

Answer with one container name.
```

**Answer:**
```
vase
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

Resolve reference chains whose shortest proof has a known depth.

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

Solve query-aware assignment, graph, scheduling, grid, set, and numeric CSPs.

**Prompt:**
```
In this 3x3 grid, each row and column contains 1..3 once.

Constraints:
1. r1c2 < r1c3
2. if r2c1 != 1, then r2c1 < r3c1
3. (r1c3 < r2c3) xor (r2c1 != 2)

Question: What is r2c3?
Answer with one name or integer.
```

**Answer:**
```
2
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

Find the shortest path or cost in weighted and unweighted directed graphs.

**Prompt:**
```
Find the shortest directed path from node 2 to node 5. If several paths are tied, return the lexicographically smallest one. Answer with space-separated nodes, or `None` if no path exists.

Graph:
Directed Edges: 0->5, 1->2, 2->0, 2->4, 3->1, 4->2, 4->5, 5->0, 5->4
```

**Answer:**
```
2 0 5
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

Determine the k-th successor of a node in a permutation digraph topology.

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
0: 0->0; 1: 1->4; 2: 2->5; 3: 3->1; 4: 4->3; 5: 5->2

Queries:
[(0, 2)]
```

**Answer:**
```
0
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
0:; 1: 1->0 1->4; 2: 2->0; 3: 3->2; 4:; 5: 5->1
```

**Answer:**
```
5 1
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

Produce a string that matches a specified regular expression pattern.

**Prompt:**
```
The answer is the shortest non-empty visible non-whitespace ASCII string that fully matches this regular expression, with lexicographic tie-breaks: \]same+?
```

**Answer:**
```
]same
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

Reason about regular expression equivalence, containment, and witnesses.

**Prompt:**
```
A = (cc)
B = c{2}
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
Yes
```

---

## [analogical_case_matching](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

Retrieve analogical cases matching query objects, links, and logical facts.

**Prompt:**
```
Match all facts by consistently renaming objects and links; each link may be reversed consistently.
Which memory case matches the query? Answer with only the index.

M0
Facts:
c is alpha-linked to a.
c is alpha-linked to b.
a is beta-linked to d.
d is beta-linked to c.
Conclusion: a is alpha-linked to c.

M1
Facts:
a is alpha-linked to e.
b is beta-linked to e.
c is beta-linked to a.
b is gamma-linked to c.
Conclusion: a is beta-linked to d.

M2
Facts:
c is alpha-linked to e.
a is beta-linked to d.
c is beta-linked to a.
a is gamma-linked to b.
Conclusion: a is alpha-linked to c.

Query facts:
u is delta-linked to z.
x is delta-linked to u.
x is delta-linked to y.
x is epsilon-linked to u.
z is gamma-linked to v.
z is gamma-linked to x.
```

**Answer:**
```
M0
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Determine the derivation production rule sequence parsing a given string.

**Prompt:**
```
(START)
start

(GRAMMAR)
R0: expr -> '(' seq ')'
R1: expr -> '⟨' seq '⟩'
R2: seq -> 
R3: expr -> '⟪' seq '⟫'
R4: expr -> '[' seq ']'
R5: expr -> '⟦' seq '⟧'
R6: seq -> expr seq
R7: expr -> '<' seq '>'
R8: start -> seq

(STRING)
⟦ [ ] ⟧ ( ) ⟦ ⟧

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R8 R6 R5 R6 R4 R2 R2 R6 R0 R2 R6 R5 R2 R2
```

---

## [syntax_error_detection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Locate syntax errors or grammatical perturbations in generated sentences.

**Prompt:**
```
(START)
start

(GRAMMAR)
seq -> 
start -> seq
expr -> '<' seq '>'
expr -> '[' seq ']'
seq -> expr seq
expr -> '(' seq ')'

(STRING)
< [ ] ( ) > ( )

Answer OK, INCOMPLETE, or ERROR token for the first invalid token. If that token repeats in STRING, append its 1-based occurrence as @occurrence.
```

**Answer:**
```
OK
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

Fill in blank tokens within a grammar-constrained sentence with prefix/suffix context.

**Prompt:**
```
(START)
start

(GRAMMAR)
expr -> '[' seq ']'
expr -> '(' seq ')'
seq -> expr seq
start -> seq
expr -> '<' seq '>'
seq -> 

(PREFIX)
[

(TEMPLATE)
___ < ___

(SUFFIX)
( ) ( )

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
Answer with the blank tokens in order, space-separated.
```

**Answer:**
```
] >
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

Answer queries on tabular data by executing SQL queries over dataframes.

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
qty|category|unit_price|date|country|status|row_id
1.00|Books|9.14|2025/06/26|France|cancelled|R0000
10.00|Clothing|10.28|2026/03/29|Spain|cancelled|R0001
5.00|Food|8.63|2025/09/12|Italy|pending|R0002
2.00|Electronics|16.89|2025/03/18|Germany|paid|R0003
1.00|Food|20.47|2026/05/13|Netherlands|paid|R0004
7.00|Office|23.45|2025/12/18|Germany|pending|R0005
3.00|Electronics|45.02|2026/02/25|Spain|paid|R0006
6.00|Clothing|20.5|2025/09/27|Spain|pending|R0007


SQL: SELECT COUNT(*) > 0
        FROM dataframe
        WHERE TRUE

The answer is the result as a single boolean (`true` or `false`).
```

**Answer:**
```
true
```

---

## [table_equivalence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

Decide if two rendered tables are semantically equivalent under mutations.

**Prompt:**
```
Do these tables contain the same data?
Ignore row order, column order, and table syntax. Match values by column name.

Table A:
job: Therapist, sports; email: walterssarah@example.com; product: Thought; qty: 1.3E2; rating: 3.5E0; country: Austria
job: Fashion designer; email: andrewroberts@example.org; product: Painting; qty: 5.89E2; rating: 1.2E0; country: British Indian Ocean Territory (Chagos Archipelago)
job: Quality manager; email: austinalexander@example.org; product: Traditional; qty: 6.09E2; rating: 2.4E0; country: Maldives
job: Herpetologist; email: hjohnston@example.org; product: Personal; qty: 2.98E2; rating: 1.2E0; country: Senegal
job: Arts development officer; email: danalucas@example.com; product: Staff; qty: 1.87E2; rating: 1.8E0; country: United States Minor Outlying Islands
job: Medical sales representative; email: williamsdalton@example.org; product: Agree; qty: 8.25E2; rating: 2.9E0; country: India
job: Adult guidance worker; email: perezrussell@example.org; product: Common; qty: 5.59E2; rating: 4E0; country: Oman
job: Rural practice surveyor; email: wendywilliams@example.org; product: Peace; qty: 3.61E2; rating: 4.1E0; country: Holy See (Vatican City State)

Table B:
country,email,product,qty,job,rating
Maldives,austinalexander@example.org,Traditional,6.09E2,Quality manager,2.4E0
Holy See (Vatican City State),wendywilliams@example.org,Peace,3.61E2,Rural practice surveyor,4.1E0
Austria,walterssarah@example.com,Thought,1.3E2,"Therapist, sports",3.5E0
British Indian Ocean Territory (Chagos Archipelago),andrewroberts@example.org,Painting,5.89E2,Fashion designer,1.2E0
Oman,perezrussell@example.org,Common,5.59E2,Adult guidance worker,4E0
Senegal,hjohnston@example.org,Personal,2.98E2,Herpetologist,1.2E0
India,williamsdalton@example.org,Agree,8.25E2,Medical sales representative,2.9E0
United States Minor Outlying Islands,danalucas@example.com,Staff,1.87E2,Arts development officer,1.8E0


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
{"x1": 0.43, "x0": 0.6, "x3": -0.08, "x2": 1.52}
{"x1": -0.71, "x0": -0.72, "x3": 0.4, "x2": 1.36}
{"x1": -0.28, "x0": -0.36, "x3": -2.46, "x2": -1.22}
{"x1": 0.68, "x0": 0.66, "x3": -1.49, "x2": -2.89}
{"x1": 0.01, "x0": 0.06, "x3": 0.46, "x2": -0.69}
{"x1": -1.57, "x0": -1.61, "x3": -1.22, "x2": -1.17}
{"x1": -0.11, "x0": -0.08, "x3": -0.36, "x2": 0.05}
{"x1": -1.77, "x0": -1.72, "x3": -3.21, "x2": -1.28}
{"x1": -0.18, "x0": -0.23, "x3": 1.08, "x2": 1.0}

Find:
column name most associated with column x1

Metric:
absolute Pearson correlation

Answer with only the identifier.
```

**Answer:**
```
x0
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

Apply string transduction operations including Caesar cipher and rotation.

**Prompt:**
```
String: eedbcdea
Operations:
- keep only d and c
- sort ascending
Answer with the final string.
```

**Answer:**
```
cdd
```

---

## [game_best_move](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

Determine the minimax-optimal move for a player in a finite graph-based game.

**Prompt:**
```
In this graph game, choose player's best move. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score.

Start: n0. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Play ends upon reaching a leaf or the move horizon; in either case, player's score is the current node's payoff. Node payoffs: n0:20; n1:0; n2:100; n3:90; n4:70; n5:100; n6:20. Edges: n0->n5,n6; n1->n2,n5; n2->n4; n3->n6.
Legal player moves now: n5, n6.
The answer is the destination node of the best move.
```

**Answer:**
```
n5
```

---

## [game_forced_win](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/game_playing.py)

Decide if a player can force a win from a given state in a graph-based game.

**Prompt:**
```
In this graph game, decide whether player can force a win. Player chooses on player turns; opponent chooses on opponent turns. Opponent minimizes player score. A win means final player score is greater than 50.

Start: n1. Turns alternate player, opponent. Move along one edge per turn, for at most 3 moves. Play ends upon reaching a leaf or the move horizon; in either case, player's score is the current node's payoff. Node payoffs: n0:40; n1:90; n2:100; n3:0; n4:20; n5:0; n6:60. Edges: n0->n5; n1->n3,n4; n2->n5; n3->n6.
The answer is yes or no.
```

**Answer:**
```
yes
```

---

## [qualitative_causal_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qualitative_causal_reasoning.py)

Reason qualitatively about causal effects and associations in graphs.

**Prompt:**
```
Assume linear causal relations, independent noise, and no exact cancellations.

- X10 directly increases X4.
- X4 directly increases X0.
- X5 directly decreases X10.
- X8 directly increases X0.
- X9 directly increases X4.

If we intervene to increase X0, what happens to X9?
Answer with: increase, decrease, no_effect, or ambiguous.
```

**Answer:**
```
no_effect
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
(p0) and (p2)

Question: List all reachable states where the property holds.
Answer as a sorted set like {s0,s2}.
````

**Answer:**
```
{s0}
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

Predict if a given Python code snippet runs successfully or raises an exception.

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(y: str, l: int) -> int:
    print(l)
    if l > 1:
        l -= l
    else:
        print(u)
    return l * 4
def f1(a: int, u: int) -> list:
    a = 0
    return []
def endpoint(x0: str, x1: int) -> int:
    return f0(x0, x1)

```
Call: `endpoint('', 1)`
The answer is `OK` if it runs successfully; otherwise the exception class name.
````

**Answer:**
```
NameError
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

Predict the return value or stdout of executing generated Python code blocks.

**Prompt:**
````
Predict the value returned by this Python call.
```python
def f0(o: list, k: list) -> list:
    a = f1(k, 4)
    return o
def f1(r: list, n: int) -> int:
    n = n
    return n + 4
def endpoint(x0: list, x1: list) -> list:
    return f0(x0, x1)

```
Call: `endpoint([0, 0, 3], [-1])`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
[0, 0, 3]
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
- replace1: str.replace(str, str, 1)
- len: len(str)
- find: str.find(str)
- sub: int - int
Bounds: strings have length <= 64; integers are between -16 and 64. Use Python string semantics.
Cost: AST nodes, then operator-count tuple in this global order (concat, substr, replace1, ite, len, find, add, sub, contains, eq_str, lt, not), then source length, then lexicographic source order.

Examples:
f(' ') = '_'
f('a') = 'a'

Return only:
def f(s: str) -> str:
    return <expression>
```

**Answer:**
```
def f(s: str) -> str:
    return s.replace(" ", "_", 1)
```

---

