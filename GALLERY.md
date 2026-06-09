# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`equation_system`](#equation_system) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`lean_proof_repair`](#lean_proof_repair) · [`conjecture_entailment`](#conjecture_entailment) · [`finite_interpretation_check`](#finite_interpretation_check) · [`bayesian_association`](#bayesian_association) · [`bayesian_intervention`](#bayesian_intervention) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`planning`](#planning) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_isomorphism`](#graph_isomorphism) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`lexical_knowledge`](#lexical_knowledge) · [`decision_path_parsing`](#decision_path_parsing) · [`continuation`](#continuation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_conversion`](#table_conversion) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`code_execution`](#code_execution) · [`diff_prediction`](#diff_prediction)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate round(1 % 5 + -3).
The answer is a number.
```

**Answer:**
```
-2
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 + 2 = 0
  X2 + 25 = 0

The answer is the numerical value for X2, or 'No solution' / 'Multiple solutions' if a unique numerical solution does not exist.
```

**Answer:**
```
-25
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Decide whether the candidate Lean 4 tactic body closes the theorem.
The answer is exactly True or False.

THEOREM WITH HOLE:
theorem ex (p0 p4 : Prop)  : (p4 ∧ p0) → p0 := by
  ?

CANDIDATE:
tauto
```

**Answer:**
```
True
```

---

## [lean_proof_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
The Lean 4 theorem below has a broken proof. Replace the proof body with one that compiles. Mathlib is imported. The answer is only the replacement tactic block.

theorem ex (x y : List Nat)  : (x ++ y).length = x.length + y.length := by
  rfl

```

**Answer:**
```
simp [List.length_append, Nat.add_assoc]
```

---

## [conjecture_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the given premises entail the conjecture (i.e., the conjecture is provable) using Superposition/Resolution/Paramodulation.

Domain: Algebra

Premises:
- (member(f39(X1,X2),X1)|~group(X1,X2))
- (member(X3,X2)|~subset(X1,X2)|~member(X3,X1))

Conjecture: `(member(f39(X1,X2),X3)|~subset(X1,X3)|~group(X1,X2))`

The answer is `True` (provable) or `False` (not provable).
```

**Answer:**
```
True
```

---

## [finite_interpretation_check](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Check whether the finite interpretation satisfies all listed requirements.
Domain: **Topology**
Background axioms, for context only:
- cnf(boundary_70,axiom,(element_of_set(X1,closure(X2,X3,X4))|~element_of_set(X1,boundary(X2,X3,X4))))
Requirements:
Variables are universally quantified. A requirement marked `False` is satisfied iff the formula is false for at least one assignment.
1. True: `(element_of_set(X1,X3)|~element_of_set(X1,intersection_of_members(X2))|~element_of_collection(X3,X2))`
2. False: `(element_of_set(X1,closure(X2,X3,X4))|~element_of_collection(boundary(X2,X3,X4),X5)|~element_of_set(X1,intersection_of_members(X5)))`

Finite interpretation:
Domain:
{0, 1}

Constants:
(none)

Functions:
boundary:
  (0, 0, 0) -> 0
  (0, 0, 1) -> 0
  (0, 1, 0) -> 0
  (0, 1, 1) -> 0
  (1, 0, 0) -> 0
  (1, 0, 1) -> 0
  (1, 1, 0) -> 0
  (1, 1, 1) -> 0
closure:
  (0, 0, 0) -> 1
  (0, 0, 1) -> 0
  (0, 1, 0) -> 0
  (0, 1, 1) -> 0
  (1, 0, 0) -> 0
  (1, 0, 1) -> 0
  (1, 1, 0) -> 0
  (1, 1, 1) -> 0
intersection_of_members:
  (0,) -> 0
  (1,) -> 1

Predicates:
element_of_collection:
  (0, 0) -> true
  (0, 1) -> false
  (1, 0) -> false
  (1, 1) -> false
element_of_set:
  (0, 0) -> true
  (0, 1) -> false
  (1, 0) -> false
  (1, 1) -> false
The answer is `True` or `False`.
```

**Answer:**
```
True
```

---

## [bayesian_association](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/causal_reasoning.py)

