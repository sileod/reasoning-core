# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`equation_system`](#equation_system) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`lean_proof_repair`](#lean_proof_repair) · [`conjecture_entailment`](#conjecture_entailment) · [`resolution_step`](#resolution_step) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`bayesian_intervention`](#bayesian_intervention) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`planning`](#planning) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_isomorphism`](#graph_isomorphism) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`lexical_knowledge`](#lexical_knowledge) · [`parsing_derivation`](#parsing_derivation) · [`continuation`](#continuation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_conversion`](#table_conversion) · [`diff_prediction`](#diff_prediction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate -3 - -8.
The answer is a number.
```

**Answer:**
```
5
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 + 23 = 0
  3*X1 + X2 + 82 = 0

The answer is the numerical value for X2, or 'No solution' / 'Multiple solutions' if a unique numerical solution does not exist.
```

**Answer:**
```
-13
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Decide whether the candidate Lean 4 tactic body closes the theorem.
The answer is exactly True or False.

THEOREM WITH HOLE:
theorem ex (a b : Int)  : 1 = (1 + 0 * b) := by
  ?

CANDIDATE:
omega
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

theorem ex (b : Int)  : |2 * b + 3| ≤ |2 * b| + |3| := by
  decide

```

**Answer:**
```
exact abs_add_le (2 * b) (3)
```

---

## [conjecture_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the given premises entail the conjecture (i.e., the conjecture is provable) using Superposition/Resolution/Paramodulation.

Domain: Group Theory

Premises:
- (product(X1,X2,X3,X3)|~product(X4,X5,X6,identity_for(X1))|~product(X4,X5,X6,X2))
- (product(X1,X2,X3,identity_for(X1))|~product(X4,inverse(X1,X3),identity_for(X4),X2))

Conjecture: `(product(X1,X2,X3,X3)|~product(X4,inverse(X1,X5),identity_for(X4),X6)|~product(X1,X6,X5,X2))`

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
Domain: Group Theory

Clause A: (equalish(multiply(X1,X2),X3) | ~product(X1,X2,X3))
Clause B: (equalish(Y1,Y2) | ~equalish(Y3,Y2) | ~product(identity,Y1,Y3))

A and B share no variables. Exactly one pair of complementary literals is unifiable.
Answer convention: write the conclusion with literals sorted alphabetically
(comparing literal text with every variable replaced by 'X'), and variables
renamed X1, X2, ... in order of first occurrence in that sorted clause.
The answer is the canonicalized resolvent, e.g. (p(X1,f(X2)) | ~q(X1)).
```

**Answer:**
```
(equalish(X1,X2) | ~product(X3,X4,X2) | ~product(identity,X1,multiply(X3,X4)))
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: B=(-4, 3); C=(0, -2); E=(0, -1); K=(-2, 1); O=(-4, 2); T=(-6, 3); Y=(-4, -5); Z=(4, -3).
Definitions: K is the midpoint of E and B. T is the translation of K by vector p2p4.
Question: Is point O on segment p5p6?
Return exactly one of: yes, no.
Return only the answer.
```

**Answer:**
```
yes
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` denotes λx.body; application is left-associative juxtaposition; free identifiers are treated as constants.

Term: (\v0.((\_0.v0) c))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(\v0.v0)
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- xor(X,X) -> false
- imp(true,X) -> X
- xor(X,true) -> not(X)
- iff(X,X) -> true
- imp(X,true) -> true
- xor(true,X) -> not(X)

Term: not(imp(true,imp(q,imp(true,imp(true,r)))))

The answer is the normal form.
```

**Answer:**
```
not(imp(q,r))
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor d is independently true with probability 0.7.
Factor b is independently true with probability 0.1.
The observation holds exactly when (factor d or factor b).
We observe it.
Which hidden fact values form the most probable complete explanation?

Answer as a sorted Python list of strings.
```

**Answer:**
```
["not b", "d"]
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A box contains 3 silver balls and 7 gold balls.
Two balls are drawn with the first ball replaced before the second selection.
Which statement is more likely?
A: at least one selected ball is silver.
B: both selected balls are gold.

Answer exactly one of: A, B, equal.
```

**Answer:**
```
A
```

---

## [bayesian_intervention](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/causal_reasoning.py)

**Prompt:**
```
System:
P(X_0) = {'0': 0.4, '1': 0.6} 
P(X_2|X_0=0) = {'0': 0.4, '1': 0.6} 
P(X_2|X_0=1) = {'0': 0.2, '1': 0.8} 
P(X_3|X_0=0) = {'0': 0.4, '1': 0.6} 
P(X_3|X_0=1) = {'0': 0.6, '1': 0.4} 
P(X_1) = {'0': 0.8, '1': 0.2}
Observed conditions:
Doing/Imposing that the state X_3 is equal to 0
Task: Compute probability distribution for X_1 (possible values: [0, 1]).

