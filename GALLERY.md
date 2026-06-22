# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`conjecture_entailment`](#conjecture_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`evidence_retrieval`](#evidence_retrieval) · [`logic_nli`](#logic_nli) · [`logic_qa`](#logic_qa) · [`multistep_abduction`](#multistep_abduction) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`planning`](#planning) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_dependencies`](#graph_dependencies) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_reasoning`](#regex_reasoning) · [`regex_retrieval`](#regex_retrieval) · [`constrained_continuation`](#constrained_continuation) · [`locate_error`](#locate_error) · [`parsing_derivation`](#parsing_derivation) · [`table_qa`](#table_qa) · [`string_transduction`](#string_transduction) · [`code_execution`](#code_execution) · [`code_runnability`](#code_runnability) · [`analogical_case_retrieval`](#analogical_case_retrieval)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate 0 * 0.
The answer is a number.
```

**Answer:**
```
0
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
A jar holds 8 buttons. In order: 4 buttons removed; then cut to half. How many buttons are in the jar now? Give the answer as a number.
```

**Answer:**
```
2
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 + 2 = 0
  X2 + 16 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
-16
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex (a b : Int) : (b^2 + 2 * b) = (2 * b + b^2) := by
  ?

CANDIDATE:
decide
```

**Answer:**
```
False
```

---

## [lean_missing_proof_line_selection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Fill `__ANSWER__` with one listed Lean proof line. Mathlib is imported.
The answer is the line number.

THEOREM:
theorem ex (s t u : Set Int) (h0 : u ⊆ s) : t ∩ u ⊆ t ∩ s := by
  intro x hx
  __ANSWER__

LINES:
1. simp
2. rfl
3. intro x hx
4. exact h0
5. intro h
6. exact ⟨hx.1, h0 hx.2⟩
```

**Answer:**
```
6
```

---

## [conjecture_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the premises entail the conjecture.

Domain: Group Theory

Premises:
- (product(multiply(X1,X2),X3,multiply(X4,X3))|~product(X1,X2,X4))
- (multiply(multiply(X1,X2),X3)=multiply(X1,multiply(X2,X3)))
- (product(X1,X2,X3)|~product(multiply(X4,X5),X2,X3)|~product(X4,X5,X1))

Conjecture: `(product(multiply(X1,X2),X3,X4)|~product(multiply(X5,multiply(X6,X2)),X3,X4)|~product(X5,X6,X1))`

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
Unsatisfiable theory.
Remove a smallest set of clauses to make it satisfiable.
The answer is sorted clause numbers.

Clauses:
1. (p(b))
2. (r(b))
3. (~p(b) | s(b))
4. (~r(b) | s(b))
5. (~s(b))
```

**Answer:**
```
[5]
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: C=(-4/21, 5/7); E=(-1, 4); F=(-4, 5); L=(-5, -2); M=(4, -4); S=(6, 10); Z=(2, 4).
Definitions: S is the translation of E by vector LZ. C is the intersection of lines ZS and FM.
Question: What type of angle is angle CSF?
Answer is one of: acute, right, obtuse.
```

**Answer:**
```
acute
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: (\v0.(((\_0.v0) c) v0))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(\v0.(v0 v0))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- if(false,X,Y) -> Y
- id(X) -> X
- let(unit,X) -> X
- if(true,X,Y) -> X
- fst(pair(X,Y)) -> X

Term: if(true,fst(if(true,let(unit,unit),c)),true)

The answer is the normal form.
```

**Answer:**
```
fst(unit)
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor d is independently true with probability 0.4.
Factor a is independently true with probability 0.6.
The observation holds exactly when (factor d or factor a).
We observe it.
Which hidden fact values form the most probable complete explanation?

The answer is a sorted Python list of strings.
```

**Answer:**
```
["a", "not d"]
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A box contains 5 gold balls and 7 silver balls.
Two balls are drawn without replacing the first ball.
Which statement is more likely?
A: both selected balls are gold.
B: the selected balls have different colors.

The answer is exactly one of: A, B, equal.
```

**Answer:**
```
B
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] Brian is the only person in the room.
[1] Steven is papa tagged
[2] all old people in the room are old
[3] if someone is echo tagged then he is november tagged, echo tagged and victor tagged and vice versa
[4] someone in the room is quiet
[5] everyone in the room who is echo tagged is not foxtrot tagged
Hypothesis:
Steven and Brian are not quiet

Which statements in the premise contradict the hypothesis?
The answer is the list of supporting statement indices, e.g. [0, 6, 7].
```

**Answer:**
```
[0, 4]
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
Karen is the only person in the room.
all old people in the room are old
everyone in the room is an old person if she is mike tagged
Jessica is juliet tagged
Karen is old
everyone in the room is an old person if she is a quiet person

Hypothesis:
Carolyn is an old person

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
```

**Answer:**
```
neutral
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
alice trusts david.
david is careful.
clara advises david.
clara advises bruno.
alice helps david.
clara is not trusted.
Anyone who trusts someone careful is active.
From x is active, it follows that x is trained.
For all x, if x is careful and x is approved, then x is verified.
Every trusted entity is not verified.
From x trusts y, it follows that y helps x.
For all x, y, z, if x advises y and y helps z, then x does not trusts z.
Whenever x trusts y and x is trained, y is approved.

