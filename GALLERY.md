# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`lean_proof_repair`](#lean_proof_repair) · [`conjecture_entailment`](#conjecture_entailment) · [`resolution_step`](#resolution_step) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`planning`](#planning) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_isomorphism`](#graph_isomorphism) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`parsing_derivation`](#parsing_derivation) · [`continuation`](#continuation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_conversion`](#table_conversion) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate (-3 - 7 * 0.8).
The answer is a number.
```

**Answer:**
```
-8.6
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
A jar holds 9 tokens. In order: multiplied by 2; then quadrupled. How many tokens are in the jar now? Give the answer as a number.
```

**Answer:**
```
72
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 + X2 - 39 = 0
  18 - X1 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
21
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem? The answer is exactly True or False.

THEOREM WITH HOLE:
theorem ex (x y : List Nat)  : (x ++ y).length = x.length + y.length := by
  ?

CANDIDATE:
decide
```

**Answer:**
```
False
```

---

## [lean_proof_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Fix the broken Lean 4 proof below. Mathlib is imported. Choose one candidate replacement. The answer is exactly one candidate body.

BROKEN PROOF:
theorem ex (a : Int)  : 0 ≤ |3 * a| := by
  decide

CANDIDATE REPLACEMENTS:
1. exact abs_nonneg (3 * a)
2. omega
3. rfl
4. assumption
```

**Answer:**
```
exact abs_nonneg (3 * a)
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

## [resolution_step](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Apply one step of binary resolution.
Domain: Geometry

Clause A: (~between(lower_dimension_point_3,lower_dimension_point_2,X1) | ~between(X1,lower_dimension_point_1,lower_dimension_point_2))
Clause B: (between(extension(Y1,Y2,Y3,Y4),Y2,Y1))

A and B share no variables. Exactly one pair of complementary literals is unifiable.
The answer is the canonicalized resolvent: literals sorted alphabetically after replacing variables by 'X', then variables renamed X1, X2, ... by first occurrence; e.g. (p(X1,f(X2)) | ~q(X1)).
```

**Answer:**
```
(~between(lower_dimension_point_3,lower_dimension_point_2,extension(lower_dimension_point_2,lower_dimension_point_1,X1,X2)))
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: E=(21/5, -2/5); H=(-2, -4); N=(74/5, -8/5); O=(-3, 2); Q=(5, 2); R=(3, -4); W=(-5, 5).
Definitions: E is the projection of O onto line RQ. N is the reflection of W across line EQ.
Question: What type of angle is angle EOQ?
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

Term: (b ((\_0._0) (\v0.c)))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(b (\v0.c))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- if(false,X,Y) -> Y
- let(unit,X) -> X
- if(true,X,Y) -> X
- id(X) -> X
- const(X,Y) -> X
- fst(pair(X,Y)) -> X

Term: pair(let(if(if(false,snd(pair(c,b)),true),true,let(unit,unit)),b),true)

The answer is the normal form.
```

**Answer:**
```
pair(let(true,b),true)
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor c is independently true with probability 0.3.
Factor e is independently true with probability 0.7.
The observation holds exactly when (factor c or factor e).
We observe it.
Which hidden fact values form the most probable complete explanation?

The answer is a sorted Python list of strings.
```

**Answer:**
```
["not c", "e"]
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A box contains 6 silver balls and 2 gold balls.
Two balls are drawn without replacing the first ball.
Which statement is more likely?
A: the first selected ball is silver.
B: the first selected ball is gold.

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
there is a room.
Ethan is yankee tagged or is yankee tagged or both
if someone is not quiet then he is an old person and vice versa
Reginald is quiet
Reginald is not yankee tagged
at least four people in the room are papa tagged
Hypothesis:
Ethan is yankee tagged

Classify the hypothesis as entailment, contradiction, or neutral. The answer is exactly one word.
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
[0] Jeffery is the only person in the room.
[1] everyone in the room who is not a quiet person is a quiet person
[2] someone who is not bravo tagged hates someone who is sierra tagged
[3] not everyone in the room who is victor tagged is sierra tagged
[4] no old person in the room is old
[5] only one person in the room is victor tagged
Hypothesis:
Jeffery is old

Which statements in the premise contradict the hypothesis?
The answer is the list of supporting statement indices, e.g. [0, 6, 7].
```

**Answer:**
```
[0, 4]
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno parent clara.
clara parent alice.
alice is kind.
clara is not careful.
clara is not kind.
clara is patient.
Whenever x parent y, x ancestor y.
Whenever x parent y and y ancestor z, x ancestor z.
From p parent x and p parent y and x is different from y, it follows that x sibling y.
If one person is sibling to another, then the second is sibling to the first.
Whenever x spouse y, y spouse x.
For all x, y, z, if x parent y and x sibling z, then z aunt or uncle y.

Hypothesis:
bruno does not ancestor alice.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is exactly one word.
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
[0] bruno parent alice.
[1] alice parent clara.
[2] bruno is not adult.
[3] david is careful.
[4] alice is not patient.
[5] alice is trusted.
[6] From x parent y, it follows that x ancestor y.
[7] From x parent y and y ancestor z, it follows that x ancestor z.
[8] From p parent x and p parent y and x is different from y, it follows that x sibling y.
[9] From x sibling y, it follows that y sibling x.
[10] If one person is spouse to another, then the second is spouse to the first.
[11] For all x, y, z, if x parent y and x sibling z, then z aunt or uncle y.

Hypothesis:
bruno ancestor clara.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
The answer is a list of indices, e.g. [0, 1].
```