The answer is a Python dict mapping each value to its probability, rounded to 1 decimals.
Example: {0: 0.1, 1: 0.9}
```

**Answer:**
```
{0: 0.8, 1: 0.2}
```

---

## [logic_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
Shannon is the only person in the room.
everyone in the room is foxtrot tagged
everyone in the room either is an old person or is not delta tagged or both
everyone in the room is not quiet and not old if and only if she is quiet
not everyone outside the room who is foxtrot tagged is not papa tagged
Janice is india tagged
Hypothesis:
Shannon is not not quiet

If the Premise entails the Hypothesis, the label is 'entailment'.
If the Premise contradicts the Hypothesis, the label is 'contradiction'.
If neither, the label is 'neutral'.
The answer is exactly one word: neutral, contradiction, or entailment.
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
[0] there is a room.
[1] if someone is old then he is old
[2] if someone is golf tagged then he is quiet and vice versa
[3] Matthew who is quiet is an old person
[4] Kenneth is a quiet person
[5] everyone in the room is not an old person if he is quiet
Hypothesis:
Matthew is an old person

Which statements in the premise entail the hypothesis?
The answer is the list of supporting statements, e.g. [0, 6, 7].
```

**Answer:**
```
[3]
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno parent clara.
clara parent alice.
david is minor.
alice trusts david.
david spouse bruno.
david ancestor alice.
Whenever x parent y, x ancestor y.
If one person is parent to a second person, and the second is ancestor to a third, then the first is ancestor to the third.
Whenever p parent x and p parent y and x is different from y, x sibling y.
Whenever x sibling y, y sibling x.
For all x, y, if x spouse y, then y spouse x.
From x parent y and x sibling z, it follows that z aunt or uncle y.

Hypothesis:
bruno ancestor alice.

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

## [multistep_evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] david parent bruno.
[1] bruno parent clara.
[2] bruno is adult.
[3] clara sibling david.
[4] alice is trusted.
[5] david ancestor clara.
[6] For all x, y, if x parent y, then x ancestor y.
[7] Anyone parent to someone who is ancestor to a third person is ancestor to that third person.
[8] From p parent x and p parent y and x is different from y, it follows that x sibling y.
[9] If one person is sibling to another, then the second is sibling to the first.
[10] Whenever x spouse y, y spouse x.
[11] Whenever x parent y and x sibling z, z aunt or uncle y.

Hypothesis:
clara aunt or uncle bruno.

Which premise statements are necessary to entail the hypothesis, meaning removing any one of them breaks that result?
The answer is a list of indices, e.g. [0, 1].
```

**Answer:**
```
[0, 3, 9, 11]
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] Clara is echo tagged.
[1] Bruno is alpha tagged.
[2] For all x, if x is echo tagged, then x is foxtrot tagged.
[3] For all x, if x is foxtrot tagged, then x is not delta tagged.

Hypothesis:
David is delta tagged.

Candidate additional facts:
[0] David is alpha tagged.
[1] David is echo tagged.
[2] David is not echo tagged.

Which candidate facts, if added to the premise, make the premise contradict the hypothesis?
Return the smallest list of candidate indices, e.g. [0, 2].
```

**Answer:**
```
[1]
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
[OBJECTS]
object_1, object_2, object_3, object_4, object_5

[ACTIONS]
action_0(x0)
  Requires: (not fluent_0), (not fluent_1(x0))
  Effect: fluent_0, fluent_1(x0)
action_1(x0, x1)
  Requires: fluent_1(x0), fluent_1(x1)
  Effect: not fluent_1(x0), fluent_0, not fluent_1(x1)

[STATE]
Initial true values: None

[GOAL]

fluent_0, (not fluent_1(object_3))
The answer is the plan.
Answer format: Multiple lines, one action per line: action(obj1, obj2)
```

**Answer:**
```
    action_0(object_4)
```

---

## [set_intersection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {977, 518, 690, 24, 580, 510, 729, 84}
Set2: {24, 698, 518, 84, 96, 451}
The answer is the intersection of Set1 and Set2 as a Python set: {elem_1, elem_2, ..., elem_n}.
```

**Answer:**
```
{24, 84, 518}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {524, 523, 518, 526, 517, 522, 520, 519, 525}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{521}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: ['2020-01-11', '2020-01-20', '2020-01-03', '2020-01-18', '2020-01-15', '2020-01-14', '2020-01-03', '2020-01-18', '2020-01-11', '2020-01-20']
How many times does '2020-01-12' appear? The answer is a number.
```

**Answer:**
```
0
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {'re', 'mi', 'dd', 'ma', 'bo', 'ef', 'ca', 'ep'}
Set2: {'mi', 'dd', 'ef', 'ep', 'agi', 're', 'ma', 'ca'}
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
Max recurrence degree: 1.

