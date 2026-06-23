# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_missing_proof_line_selection`](#lean_missing_proof_line_selection) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`conjecture_entailment`](#conjecture_entailment) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`parsing_derivation`](#parsing_derivation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`analogical_case_retrieval`](#analogical_case_retrieval)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate -5 + 9.
The answer is a number.
```

**Answer:**
```
4
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Jon has half as many apples as Wei. Wei has 2 fewer apples than Ravi. Ravi has 8 apples. How many apples does Wei have? Answer with s a number.
```

**Answer:**
```
6
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X2 + 13 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
-13
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
1. intro x hx
2. exact ⟨h0 h.1, h.2⟩
3. exact h0
4. simp
5. rfl
6. intro h
```

**Answer:**
```
2
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem?
The answer is True or False.

THEOREM:
theorem ex (p3 p4 p6 : Prop) : (p4 → p3) ∧ (p3 → p6) → (p4 → p6) := by
  ?

CANDIDATE:
decide
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

TPTP source: FLD002-0.ax

Background axioms:
- (sum(additive_identity,X1,X1)|~defined(X1))
- (defined(additive_identity))

Premises:
- (sum(X1,X2,X3)|~sum(X1,X4,X5)|~sum(X4,X6,X2)|~sum(X5,X6,X3))

Conjecture: `(sum(X1,additive_identity,X2)|~sum(X3,additive_identity,X1)|~sum(X3,additive_identity,X2))`

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
- (X5=X4|~product(X1,X2,X3,X4)|~product(X1,X2,X3,X5))
- (product(X1,X2,identity_for(X1),X2))
Negated theorem: `(inverse(X1,multiply(X1,identity_for(X1),identity_for(X1))) != identity_for(X1))`
Clauses:
1. (product(X2,X1,X3,multiply(X2,X1,X3))|~group_member(X1,X2)|~group_member(X3,X2))
2. (group_member(identity_for(X1),X1))
3. (product(X1,X2,inverse(X1,X2),identity_for(X1)))
4. (product(X1,inverse(X1,X2),X2,identity_for(X1)))
5. (product(X1,identity_for(X1),X2,X2))
```

**Answer:**
```
1 2
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: D=(1, 0); H=(5, 3); I=(-5, 0); O=(-12, 0); Q=(5, 0); X=(-2, 3); Y=(-1, -4).
Definitions: O is the translation of I by vector HX. Q is the projection of H onto line IO.
Question: Where is point Q relative to directed line OY?
Answer is one of: left, right, on.
```

**Answer:**
```
left
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: (d ((a ((\_0.c) d)) b))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(d ((a c) b))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- sub(X,X) -> 0
- neg(neg(X)) -> X
- mul(1,X) -> X
- add(mul(X,Y),mul(X,Z)) -> mul(X,add(Y,Z))
- pow(X,1) -> X
- add(X,0) -> X
- sub(X,0) -> X
- add(0,X) -> X

Term: sub(add(sub(neg(neg(b)),2),pow(neg(1),1)),mul(a,pow(0,1)))

The answer is the normal form.
```

**Answer:**
```
sub(add(sub(b,2),neg(1)),mul(a,0))
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor c is independently true with probability 0.2.
Factor d is independently true with probability 0.7.
The observation holds exactly when (factor c or factor d).
We observe it.
Which hidden fact values form the most probable complete explanation?

Hidden fact values:
0. c
1. not c
2. d
3. not d

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
A deck contains 8 red cards and 7 blue cards.
Two cards are drawn without replacing the first card.
Which statement is more likely?
A: at least one selected card is red.
B: both selected cards are blue.

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
Bobby is the only person in the room.
“everyone anywhere is zulu tagged” unless “Bobby is not old”
Daniel is india tagged
Joseph who is zulu tagged is an old person
Bobby is november tagged
Bobby is november tagged

Hypothesis:
Joseph is not quiet and not old

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
```

**Answer:**
```
contradiction
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] Angela is the only person in the room.
[1] everyone in the room who is tango tagged is romeo tagged
[2] Laura who is whiskey tagged is tango tagged
[3] Susan is not tango tagged
[4] Laura is not an old person
[5] everyone in the room who is victor tagged is alpha tagged
Hypothesis:
Laura is a quiet old person

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
map is above lamp.
lamp is above key.
lamp is visible.
lamp is not blocked.
key is visible.
map is blocked.
For all x, y, if x is left of y, then y is right of x.
Whenever x is above y, y is below x.
From x is inside y, it follows that y contains x.
If one person is inside to a second person, and the second is inside to a third, then the first is inside to the third.
Anyone left of to someone who is left of to a third person is left of to that third person.
If one person is above to a second person, and the second is above to a third, then the first is above to the third.
Every disjoint relation creates a disjoint relation in the reverse direction.