**Prompt:**
```
System:
P(X_0) = {'0': 0.1, '1': 0.9} 
X_3 ~ Noisy-AND(leak=0.0, weights={'X_0': 0.1, 'X_2': 0.8}) 
P(X_2) = {'0': 0.3, '1': 0.7} 
P(X_1) = {'0': 0.6, '1': 0.4}
Observed conditions:
Without further Observation/Knowledge of other variable.
Task: Compute probability distribution for X_0 (possible values: [0, 1]).

The answer is a Python dict mapping each value to its probability, rounded to 1 decimals.
Example: {0: 0.1, 1: 0.9}
```

**Answer:**
```
{0: 0.1, 1: 0.9}
```

---

## [bayesian_intervention](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/causal_reasoning.py)

**Prompt:**
```
System:
P(X_0) = {'0': 0.5, '1': 0.5} 
X_2 ~ Noisy-OR(leak=0.0, weights={'X_0': 0.6, 'X_1': 0.6}) 
P(X_1) = {'0': 0.1, '1': 0.9} 
X_3 ~ Noisy-OR(leak=0.0, weights={'X_1': 0.3, 'X_2': 0.8})
Observed conditions:
Doing/Imposing that the state X_1 is equal to 1. Observing/Knowing that the state X_3 is equal to 0
Task: Compute probability distribution for X_0 (possible values: [0, 1]).

The answer is a Python dict mapping each value to its probability, rounded to 1 decimals.
Example: {0: 0.1, 1: 0.9}
```

**Answer:**
```
{0: 0.6, 1: 0.4}
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
Lee is the only person in the room.
everyone in the room who is sierra tagged is not old
all old people in the room are old
Daniel is not kilo tagged
all old people in the room are old
at least one person in the room is not sierra tagged
Hypothesis:
Lee is not sierra tagged

If the Premise entails the Hypothesis, the label is 'entailment'.
If the Premise contradicts the Hypothesis, the label is 'contradiction'.
If neither, the label is 'neutral'.
The answer is exactly one word: neutral, contradiction, or entailment.
```

**Answer:**
```
entailment
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] Rodney is the only person in the room.
[1] Not all Bellbridge's houses are purple.
[2] Rodney and Gilbert are respectively quiet and quiet
[3] Gilbert is a quiet person and is a quiet person
[4] all old people in the room are old
[5] everyone in the room who is old is not an old person
Hypothesis:
Rodney is an old quiet person

Which statements in the premise contradict the hypothesis?
The answer is the list of supporting statements, e.g. [0, 6, 7].
```

**Answer:**
```
[0, 5]
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
Elena is charlie tagged.
Elena is delta tagged.
David is echo tagged.
Elena is echo tagged.
David is not delta tagged.
Alice is delta tagged.
Alice is echo tagged.
Clara is foxtrot tagged.
Bruno is gamma tagged.
Alice is gamma tagged.
From x is charlie tagged and x is delta tagged, it follows that x is echo tagged.
From x is echo tagged, it follows that x is foxtrot tagged.
Anyone who is echo tagged and bravo tagged is alpha tagged.
For all x, if x is charlie tagged and x is bravo tagged, then x is echo tagged.
Whenever x is delta tagged and x is alpha tagged, x is echo tagged.
If a person is echo tagged and gamma tagged, then that person is kappa tagged.
Anyone who is charlie tagged and foxtrot tagged is kappa tagged.
Every gamma-tagged person who is echo tagged is not charlie tagged.
Every foxtrot-tagged person is kappa tagged.
For all x, if x is gamma tagged and x is alpha tagged, then x is kappa tagged.
Anyone beta-linked to someone who is alpha-linked to a third person is gamma-linked to that third person.
For all x, y, if x is delta-related to y, then y is not omega-connected to x.
People reached by a omega-connected relation from a alpha-tagged person are echo tagged.
Anyone delta-related to a delta-tagged person is charlie tagged.

Hypothesis:
Elena is alpha tagged.

If the Premise entails the Hypothesis, the label is 'entailment'.
If the Premise contradicts the Hypothesis, the label is 'contradiction'.
If neither, the label is 'neutral'.
The answer is exactly one word: neutral, contradiction, or entailment.
```