Allowed binary ops: +, -, *, **
- Previous terms must be referenced exactly as: U[n - 1] ... U[n - 1]
- You may use "n" (current index).
- The answer is the right-hand side only (do not write "U[n] =").
- Your recurrence degree must be <= 1.

Sequence: [8, 9, 11, 14, 18, 23, 29, 36]
Degree of recurrence: 1
Initial terms: [8]

The answer must hold for all n >= d and be as simple as possible.
```

**Answer:**
```
n + U[n - 1]
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 entities labeled 0 through 4.
You are given the following facts (read 'i rel j' as 'entity i is rel to entity j'):
  2 starts 3
  1 starts 2
  4 after 2
  0 started-by 1
  0 before 4
  0 equals 2

What is the relation of the vertical extent of box 3 to that of box 0?
The answer is exactly one of: after, before, contains, during, equals, finished-by, finishes, meets, met-by, overlapped-by, overlaps, started-by, starts.
```

**Answer:**
```
started-by
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Objects occupy distinct points on the integer grid [0, 4] x [0, 4].
North is +y and East is +x. Any object not mentioned in a step stays fixed.
Initial facts:
- B is above A.
- C is right of B.
- B starts at (2, 3).
- B is above C.
- A is left of B.
- C is right of A.
- A starts at (1, 0).
- C is above A.
Steps:
1. C and A swap positions.
What is the final coordinate of B? Answer as (x, y).
```

**Answer:**
```
(2, 3)
```

---

## [reference_tracking](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/tracking.py)

**Prompt:**
```
Inventory:
- b1: green
- b2: green
- b3: white
- b4: black
Initial state:
- b1 is in x2
- b2 is in x3
- b3 is in x2
- b4 is in x3
Moves:
- Transfer b3 from x2 into x1.
- Relocate b3 from x1 to x2.
- Relocate b4 from x3 to x1.
- Move b3 from x2 to x1.
Where is b2 now? The answer is a box tag, like x1.
```

**Answer:**
```
x3
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A quiet stern teacher named Paul helped a kind old farmer named Sara.
(2) He called a loud short baker named Hugo.
(3) The stern teacher praised a tall young chef named Kate.
(4) A quiet young teacher named Tom called the chef.
(5) She greeted the stern teacher.
(6) He met a quiet stern writer named Ben.

In sentence 5, what does the subject expression 'She' refer to?
The answer is the name of the person it refers to.
```

**Answer:**
```
Kate
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
Variables/domains:
- 0 <= x0 <= 2
- 0 <= x1 <= 1

Constraints:
1. -2*x0 + 3*x1 >= -4
2. (3*x1) % 3 == 0
3. -x0 - x1 != 0
Enumerate ALL satisfying assignments in variable order [x0, x1].
The answer is a Python list of lists of ints, sorted lexicographically, or UNSAT if no assignment exists.

```

**Answer:**
```
[[0, 1], [1, 0], [1, 1], [2, 0], [2, 1]]
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

0: 0->2 0->5; 1: 1->4 1->5; 2: 2->0 2->3 2->5; 3: 3->1 3->2 3->4; 4: 4->0 4->3; 5: 5->0 5->1 5->2

Find the lexicographically smallest shortest directed path from Node 2 to Node 3.
If no path exists, answer `None`.
The answer is a Python list of nodes or `None`.
```

**Answer:**
```
[2, 3]
```

---

## [graph_isomorphism](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider two directed graphs described below.

Graph A:
0: 0->1 0->2; 1:; 2: 2->0 2->4; 3: 3->0 3->2; 4: 4->1 4->2 4->5; 5: 5->2

Graph B:
0: 0->2; 1:; 2: 2->0 2->4; 3: 3->0 3->2; 4: 4->1 4->2 4->5; 5: 5->1

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

0: 0->1; 1: 1->0; 2: 2->2; 3: 3->4; 4: 4->3; 5: 5->5

Queries: [(0, 2)]
Each pair (x, k) asks for the k-th successor of x (following exact directed edges k times).
The answer is a Python list of integers in query order.
```

**Answer:**
```
[0]
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

digraph { 3->1; 3->5; 5->4 }

In this scenario, a directed edge from U to V means V depends on U (so U is a prerequisite of V).
List all prerequisites of node 4 (recursively), making sure to order base prerequisites first.
Do not include the query node itself.
If A is a prerequisite of B and both appear in your answer, A must appear before B.
Tie-break nodes with no mutual dependency lexicographically (smaller node ID first).
The answer is a Python list of integers.
```