Hypothesis:
key is not below map.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
```

**Answer:**
```
contradiction
```

---

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] bruno advises david.
[1] david is approved.
[2] bruno is not approved.
[3] alice is trusted.
[4] clara is approved.
[5] clara trusts bruno.
[6] bruno is trusted.
[7] Whenever x advises y and y is approved, x is verified.
[8] Whenever x is verified, x is careful.
[9] Whenever x advises y and y trusts z, x helps z.
[10] Every active entity is trained.
[11] For all x, if x is verified and x is active, then x is careful.
[12] If a person is helps to someone trusted, then that person is careful.

Hypothesis:
bruno is careful.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
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
[0] alice is active.
[1] For all x, if x is active, then x is verified.
[2] All things that are verified are trained.

Hypothesis:
david is trained.

Candidate Facts:
[0] clara trusts alice.
[1] alice is not approved.
[2] bruno is active.
[3] david is active.
[4] david is not active.
[5] clara is active.

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
david is trusted.
clara is trusted.
alice is trained.
bruno helps david.
clara advises bruno.
Anyone who is careful and trusted is approved.
Every approved entity is trained.
Every careful entity that is also active is approved.
Every approved entity is trusted.
If a careful person is advises to someone, then that other person is verified.
Anyone helps to someone who is advises to a third person is trusts to that third person.
For all x, if x is trained, then x is not verified.

Question:
How many entities are trained?

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
  Requires: (not fluent_2(x0)), (not fluent_1)
  Effect: fluent_2(x0), fluent_1
action_1(x0, x1)
  Effect: not fluent_2(x0)

Initial state:
Default value: False
True values: None

Goal:
fluent_1

Action format example: action_0(object1 object2).
The answer is the plan, one action per line.
```

**Answer:**
```
action_0(object_1)
```

---

## [set_intersection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {351, 947, 14, 275, 132, 415, 378, 898}
Set2: {296, 898, 892, 378, 14, 406}
The answer is Set1 ∩ Set2 as a Python set.
```

**Answer:**
```
{14, 378, 898}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {849, 851, 845, 846, 852, 848, 854}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{847, 850, 853}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: [19, 18, 9, 19, 17, 8, 11, 19, 20, 3]
How many times does 8 appear? The answer is a number.
```

**Answer:**
```
1
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {362, 742, 131, 68, 71, 365, 994, 333}
Set2: {68, 742, 333, 365, 994, 953, 131, 362}
Do Set1 and Set2 contain exactly the same elements? The answer is True or False.
```

**Answer:**
```
False
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *, **.
Use n.
Sequence: [9, 8, 7, 6, 5, 4, 3, 2]
Initial terms: []
The answer is the RHS only.
```

**Answer:**
```
9 - n
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E0 is newer than E3.
- E2 is newer than E1.
- E2 is immediately newer than E4.
- E3 is newer than E2.

Which object is the 4th-newest?
The answer is one object label.
```

**Answer:**
```
E4
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- C is right of A.
- B is left of C.
- A is above B.
- A is left of B.
- B is above C.
- C is below A.

Steps:
1. A and B swap positions.

What is the final spatial relation of A to B? The answer is (horizontal, vertical), where horizontal is left/right/aligned and vertical is above/below/aligned.
```

**Answer:**
```
(right, below)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: green
- b2: blue
- b3: red
- b4: red

Initial State:
- b1 is in x2
- b2 is in x2
- b3 is in x2
- b4 is in x2

Moves:
- Transfer b4 from x2 into x3.
- Transfer b3 from x2 into x1.
- Move it from x1 to x2.
- Relocate b3 from x2 to x1.
Where is b4 now? The answer is a box tag, like x1.
```

**Answer:**
```
x3
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A loud short lawyer named Rita called a short stern writer named Adam.
(2) He watched an old tall teacher named Mia.
(3) He met her.
(4) He greeted Rita.
(5) She questioned a quiet stern writer named Rose.
(6) Rose helped the short writer.
(7) The teacher greeted Rose.