**Answer:**
```
neutral
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] Elena is gamma-linked to Clara.
[1] Clara is gamma tagged.
[2] Bruno is delta-related to Elena.
[3] Alice is bravo tagged.
[4] Bruno is gamma tagged.
[5] David is gamma-linked to Bruno.
[6] Alice is foxtrot tagged.
[7] Elena is kappa tagged.
[8] David is bravo tagged.
[9] Elena is bravo tagged.
[10] Whenever x is gamma-linked to y and y is gamma tagged, x is alpha tagged.
[11] Every alpha-tagged person is delta tagged.
[12] If a person is gamma tagged and foxtrot tagged, then that person is bravo tagged.
[13] If a person is delta tagged and echo tagged, then that person is kappa tagged.
[14] Every gamma-tagged person who is foxtrot tagged is alpha tagged.
[15] Anyone who is alpha tagged and bravo tagged is charlie tagged.
[16] From x is delta tagged and x is alpha tagged, it follows that x is not echo tagged.
[17] For all x, if x is foxtrot tagged, then x is gamma tagged.
[18] From x is beta-linked to y and y is omega-connected to z, it follows that x is gamma-linked to z.
[19] Every charlie-tagged person who is echo tagged is foxtrot tagged.
[20] Every bravo-tagged person who is foxtrot tagged is charlie tagged.
[21] Whenever x is echo tagged, x is not delta tagged.
[22] If a person is echo tagged and charlie tagged, then that person is kappa tagged.
[23] For all x, if x is gamma tagged and x is bravo tagged, then x is delta tagged.

Hypothesis:
Elena is echo tagged.

Which premise statements are necessary to contradict the hypothesis, meaning removing any one of them breaks that result?
The answer is a list of indices, e.g. [0, 1].
```

**Answer:**
```
[0, 1, 10, 11, 16]
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] Elena is delta-related to Alice.
[1] Clara is bravo tagged.
[2] From x is delta-related to y and y is bravo tagged, it follows that x is charlie tagged.
[3] Whenever x is charlie tagged, x is echo tagged.

Hypothesis:
Elena is echo tagged.

Candidate additional facts:
[0] Bruno is bravo tagged.
[1] Alice is not bravo tagged.
[2] Alice is alpha tagged.
[3] Alice is bravo tagged.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
Return the smallest list of candidate indices, e.g. [0, 2].
```

**Answer:**
```
[3]
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
[OBJECTS]
object_1, object_2, object_3

[ACTIONS]
action_0(x0)
  Requires: fluent_1(x0)
  Effect: not fluent_1(x0)
action_1(x0)
  Requires: (not fluent_0), (not fluent_1(x0))
  Effect: fluent_0, fluent_1(x0)

[STATE]
Initial true values: None

[GOAL]

fluent_0, fluent_1(object_2)
The answer is the plan.
Answer format: Multiple lines, one action per line: action(obj1, obj2)
```

**Answer:**
```
    action_1(object_2)
```

---

## [set_intersection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {915, 362, 299, 427, 160, 76, 57, 776}
Set2: {911, 776, 54, 362, 160, 346}
The answer is the intersection of Set1 and Set2 as a Python set: {elem_1, elem_2, ..., elem_n}.
```

**Answer:**
```
{160, 362, 776}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {536, 540, 539, 537, 535, 533, 542, 538}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{534, 541}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: [2, 13, 2, 8, 18, 7, 8, 1, 8, 11]
How many times does 8 appear? The answer is a number.
```

**Answer:**
```
3
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {'nx', 'gm', 'akp', 'ft', 'adk', 'au', 'wy', 'ajp'}
Set2: {'wy', 'ft', 'cr', 'akp', 'au', 'ajp', 'gm', 'adk', 'nx'}
The answer is True if Set1 and Set2 contain exactly the same elements, False otherwise.
```

**Answer:**
```
False
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer a recurrence for a sequence indexed from 0: [U0, U1, ..., U7].
Max recurrence degree: 0.

Allowed binary ops: +, -, *, **
- Previous terms must be referenced exactly as: U[n - 1] ... U[n - 0]
- You may use "n" (current index).
- The answer is the right-hand side only (do not write "U[n] =").
- Your recurrence degree must be <= 0.

Sequence: [0, 1, 2, 3, 4, 5, 6, 7]
Degree of recurrence: 0
Initial terms: []

The answer must hold for all n >= d and be as simple as possible.
```

**Answer:**
```
n
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 entities labeled 0 through 4.
You are given the following facts (read 'i rel j' as 'entity i is rel to entity j'):
  0 overlaps 3
  2 overlapped-by 0
  4 meets 3
  1 overlapped-by 0
  1 overlapped-by 4
  1 started-by 2