**Answer:**
```
[0, 1, 6, 7]
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] David is echo tagged.
[1] Clara is bravo tagged.
[2] Anyone who is echo tagged is delta tagged.
[3] From x is delta tagged, it follows that x is not bravo tagged.

Hypothesis:
Bruno is bravo tagged.

Candidate additional facts:
[0] Alice is delta tagged.
[1] Clara is foxtrot tagged.
[2] Bruno is not echo tagged.
[3] Bruno is bravo tagged.
[4] Bruno is echo tagged.
[5] Alice is echo tagged.

Which candidate facts, if added to the premise, make the premise contradict the hypothesis?
The answer is the smallest list of candidate indices, e.g. [0, 2].
```

**Answer:**
```
[4]
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
clara is trusted.
david helps bruno.
clara is active.
alice advises bruno.
bruno is careful.
Being trusted implies being verified.
Every verified entity is active.
Every active entity is careful.
Every careful entity is trained.
Anyone who is trained and approved is active.
Whenever x helps y, y advises x.
Anyone who is verified and careful is approved.
From x advises y and x is active, it follows that y is trained.
Every trusted entity is careful.

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
  Requires: (not fluent_3(x0)), (not fluent_2(x0))
  Effect: not fluent_0(x0), fluent_3(x0), not fluent_1, fluent_2(x0)

Initial state:
True values: None

Goal:
fluent_2(object_1)
Hint: Reference solution has 1 actions (but it may not be optimal).

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
Set1: {473, 892, 97, 238, 717, 188, 54, 522}
Set2: {54, 213, 144, 522, 106, 238}
The answer is Set1 ∩ Set2 as a Python set.
```

**Answer:**
```
{54, 238, 522}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {'ninety-eight', 'ninety-five', 'ninety-seven', 'eighty-nine', 'ninety-two', 'ninety-four', 'ninety', 'ninety-one', 'ninety-six'}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{'ninety-three'}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: [2, 7, 5, 4, 8, 10, 20, 20, 19, 15]
How many times does 2 appear? The answer is a number.
```

**Answer:**
```
1
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {536, 668, 519, 22, 386, 214, 30, 172}
Set2: {386, 30, 214, 519, 668, 22, 172, 536}
Do Set1 and Set2 contain exactly the same elements? The answer is True or False.
```

**Answer:**
```
True
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer a recurrence for sequence [U0, U1, ..., U7] indexed from 0.
Max recurrence degree: 1.

Allowed binary ops: +, -, *, **
- Previous terms must be referenced exactly as: U[n - 1] ... U[n - 1]
- You may use "n" (current index).
- The answer is the right-hand side only (do not write "U[n] =").

Sequence: [8, 9, 11, 14, 18, 23, 29, 36]
Initial terms: [8]

The answer should be as simple as possible and valid for all n >= d.
```

**Answer:**
```
n + U[n - 1]
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E4 is newer than E2.
- E3 is the newest.
- E1 is newer than E4.
- E1 is the 3rd-newest.

Which object is the 4th-oldest?
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
Objects occupy distinct points on the integer grid [0, 4] x [0, 4].
North is +y and East is +x. Any object not mentioned in a step stays fixed.
Initial facts:
- A is left of C.
- C is right of B.
- A starts at (1, 1).
- C is above B.
- A is left of B.
- A is below B.
- C is above A.
- C starts at (3, 4).
Steps:
1. B jumps to A's position offset by (-1, -1).
What is the final coordinate of A? The answer is (x, y).
```

**Answer:**
```
(1, 1)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: yellow
- b2: white
- b3: yellow
- b4: yellow
Initial state:
- b1 is in x2
- b2 is in x1
- b3 is in x2
- b4 is in x3
Moves:
- Move b2 from x1 to x3.
- Move b4 from x3 to x1.
- Transfer b2 from x3 into x2.
- Move it from x2 to x3.
Where is b1 now? The answer is a box tag, like x1.
```

**Answer:**
```
x2
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A kind old doctor named Sara helped a kind short engineer named Zoe.
(2) Zoe questioned a loud old pilot named Leo.
(3) She avoided him.
(4) A kind loud nurse named Lily questioned Sara.
(5) Sara praised Lily.
(6) A loud young scientist named Kate called Leo.
(7) He avoided her.

In sentence 3, what does the subject expression 'She' refer to?
The answer is the person's name.
```