In sentence 3, what does the object expression 'her' refer to?
The answer is the person's name.
```

**Answer:**
```
Mia
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
4x4 grid. Each row and column contains 1..4 once.
Clues:
- r2c3 = 2
- r1c4 = 1
- r3c4 = 2
- r2c2 = 4

What is r2c4?
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
Find the lexicographically smallest shortest directed path from node 3 to node 4.
Answer with space-separated nodes, or `None` if no path exists.

Graph:
Adjacency Dictionary (source to targets): {0: [1, 4], 1: [0], 2: [3], 3: [4], 4: [3], 5: [0]}
```

**Answer:**
```
3 4
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
0: 0->1; 1: 1->4; 2: 2->0; 3: 3->3; 4: 4->2; 5: 5->5

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
List all ancestors of node 5.
Order them so predecessors come before successors, with lexicographic tie-breaks.
Answer with space-separated indexes.

Graph:
0: 0->2; 1: 1->2 1->5; 2:; 3: 3->0; 4: 4->3 4->5; 5:
```

**Answer:**
```
1 4
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 1-character string that fully matches the regular expression: K|[S9K]
```

**Answer:**
```
S
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'b', 'd'
Negative: 'aaac', 'bdc', 'c', 'cadbd', 'cbac', 'ccac', 'da', 'dccca'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
b|d
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: 14. 4439. 47. 0Bg. 626. v]]]
Regex: \d{2,4}
The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. The answer is [] if none.
```

**Answer:**
```
["14","4439","47","626"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = c|ba?
B = a|bb
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
( ( ) ( ) ) [ ]

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R3 R2 R3 R1 R2 R3 R1 R1 R2 R4 R1 R1
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> 'certain'
D -> 'more' D

(STRING)
more more more certain

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
OK
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> C
C -> 'activity' C
C -> 'gas'

(PREFIX)
<empty>

(TEMPLATE)
___ activity ___

(SUFFIX)
gas

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
activity activity activity
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
| company         | price   |
|:----------------|:--------|
| Thompson-Owen   | 290.63  |
| Anderson-Wilson | 163.28  |
| Bishop LLC      | 95.23   |
| Bryant Ltd      | 87.03   |
| Paul Inc        | 430.13  |

SQL: SELECT COUNT(*) FROM dataframe WHERE price > 163.28

The answer is the result as single value.
```

**Answer:**
```
2
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: ababbbee
Operations:
- sort ascending
- caesar shift by 4
Answer with the final string.
```

**Answer:**
```
eeffffii
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(z: str, o: int) -> int:
    o += 5
    return f0(z, o)
def f1(u: int) -> str:
    print(u)
    return ""
def endpoint(x0: str, x1: int) -> int:
    return f0(x0, x1)

```
Call: `endpoint('ba', 1)`
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
def f0(y: str) -> list:
    a = [0, 1, 2]
    b = 0
    b -= 7
    return a
def f1(u: str, z: int) -> int:
    z *= 1
    return z + 4
def endpoint(x0: str) -> list:
    return f0(x0)

```
Call: `endpoint('y')`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
[0, 1, 2]
```

---

## [code_input_deduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Find the smallest integer x in [-6, 9] such that `endpoint(x) == target`.
Answer with the integer.

```python
def f0(x: int) -> int:
    x -= 4
    return x


def endpoint(x):
    return f0(x) % 4

```

Target: 0
````

**Answer:**
```
-4
```

---

## [analogical_case_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed, and each link direction may be consistently reversed.

M0
a is alpha-linked to b.
d is alpha-linked to b.
a is beta-linked to c.
b is beta-linked to a.
Implies: a is beta-linked to d.

M1
c is alpha-linked to e.
e is alpha-linked to a.
e is alpha-linked to b.
a is beta-linked to b.
Implies: d is alpha-linked to e.

M2
b is alpha-linked to e.
a is beta-linked to b.
b is beta-linked to c.
d is beta-linked to e.
Implies: d is beta-linked to b.

M3
a is beta-linked to c.
b is beta-linked to a.
e is beta-linked to a.
e is beta-linked to d.
Implies: a is beta-linked to d.

Query
u is delta-linked to y.
x is epsilon-linked to v.
z is epsilon-linked to v.
u is gamma-linked to z.
v is gamma-linked to u.
v is gamma-linked to z.
y is gamma-linked to v.
z is gamma-linked to y.
Implies:
```

**Answer:**
```
z is gamma-linked to x.
```

---