Question:
How many entities are approved?

Answer with one integer.
```

**Answer:**
```
1
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] bruno is approved.
[1] clara is active.
[2] Whenever x is approved, x is trusted.
[3] All things that are trusted are verified.

Hypothesis:
clara is verified.

Candidate Facts:
[0] clara is trained.
[1] alice is approved.
[2] alice is careful.
[3] clara is approved.
[4] clara is not approved.
[5] david is approved.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
The answer is the smallest list of candidate indices, e.g. [0, 2].
```

**Answer:**
```
[3]
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] box is inside map.
[1] map is inside key.
[2] lamp is safe.
[3] key is right of map.
[4] lamp is not marked.
[5] lamp is fixed.
[6] If one person is left of to another, then the second is right of to the first.
[7] From x is above y, it follows that y is below x.
[8] Whenever x is inside y, y contains x.
[9] Anyone inside to someone who is inside to a third person is inside to that third person.
[10] For all x, y, z, if x is left of y and y is left of z, then x is left of z.
[11] Above relations followed by above relations imply above relations.
[12] Whenever x is disjoint from y, y is disjoint from x.

Hypothesis:
key does not contain box.

Which premise statements are necessary to contradict the hypothesis, meaning removing any one of them breaks that result?
The answer is a list of indices, e.g. [0, 1].
```

**Answer:**
```
[0, 1, 8, 9]
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
alice is approved.
alice is verified.
bruno is trained.
david is trained.
bruno is approved.
clara is careful.
Whenever x is approved and x is verified, x is careful.
Whenever x is careful, x is trusted.
Every careful entity that is also trained is approved.
Anyone whom a careful person helps is trusted.
Whenever x advises y and y is active, x is careful.
Anyone who is trained and approved is not active.
From x advises y and y is trusted, it follows that x is careful.

Hypothesis:
alice is trusted.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
```

**Answer:**
```
entailment
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
Objects:
object_1, object_2, object_3, object_4

Actions:
action_0(x0, x1)
  Requires: (not fluent_0)
  Effect: fluent_0
action_1(x0)
  Requires: fluent_0
  Effect: fluent_1(x0), not fluent_0

Initial state:
True values: None

Goal:
fluent_1(object_1), fluent_0
Hint: Reference solution has 3 actions (but it may not be optimal).

Action format example: action_0(object1 object2).
The answer is the plan, one action per line.
```

**Answer:**
```
action_0(object_4, object_4)
action_1(object_1)
action_0(object_4, object_4)
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: [6, 1, 8, 4, 20, 8, 15, 4, 4, 3]
How many times does 8 appear? The answer is a number.
```

**Answer:**
```
2
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {141, 399, 696, 820, 487, 408, 166, 753}
Set2: {820, 166, 696, 408, 399, 141, 753}
Do Set1 and Set2 contain exactly the same elements? The answer is True or False.
```

**Answer:**
```
False
```

---

## [set_intersection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {596, 619, 157, 228, 1, 798, 651, 737}
Set2: {666, 651, 157, 393, 227, 596}
The answer is Set1 ∩ Set2 as a Python set.
```

**Answer:**
```
{157, 596, 651}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {28, 24, 29, 27, 31, 26, 33}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{25, 30, 32}
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *, **.
Use n.
Sequence: [0, 4, 16, 36, 64, 100, 144, 196]
Initial terms: []
The answer is the RHS only.
```

**Answer:**
```
4*n**2
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E1 is the 5th-newest.
- E2 is the 2nd-newest.
- E3 is newer than E0.
- E2 is newer than E3.

Which object is the 3rd-newest?
The answer is one object label.
```

**Answer:**
```
E3
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x. Unmentioned objects stay fixed.

Initial Facts:
- B is in the same row as C.
- C is right of A.
- A is right of B.
- C is right of B.
- C is below A.
- A is above B.
- A starts at (3, 4).

Steps:
1. B jumps to C's position offset by (-1, 1).

What is the final coordinate of A? The answer is (x, y).
```

**Answer:**
```
(3, 4)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: black
- b2: yellow
- b3: yellow
- b4: white
Initial state:
- b1 is in x1
- b2 is in x1
- b3 is in x1
- b4 is in x3
Moves:
- Move b4 from x3 to x1.
- Move b1 from x1 to x3.
- Move b3 from x1 to x3.
- Relocate b4 from x1 to x3.
Where is b2 now? The answer is a box tag, like x1.
```

**Answer:**
```
x1
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A quiet young engineer named Max called a loud old pilot named Zoe.
(2) He avoided an old quiet pilot named Noah.
(3) A loud old writer named Mary helped Noah.
(4) A kind young engineer named Iris greeted the loud pilot.
(5) Max avoided the kind engineer.
(6) She thanked him.

In sentence 6, what does the subject expression 'She' refer to?
The answer is the person's name.
```