What is the relation of the vertical extent of box 4 to that of box 2?
The answer is exactly one of: after, before, contains, during, equals, finished-by, finishes, meets, met-by, overlapped-by, overlaps, started-by, starts.
```

**Answer:**
```
overlaps
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Objects occupy distinct points on the integer grid [0, 4] x [0, 4].
North is +y and East is +x. Any object not mentioned in a step stays fixed.

Initial facts:
- C is in the same column as A.
- C is left of B.
- B is below A.
- C is above B.
- A is above C.
- A is left of B.

Steps:
1. B jumps to A's position offset by (2, 0).

What is the final Manhattan distance between A and B? Answer as an integer.

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
- b1: green
- b2: blue
- b3: black
- b4: yellow
Initial state:
- b1 is in x1
- b2 is in x1
- b3 is in x1
- b4 is in x2
Moves:
- Transfer everything in x1 into x2.
- Move all contents of x2 to x1.
- Transfer b3 from x1 into x2.
- Move it from x2 to x3.
Where is b4 now? The answer is a box tag, like x1.
```

**Answer:**
```
x1
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A stern tall writer named Lena avoided a loud stern nurse named Sam.
(2) A quiet tall banker named Nora thanked him.
(3) She questioned a short stern farmer named Mary.
(4) Sam met Mary.
(5) The farmer thanked him.
(6) An old stern teacher named Alan questioned her.
(7) The nurse met the banker.

In sentence 6, what does the object expression 'her' refer to?
The answer is the name of the person it refers to.
```

**Answer:**
```
Mary
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
Variables/domains:
- 0 <= x0 <= 2
- 0 <= x1 <= 1

Constraints:
1. -x0 - 2*x1 == 0
2. -2*x0 <= 1
3. x0 != -3

Enumerate ALL satisfying assignments in variable order [x0, x1].
The answer is a Python list of lists of ints, sorted lexicographically, or UNSAT if no assignment exists.

```

**Answer:**
```
[[0, 0]]
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

Nodes [0, 1, 2, 3, 4, 5] and directed edges: (0, 4), (1, 5), (3, 2), (4, 2), (5, 4).

Find the lexicographically smallest shortest directed path from Node 1 to Node 4.
If no path exists, answer `None`.
The answer is a Python list of nodes or `None`.
```

**Answer:**
```
[1, 5, 4]
```

---

## [graph_isomorphism](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider two directed graphs described below.

Graph A:
Directed Edges: 0->1, 1->5, 3->4, 4->2, 4->3, 5->1, 5->3

Graph B:
digraph { 0->4; 1->5; 3->1; 4->2; 4->3; 5->1; 5->3 }

Do Graph A and Graph B have the exact same structure, just with different node labels? (In other words, are they isomorphic?)
The answer is `True` or `False`.
```

**Answer:**
```
False
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

Adjacency Dictionary (source to targets): {0: [2], 1: [0], 2: [3], 3: [5], 4: [1], 5: [4]}

Queries: [(5, 2)]
Each pair (x, k) asks for the k-th successor of x (following exact directed edges k times).
The answer is a Python list of integers in query order.
```

**Answer:**
```
[1]
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

0: 0->1; 1:; 2:; 3: 3->1; 4: 4->2 4->3; 5: 5->1

In this scenario, a directed edge from U to V means V depends on U (so U is a prerequisite of V).
List all prerequisites of node 1 (recursively), making sure to order base prerequisites first.
Do not include the query node itself.
If A is a prerequisite of B and both appear in your answer, A must appear before B.
Tie-break nodes with no mutual dependency lexicographically (smaller node ID first).
The answer is a Python list of integers.
```

**Answer:**
```
[0, 4, 3, 5]
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 1-character string that fully matches the regular expression: ([VEX])
```

**Answer:**
```
V
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'a', 'aa'
Negative: 'abcc', 'ac', 'adaac', 'adacb', 'ca', 'ccbba', 'dac', 'dbd'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
a+
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: Individual surface country item majority federal. Reveal at girl meet.
Regex: \b[A-Z][a-z]+\b
Return only a JSON array of exact non-overlapping matches, left-to-right. Include duplicates. Return [] if none.
```