**Answer:**
```
[3, 5]
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 4-character string that fully matches the regular expression: .{3,5}
```

**Answer:**
```
swN/
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'a', 'ad', 'add', 'addd', 'adddd', 'd'
Negative: 'aaa', 'aab', 'b', 'c', 'caab', 'cc', 'dba', 'dd'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
ad*|d
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: Network believe eat that. Support board Mr behavior.
Regex: \b[a-z]{4,7}\b
Return only a JSON array of exact non-overlapping matches, left-to-right. Include duplicates. Return [] if none.
```

**Answer:**
```
["believe","that","board"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Consider the regular expressions A = ab|c? and B = baa?
Do A and B accept exactly the same set of strings?
The answer is Yes or No.
```

**Answer:**
```
No
```

---

## [lexical_knowledge](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/knowledge.py)

**Prompt:**
```
Context: WordNet (relation holds for any valid noun sense).

Select hypernym(teacher)
From: [lad, educator, amateur, monk, actor, conveyor]
The answer is one word.
```

**Answer:**
```
educator
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: S -> B
R1: B -> B 'yet'
R2: B -> 'student'
R3: B -> C

(STRING)
student yet yet yet

(QUESTION)
Return the rule labels used in the leftmost derivation of STRING.
Answer only the labels in order, separated by spaces.
```

**Answer:**
```
R0 R1 R1 R1 R2
```

---

## [continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
List all valid next tokens for this prefix. The answer is the list of valid tokens sorted alphabetically and separated by |, with STOP at the end if the prefix forms a complete string.
(GRAMMAR)
S -> B
B -> 'top' B
B -> 'church'
(PREFIX)
top top
```

**Answer:**
```
church|top
```

---

## [locate_error](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
S -> A
A -> A 'environment'
A -> 'clear'

(STRING)
clear environment environment environment clear environment

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
environment >>clear<<
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
< [

(TEMPLATE)
___ < ___

(SUFFIX)
> [ ] [ ]

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 3 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
] < >
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
      customer  product
   Tracy Smith    Young
   Ashley Shaw    Clear
  Lindsey Hunt National
    Taylor Ray     Long
Jennifer Weber     Drug

SQL: SELECT COUNT(*) FROM dataframe WHERE CAST(customer AS VARCHAR) LIKE '%racy Smith%'

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
Convert the following table from latex to json.

\begin{tabular}{ll}
\toprule
product & job \\
\midrule
Find & Engineer, drilling \\
Interview & Best boy \\
Like & Programme researcher, broadcasting/film/video \\
Than & Scientist, biomedical \\
Staff & Writer \\
\bottomrule
\end{tabular}


The answer is the converted table.
```

**Answer:**
```
[
    {
        "product":"Find",
        "job":"Engineer, drilling"
    },
    {
        "product":"Interview",
        "job":"Best boy"
    },
    {
        "product":"Like",
        "job":"Programme researcher, broadcasting\/film\/video"
    },
    {
        "product":"Than",
        "job":"Scientist, biomedical"
    },
    {
        "product":"Staff",
        "job":"Writer"
    }
]
```

---

## [diff_prediction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_diff.py)

**Prompt:**
```
Below is the version history of a file.

Version a35e8c6:
1    | Information important including official state bar
2    | Individual significant line impact clearly wish education voice
3    | Window door tonight west
4    | Happen every then discussion occur
5    | Development land decade

Version cb469be:
1    | Information business including official state bar
2    | Individual significant line impact clearly wish education voice
3    | Window door tonight west
4    | Happen every then discussion occur
5    | Development land decade

Generate the Unified Diff to transform version a35e8c6 into version cb469be.
The answer is the diff chunks only (no file headers), or empty if no changes.
```

**Answer:**
```
@@ -1,4 +1,4 @@
-Information important including official state bar
+Information business including official state bar
 Individual significant line impact clearly wish education voice
 Window door tonight west
 Happen every then discussion occur
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(y: int) -> int:
    try:
        y = y + y
    except Exception:
        y = (y // 4) + y
    return y
def f1(p: str) -> int:
    pass
    return 0
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(-2)`
Answer is `OK` if it runs successfully; exception class name otherwise.
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
def f0(m: int) -> list:
    m = 2
    print(m)
    return []
def f1(e: int) -> str:
    a = 7
    a = e + 3
    return ""
def endpoint(x0: int) -> list:
    return f0(x0)

```
Call: `endpoint(-3)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
[]
```

---

