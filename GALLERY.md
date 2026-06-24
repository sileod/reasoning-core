# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`conjecture_entailment`](#conjecture_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_expression`](#set_expression) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`analogical_case_retrieval`](#analogical_case_retrieval)

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

TPTP source: GRP003-1.ax

Background axioms:
- (product(inverse(X1),X1,identity))
- (subgroup_member(inverse(X1))|~subgroup_member(X1))

Premises:
- (X3=X4|~product(X1,X2,X3)|~product(X1,X2,X4))
- (product(X1,X2,multiply(X1,X2)))
- (product(identity,X1,X1))

Conjecture: `(subgroup_member(X1)|~product(identity,identity,X1)|~subgroup_member(X2))`

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
- (between(X2,inner_pasch(X1,X2,X3,X5,X4),X4)|~between(X1,X2,X3)|~between(X4,X5,X3))
Negated theorem: `(between(extension(lower_dimension_point_3,lower_dimension_point_2,X1,X2),lower_dimension_point_1,lower_dimension_point_2))`
Clauses:
1. (~between(lower_dimension_point_1,lower_dimension_point_2,lower_dimension_point_3))
2. (between(X1,X2,extension(X1,X2,X3,X4)))
3. (equidistant(X1,extension(X2,X1,X3,X4),X3,X4))
4. (~between(lower_dimension_point_2,lower_dimension_point_3,lower_dimension_point_1))
5. (~between(lower_dimension_point_3,lower_dimension_point_1,lower_dimension_point_2))
6. (between(X5,inner_pasch(X1,X2,X3,X5,X4),X1)|~between(X1,X2,X3)|~between(X4,X5,X3))
7. (X1=X2|~equidistant(X1,X2,X3,X3))
8. (X1=X2|~between(X1,X2,X1))
```

**Answer:**
```
2 3 7 8
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

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: ((a (a ((\_0.c) a))) (d c))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
((a (a c)) (d c))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- id(X) -> X
- if(false,X,Y) -> Y
- const(X,Y) -> X
- fst(pair(X,Y)) -> X
- let(unit,X) -> X

Term:
let(unit,const(fst(let(b,if(false,a,true))),b))

The answer is the normal form.
```

**Answer:**
```
fst(let(b,true))
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
Mark is the only person in the room.
all old people in the room are old
no old person outside the room is old
Benjamin is old and is papa tagged
everyone in the room is old if he is quiet
Richard is a quiet person

Hypothesis:
Benjamin is old

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
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
[0] there is a room.
[1] someone in the room is november tagged
[2] no old person in the room is old
[3] Laurie is papa tagged
[4] Ashley and Laurie are old people
[5] Laurie is tango tagged
Hypothesis:
it is true that “Laurie is an old person”

Which statements in the premise entail the hypothesis?
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
alice is trained.
clara is verified.
david is not active.
bruno is active.
alice helps david.
Whenever x is trained, x is active.
From x is active, it follows that x is trusted.
Being trusted implies being verified.
Being verified implies being approved.
Whenever x is verified and x is careful, x is active.
Whenever x is verified and x is careful, x is not approved.
Helps relations followed by trusts relations imply advises relations.
All things that are approved are not careful.
From x trusts y and y is verified, it follows that x is trusted.

Hypothesis:
bruno is verified.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
```

**Answer:**
```
entailment
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] key is left of box.
[1] box is left of map.
[2] box is marked.
[3] lamp is not safe.
[4] key is safe.
[5] lamp is right of key.
[6] Whenever x is left of y, y is right of x.
[7] Every above relation creates a below relation in the reverse direction.
[8] Whenever x is inside y, y contains x.
[9] For all x, y, z, if x is inside y and y is inside z, then x is inside z.
[10] For all x, y, z, if x is left of y and y is left of z, then x is left of z.
[11] Whenever x is above y and y is above z, x is above z.
[12] If one person is disjoint to another, then the second is disjoint to the first.

Hypothesis:
map is right of key.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 6 10
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] bruno is verified.
[1] david is trusted.
[2] From x is verified, it follows that x is active.
[3] Whenever x is active, x is trained.

Hypothesis:
david is trained.

Candidate Facts:
[0] david is not active.
[1] alice is verified.
[2] david is not verified.
[3] david is verified.
[4] bruno helps clara.
[5] david advises alice.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
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
david is careful.
david is trained.
alice is trusted.
bruno is trained.
bruno is verified.
clara is trusted.
Anyone who is careful and trained is trusted.
Every trusted entity is active.
Anyone who is trained and verified is careful.
From x helps y and y is active, it follows that x is careful.
For all x, if x is trained and x is approved, then x is verified.
From x trusts y and x is approved, it follows that y is trusted.
Whenever x advises y and x is approved, y is trained.

Question:
How many entities are trusted?

Answer with one integer.
```

**Answer:**
```
4
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
Set_A: {159, 162, 158, 164, 160, 161, 157, 155}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{156, 163}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: ['o', 'o', 'k', 'l', 'h', 'l', 'l', 't', 'r', 'e']
How many times does 'l' appear? The answer is a number.
```

**Answer:**
```
3
```

---

## [set_expression](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
B: {25, 7, 5, 15, 4, 22, 8, 3}
C: {1, 8, 3, 4, 5, 26, 15, 21}
Evaluate (C&B).
```

**Answer:**
```
{15, 3, 4, 5, 8}
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
The answer is a 2-character string that fully matches the regular expression: [c6I]{1,3}
```

**Answer:**
```
cc
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'd', 'dd'
Negative: 'a', 'adc', 'bdddc', 'cb', 'cbcbc', 'cc', 'daa', 'dbdc'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
d+
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: ?? z ; v ?? G(
Regex: (\?){2}
The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. The answer is [] if none.
```

**Answer:**
```
["??","??"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = bba?
B = (ab|ab)
Is every string accepted by A also accepted by B?
The answer is Yes or No.
```

**Answer:**
```
No
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
[ ( ) < > ] [ < > ] [ ]

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R4 R2 R3 R1 R2 R5 R1 R1 R2 R4 R2 R5 R1 R1 R2 R4 R1 R1
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
< < > > (

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
INCOMPLETE
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> D D
D -> 'nature'

(PREFIX)
nature nature nature nature nature

(TEMPLATE)
___ nature ___

(SUFFIX)
nature nature nature

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
nature nature nature
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

## [analogical_case_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed, and each link name may also have its direction consistently reversed.

M0
e is alpha-linked to c.
e is beta-linked to c.
d is gamma-linked to b.
e is gamma-linked to c.
Implies: d is alpha-linked to e.

M1
b is alpha-linked to e.
b is beta-linked to a.
b is beta-linked to d.
b is gamma-linked to c.
Implies: d is gamma-linked to b.

M2
d is alpha-linked to a.
a is beta-linked to e.
a is gamma-linked to c.
c is gamma-linked to e.
Implies: a is alpha-linked to c.

M3
a is alpha-linked to b.
d is alpha-linked to a.
d is alpha-linked to b.
d is beta-linked to c.
Implies: b is beta-linked to d.

Query
u is delta-linked to x.
v is delta-linked to y.
x is delta-linked to z.
y is delta-linked to u.
y is delta-linked to x.
z is delta-linked to u.
y is epsilon-linked to v.
y is gamma-linked to u.
Implies:
```

**Answer:**
```
x is epsilon-linked to y.
```

---