**Answer:**
```
["Individual","Reveal"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Consider the regular expressions A = a|b* and B = a|b*
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
Yes
```

---

## [lexical_knowledge](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/knowledge.py)

**Prompt:**
```
Context: WordNet (relation holds for any valid noun sense).
Select all cohyponyms(kitchen)
From: [flooring, drug, ballroom, bedroom, bower, bathroom, shipyard, handbag, classroom, foyer, privy]
The answer is a JSON list.
```

**Answer:**
```
["ballroom", "bathroom", "bedroom", "classroom", "foyer", "privy"]
```

---

## [decision_path_parsing](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

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
< [ ] > ( ) <M> ( </M> )

(QUESTION)
Output the rule IDs on the path from the root to the marked token.
Include only rules whose left-hand side has more than one possible production.
Answer NONE if there are no such rules.
One line only.
```

**Answer:**
```
R2 R2 R2 R3
```

---

## [continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
List all valid next tokens for this prefix. The answer is the list of valid tokens sorted alphabetically and separated by |, with STOP at the end if the prefix forms a complete string.
(GRAMMAR)
S -> B
B -> 'develop'
B -> 'pattern' B
(PREFIX)
pattern pattern
```

**Answer:**
```
develop|pattern
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> D 'parent'
D -> 'get'

(STRING)
get parent get parent

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
parent >>get<<
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> C
B -> 'special'
B -> B B
C -> B

(PREFIX)
special special

(TEMPLATE)
special ___ ___ special ___

(SUFFIX)
special

Fill in the 3 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 5 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
special special special special special
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
qty,date
510,2025-12-19
78,2026-01-21
407,2025-07-03
433,2026-05-05
342,2026-04-22


SQL: SELECT COUNT(*) FROM dataframe WHERE date = '2025-12-19'

The answer is the result as single value.
```

**Answer:**
```
1
```

---

## [table_conversion](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Convert the following table from markdown to html.

| city            | rating   |
|:----------------|:---------|
| South Saramouth | 3.2      |
| Stewartview     | 1.0      |
| West Debra      | 4.6      |
| Christopherview | 3.5      |
| Taylorfurt      | 2.6      |

The answer is the converted table.
```

**Answer:**
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>city</th>
      <th>rating</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>South Saramouth</td>
      <td>3.2</td>
    </tr>
    <tr>
      <td>Stewartview</td>
      <td>1.0</td>
    </tr>
    <tr>
      <td>West Debra</td>
      <td>4.6</td>
    </tr>
    <tr>
      <td>Christopherview</td>
      <td>3.5</td>
    </tr>
    <tr>
      <td>Taylorfurt</td>
      <td>2.6</td>
    </tr>
  </tbody>
</table>
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` denotes λx.body; application is left-associative juxtaposition; free identifiers are treated as constants.

Term: (a ((\_0.(\v0._0)) c))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(a (\v0.c))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- if(false,X,Y) -> Y
- or(true,X) -> true
- or(X,false) -> X
- and(X,false) -> false
- not(not(X)) -> X
- or(X,X) -> X

Term: or(or(not(or(c,c)),false),not(c))

The answer is the normal form.
```

**Answer:**
```
not(c)
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict the printed output of the following Python code:

```python
j = 0
r = 8
z = 13
y = j
print("go"[0])
```

The answer is the exact printed output string.
````

**Answer:**
```
g
```

---

## [diff_prediction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_diff.py)

**Prompt:**
```
Below is the version history of a file.

Version f3c5571:
1    | Door fall certain same
2    | Message fight western several none model
3    | Believe suggest water record outside particularly boy design
4    | Fish level join feeling
5    | Authority serious what travel so nearly

Version cf31210:
1    | Door fall certain same
2    | Message fight western several none model
3    | her decide better wonder operation
4    | Believe suggest water record outside particularly boy design
5    | Fish level join feeling
6    | Authority serious what travel so nearly

Generate the Unified Diff to transform version f3c5571 into version cf31210.
The answer is the diff chunks only (no file headers), or empty if no changes.
```

**Answer:**
```
@@ -1,5 +1,6 @@
 Door fall certain same
 Message fight western several none model
+her decide better wonder operation
 Believe suggest water record outside particularly boy design
 Fish level join feeling
 Authority serious what travel so nearly
```

---