**Answer:**
```
Zoe
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
Variables/domains:
- 0 <= x0 <= 1
- 0 <= x1 <= 1

Constraints:
1. -x1 == 0
2. (x0 + 3*x1) % 3 == 1
3. -3*x0 <= -1
Enumerate ALL satisfying assignments in variable order [x0, x1].
The answer is a lexicographically sorted Python list of int lists, or UNSAT.

```

**Answer:**
```
[[1, 0]]
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

0: 0->1 0->4 0->5; 1:; 2: 2->0; 3: 3->1; 4:; 5: 5->0

Find the lexicographically smallest shortest directed path from Node 5 to Node 0.
The answer is a Python list of nodes, or `None` if no path exists.
```

**Answer:**
```
[5, 0]
```

---

## [graph_isomorphism](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider two directed graphs described below.

Graph A:
0: 0->1; 1: 1->2 1->5; 2: 2->1; 3: 3->1; 4: 4->2; 5: 5->1

Graph B:
0: 0->1; 1: 1->3; 2:; 3: 3->0 3->2; 4: 4->5; 5: 5->1 5->4

Are Graph A and Graph B isomorphic?
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

digraph { 0->3; 1->1; 2->5; 3->4; 4->0; 5->2 }

Queries: [(2, 2)]
Each pair (x, k) asks for the k-th successor of x (following exact directed edges k times).
The answer is a Python list of integers in query order.
```

**Answer:**
```
[2]
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

digraph { 1->3; 2->3; 5->1; 5->4 }

In this scenario, a directed edge from U to V means V depends on U (so U is a prerequisite of V).
List all prerequisites of node 3 (recursively), making sure to order base prerequisites first.
Exclude the query node; prerequisites must precede dependents, with lexicographic tie-breaks.
The answer is a Python list of integers.
```

**Answer:**
```
[2, 5, 1]
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 5-character string that fully matches the regular expression: [4s5]+
```

**Answer:**
```
5545s
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'abd', 'c'
Negative: 'a', 'adbdb', 'bccca', 'cb', 'd', 'dbb', 'dca', 'dcc'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
abd|c
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: v, 1\, imageWz, Democrat8, 4\, .
Regex: \d\\{1}
The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. The answer is [] if none.
```

**Answer:**
```
["1\\","4\\"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = (aba)
B = (abc)
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
( ( ) ) [ ]

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R2 R3 R2 R3 R1 R1 R2 R4 R1 R1
```

---

## [continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
List valid next tokens for this prefix. The answer is the valid tokens sorted alphabetically and separated by |, with STOP at the end if the prefix forms a complete string.
(GRAMMAR)
S -> A
A -> 'rock'
A -> 'rock' A
(PREFIX)
rock rock rock rock
```

**Answer:**
```
rock|STOP
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> D
D -> 'national'
D -> D 'hour'

(STRING)
national hour national hour hour

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
hour >>national<<
```

---

## [constrained_continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> A
A -> 'relate'
A -> A 'factor'

(PREFIX)
<empty>

(TEMPLATE)
relate ___ ___ factor

(SUFFIX)
<empty>

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 4 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
relate factor factor factor
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
date,product
2026-04-08,Structure
2025-07-26,Interview
2026-02-06,Research
2025-10-09,Short
2025-06-26,Successful


SQL: SELECT COUNT(*) FROM dataframe WHERE product = 'Interview'

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
Convert the following table from yaml to html.

- price: '424.73'
  date: 2025-08-23
- price: '315.78'
  date: 2025-11-13
- price: '350.42'
  date: 2026-05-22
- price: '215.47'
  date: 2025-10-15
- price: '53.21'
  date: 2025-09-07


The answer is the converted table.
```

**Answer:**
```
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>price</th>
      <th>date</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>424.73</td>
      <td>2025-08-23</td>
    </tr>
    <tr>
      <td>315.78</td>
      <td>2025-11-13</td>
    </tr>
    <tr>
      <td>350.42</td>
      <td>2026-05-22</td>
    </tr>
    <tr>
      <td>215.47</td>
      <td>2025-10-15</td>
    </tr>
    <tr>
      <td>53.21</td>
      <td>2025-09-07</td>
    </tr>
  </tbody>
</table>
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: adbdbceb
Edits:
- insert e at index 8
- replace index 5 with a
- delete at index 3
Answer with the final string.
```

**Answer:**
```
adbbaebe
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(n: str) -> list:
    a = f0(n)
    print(n)
    return a
def f1(t: list, r: str) -> str:
    a = [0, 1, 2]
    return f1(a, r)
def endpoint(x0: str) -> list:
    return f0(x0)

```
Call: `endpoint('ax')`
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
def f0(k: list, a: int) -> str:
    a = a
    return f1(8, k)
def f1(q: int, s: list) -> str:
    print(q)
    return ""
def endpoint(x0: list, x1: int) -> str:
    return f0(x0, x1)

```
Call: `endpoint([1, -1, 0], -2)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
''
```

---