**Answer:**
```
Iris
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
4x4 grid. Each row and column contains 1..4 once.
Clues:
- r3c2 = 2
- r4c2 = 1
- r1c1 = 4
- r1c3 = 2

What is r1c2?
Answer with one number.
```

**Answer:**
```
3
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

digraph { 0->2; 0->3; 0->4; 1->2; 1->3; 1->5; 4->3; 5->2; 5->4 }

In this scenario, a directed edge from U to V means V depends on U (so U is a prerequisite of V).
List all prerequisites of node 2 (recursively), making sure to order base prerequisites first.
Exclude the query node; prerequisites must precede dependents, with lexicographic tie-breaks.
The answer is a Python list of integers.
```

**Answer:**
```
[0, 1, 5]
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

Node 0 points to 5. Node 1 points to 0, 2. Node 2 points to 3. Node 3 points to 4. Node 4 points to 3. Node 5 points to 4.

Find the lexicographically smallest shortest directed path from Node 1 to Node 3.
The answer is a Python list of nodes, or `None` if no path exists.
```

**Answer:**
```
[1, 2, 3]
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

Directed Edges: 0->2, 1->4, 2->1, 3->0, 4->5, 5->3

Queries: [(5, 1)]
Each pair (x, k) asks for the k-th successor of x (following exact directed edges k times).
The answer is a Python list of integers in query order.
```

**Answer:**
```
[3]
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 5-character string that fully matches the regular expression: [ETX]+
```

**Answer:**
```
TXETX
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'aaad', 'dbb'
Negative: 'aa', 'ab', 'c', 'cbaa', 'cdac', 'cdbb', 'dad', 'ddcd'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
a*db*
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = (c|bb)
B = c|a?
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
No
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: i. R. ]W. ]U. [. o
Regex: \][M-Y]
The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. The answer is [] if none.
```

**Answer:**
```
["]W","]U"]
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> A
A -> 'sound'
A -> A 'sound'

(PREFIX)
sound

(TEMPLATE)
sound ___ ___

(SUFFIX)
<empty>

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
sound sound sound
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> B
B -> 'hold' B
B -> 'seven'

(STRING)
hold hold hold hold hold seven seven

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
seven >>seven<<
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: S -> B
R1: B -> B 'court'
R2: B -> 'skill'
R3: B -> C

(STRING)
skill court court court court

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R1 R1 R1 R1 R2
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
\begin{tabular}{rr}
\toprule
qty & price \\
\midrule
879.0 & 495.56 \\
932.0 & 303.56 \\
15.0 & 35.43 \\
502.0 & 475.31 \\
799.0 & 464.51 \\
\bottomrule
\end{tabular}


SQL: SELECT ROUND(MIN(price), 2) FROM dataframe

The answer is the result as single value.
```

**Answer:**
```
35.43
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: ccbcdbbc
Operations:
- replace c with b
- sort ascending
Answer with the final string.
```

**Answer:**
```
bbbbbbbd
```

---

## [code_execution](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict the value returned by this Python call.
```python
def f0(y: int) -> int:
    print(y)
    return y - 5
def f1(e: int) -> str:
    e = [i % 3 for i in range(2, 8)]
    return "go"
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(0)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
-5
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(b: list, q: str) -> int:
    assert 4 == 5
    a = f0([0, 1, 2], "go") * f0(b, q)
    return a + 1
def f1(a: list, f: list) -> list:
    print(f)
    return f
def endpoint(x0: list, x1: str) -> int:
    return f0(x0, x1)

```
Call: `endpoint([-3, 1], 'czb')`
The answer is `OK` if it runs successfully; otherwise the exception class name.
````

**Answer:**
```
AssertionError
```

---

## [analogical_case_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed.

M0
b is beta-linked to e.
c is beta-linked to b.
c is beta-linked to e.
e is gamma-linked to b.
Implies: c is beta-linked to a.

M1
d is alpha-linked to a.
d is alpha-linked to c.
d is beta-linked to c.
c is gamma-linked to b.
Implies: a is alpha-linked to c.

M2
b is beta-linked to e.
d is beta-linked to b.
b is gamma-linked to c.
d is gamma-linked to c.
Implies: b is beta-linked to c.

M3
a is alpha-linked to e.
e is alpha-linked to b.
c is beta-linked to d.
e is gamma-linked to b.
Implies: e is alpha-linked to d.

M4
a is beta-linked to e.
b is beta-linked to c.
d is beta-linked to b.
b is gamma-linked to a.
Implies: d is gamma-linked to a.

M5
c is alpha-linked to a.
e is alpha-linked to d.
d is beta-linked to e.
c is gamma-linked to d.
Implies: a is beta-linked to d.

Query
v is delta-linked to y.
y is delta-linked to x.
y is delta-linked to z.
u is epsilon-linked to z.
v is epsilon-linked to z.
u is gamma-linked to z.
y is gamma-linked to u.
z is gamma-linked to y.
Implies:
```

**Answer:**
```
x is delta-linked to z.
```

---
