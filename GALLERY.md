# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`word_problem_math`](#word_problem_math) · [`equation_system`](#equation_system) · [`lean_candidate_compilation`](#lean_candidate_compilation) · [`lean_proof_repair`](#lean_proof_repair) · [`conjecture_entailment`](#conjecture_entailment) · [`resolution_step`](#resolution_step) · [`planar_geometry_relations`](#planar_geometry_relations) · [`lambda_reduction`](#lambda_reduction) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`logic_nli`](#logic_nli) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`planning`](#planning) · [`set_intersection`](#set_intersection) · [`set_missing_element`](#set_missing_element) · [`count_elements`](#count_elements) · [`set_equality`](#set_equality) · [`sequential_induction`](#sequential_induction) · [`qualitative_reasoning`](#qualitative_reasoning) · [`navigation`](#navigation) · [`reference_tracking`](#reference_tracking) · [`coreference`](#coreference) · [`constraint_satisfaction`](#constraint_satisfaction) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_isomorphism`](#graph_isomorphism) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`regex_following`](#regex_following) · [`regex_induction`](#regex_induction) · [`regex_retrieval`](#regex_retrieval) · [`regex_reasoning`](#regex_reasoning) · [`parsing_derivation`](#parsing_derivation) · [`continuation`](#continuation) · [`locate_error`](#locate_error) · [`constrained_continuation`](#constrained_continuation) · [`table_qa`](#table_qa) · [`table_conversion`](#table_conversion) · [`diff_prediction`](#diff_prediction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate 13 + 8.
The answer is a number.
```

**Answer:**
```
21
```

---

## [word_problem_math](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
A jar holds 5 tokens. In order: 11 more tokens added; then 8 more tokens added. How many tokens are in the jar now? Give the answer as a number.
```

**Answer:**
```
24
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X2'.

System:
  X1 - 19 = 0
  X2 - 7 = 0

The answer is the value of X2, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
7
```

---

## [lean_candidate_compilation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_lean.py)

**Prompt:**
```
Does this Lean 4 tactic body close the theorem? The answer is exactly True or False.

THEOREM WITH HOLE:
theorem ex (p0 p4 : Prop)  : (p0 → p4) → (¬ p4 → ¬ p0) := by
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
Fix the broken Lean 4 proof below. Mathlib is imported. Choose one candidate replacement. The answer is exactly one candidate body.

BROKEN PROOF:
theorem ex (s t u : Finset Nat)  : t ∩ (s ∩ u) = (t ∩ s) ∩ u := by
  assumption

CANDIDATE REPLACEMENTS:
1. omega

2. ext x; simp [and_assoc]

3. rfl

4. decide
```

**Answer:**
```
ext x; simp [and_assoc]
```

---

## [conjecture_entailment](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
Decide if the premises entail the conjecture.

Domain: Group Theory

Premises:
- (greatest_lower_bound(X1,multiply(inverse(greatest_lower_bound(multiply(X2,inverse(X1)),X3)),X2))=X1)
- (greatest_lower_bound(identity,multiply(inverse(greatest_lower_bound(X1,X2)),X1))=identity)
- (greatest_lower_bound(X1,greatest_lower_bound(X2,greatest_lower_bound(X3,X1)))=greatest_lower_bound(X2,greatest_lower_bound(X3,X1)))

Conjecture: `(greatest_lower_bound(identity,multiply(inverse(greatest_lower_bound(X1,greatest_lower_bound(X2,X3))),X3))=identity)`

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
Domain: Algebra

Clause A: (associative(X1,X2) | member(f34(X1,X2),X1))
Clause B: (ordered_pair_predicate(Y1) | ~relation(universal_set) | ~member(Y1,Y2))

A and B share no variables. Exactly one pair of complementary literals is unifiable.
The answer is the canonicalized resolvent: literals sorted alphabetically after replacing variables by 'X', then variables renamed X1, X2, ... by first occurrence; e.g. (p(X1,f(X2)) | ~q(X1)).
```

**Answer:**
```
(associative(X1,X2) | ordered_pair_predicate(f34(X1,X2)) | ~relation(universal_set))
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: D=(4, 4); I=(3, 2); K=(-3, -5); M=(5, -5); N=(221/53, 207/53); O=(-2, -3); X=(1, 3).
Definitions: X is the 90-degree counterclockwise rotation of D about I. N is the reflection of X across line IM.
Question: What type of angle is angle NIK?
Answer is one of: acute, right, obtuse.
```

**Answer:**
```
obtuse
```

---

## [lambda_reduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Reduce the following untyped λ-term to β-normal form.
Syntax: `\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.

Term: (\v0.(((\_0.(_0 _0)) v0) v0))

The answer is the β-normal form (compared up to α-equivalence).
```

**Answer:**
```
(\v0.((v0 v0) v0))
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- norm(norm(X)) -> norm(X)
- join(dot,X) -> X
- join(X,dot) -> X
- parent(join(X,Y)) -> X
- join(root,X) -> norm(X)
- base(join(X,Y)) -> Y

Term: parent(join(join(dot,join(dot,base(base(base(tmp))))),parent(base(root))))

The answer is the normal form.
```

**Answer:**
```
base(base(base(tmp)))
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor b is independently true with probability 0.4.
Factor c is independently true with probability 0.3.
The observation holds exactly when (factor b or factor c).
We observe it.
Which hidden fact values form the most probable complete explanation?

The answer is a sorted Python list of strings.
```

**Answer:**
```
["b", "not c"]
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A box contains 8 blue balls and 6 red balls.
Two balls are drawn without replacing the first ball.
Which statement is more likely?
A: both selected balls are blue.
B: both selected balls are red.

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
Amber is golf tagged
someone in the room is not romeo tagged
Amber and Sarah are respectively quiet and quiet
if someone is sierra tagged then she is an old person
everyone in the room is not juliet tagged if she is uniform tagged
Hypothesis:
Julie is an old person

Classify the hypothesis as entailment, contradiction, or neutral. The answer is exactly one word.
```

**Answer:**
```
neutral
```

---

## [evidence_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_semantics.py)

**Prompt:**
```
Premise:
[0] there is a room.
[1] Mary dreamt that “all old people in the room are quiet”
[2] Mark is not hotel tagged
[3] Mark who is india tagged is alpha tagged
[4] everyone in the room either is not lima tagged or is foxtrot tagged or both
[5] Joshua is november tagged
Hypothesis:
Mark is hotel tagged

Which statements in the premise contradict the hypothesis?
The answer is the list of supporting statement indices, e.g. [0, 6, 7].
```

**Answer:**
```
[2]
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno parent david.
david parent clara.
clara is trusted.
alice does not parent clara.
david does not aunt or uncle alice.
clara is patient.
Whenever x parent y, x ancestor y.
If one person is parent to a second person, and the second is ancestor to a third, then the first is ancestor to the third.
For all p, x, y, if p parent x and p parent y and x is different from y, then x sibling y.
From x sibling y, it follows that y sibling x.
For all x, y, if x spouse y, then y spouse x.
For all x, y, z, if x parent y and x sibling z, then z aunt or uncle y.

Hypothesis:
bruno ancestor clara.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is exactly one word.
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
[0] alice parent clara.
[1] clara parent david.
[2] bruno sibling clara.
[3] alice does not helps clara.
[4] clara is adult.
[5] david ancestor bruno.
[6] From x parent y, it follows that x ancestor y.
[7] Anyone parent to someone who is ancestor to a third person is ancestor to that third person.
[8] Whenever p parent x and p parent y and x is different from y, x sibling y.
[9] Whenever x sibling y, y sibling x.
[10] Whenever x spouse y, y spouse x.
[11] Whenever x parent y and x sibling z, z aunt or uncle y.

Hypothesis:
alice ancestor david.

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
[0] Clara is alpha tagged.
[1] David is bravo tagged.
[2] Every alpha-tagged person is foxtrot tagged.
[3] Anyone who is foxtrot tagged is echo tagged.

Hypothesis:
Bruno is echo tagged.

Candidate additional facts:
[0] Bruno is not alpha tagged.
[1] Alice is alpha tagged.
[2] Bruno is delta tagged.
[3] Alice is foxtrot tagged.
[4] Clara is bravo tagged.
[5] Bruno is alpha tagged.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
The answer is the smallest list of candidate indices, e.g. [0, 2].
```

**Answer:**
```
[5]
```

---

## [planning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/planning.py)

**Prompt:**
```
[OBJECTS]
object_1

[ACTIONS]
action_0(x0, x1)
  Requires: fluent_0
  Effect: not fluent_0
action_1(x0, x1)
  Requires: fluent_0
  Effect: not fluent_0
action_2(x0)
  Requires: (not fluent_0)
  Effect: fluent_0

[STATE]
Default: False
Initial true values: None

[GOAL]

fluent_0
The answer is the plan, one action per line: action(obj1, obj2).
```

**Answer:**
```
    action_2(object_1)
```

---

## [set_intersection](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {797, 74, 20, 694, 324, 260, 544, 35}
Set2: {159, 74, 20, 104, 324, 881}
The answer is Set1 ∩ Set2 as a Python set.
```

**Answer:**
```
{20, 74, 324}
```

---

## [set_missing_element](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set_A: {232, 225, 230, 229, 234, 228, 231}
The answer is the missing elements from Set_A as a Python set.
```

**Answer:**
```
{226, 227, 233}
```

---

## [count_elements](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
List: ['j', 'f', 'n', 'f', 'o', 'k', 'r', 'h', 'r', 'r']
How many times does 'r' appear? The answer is a number.
```

**Answer:**
```
3
```

---

## [set_equality](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/set_operations.py)

**Prompt:**
```
Set1: {366, 469, 821, 78, 667, 353, 730, 34}
Set2: {667, 821, 353, 730, 78, 366, 469}
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
Infer a recurrence for sequence [U0, U1, ..., U7] indexed from 0.
Max recurrence degree: 1.

Allowed binary ops: +, -, *, **
- Previous terms must be referenced exactly as: U[n - 1] ... U[n - 1]
- You may use "n" (current index).
- The answer is the right-hand side only (do not write "U[n] =").

Sequence: [-2, 3, 1, 8, 8, 17, 19, 30]
Initial terms: [-2]

The answer should be as simple as possible and valid for all n >= d.
```

**Answer:**
```
n**2 - U[n - 1]
```

---

## [qualitative_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/qstr.py)

**Prompt:**
```
There are 5 objects: E0, E1, E2, E3, E4.
They have distinct ages.
Facts:
- E2 is the 5th-newest.
- E4 is the 3rd-newest.
- E0 is immediately newer than E1.

Which object is the 2nd-oldest?
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
Objects occupy distinct points on the integer grid [0, 4] x [0, 4].
North is +y and East is +x. Any object not mentioned in a step stays fixed.
Initial facts:
- B is below A.
- C is above B.
- C is in the same column as B.
- A is below C.
- A is right of B.
- A is right of C.
Steps:
1. B jumps to C's position offset by (1, -1).
What is the final Manhattan distance between B and C? The answer is an integer.
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
- b1: white
- b2: yellow
- b3: white
- b4: black
Initial state:
- b1 is in x3
- b2 is in x2
- b3 is in x3
- b4 is in x1
Moves:
- Relocate b3 from x3 to x1.
- Relocate all balls from x1 to x3.
- Move b3 from x3 to x1.
- Move b3 from x1 to x3.
Where is b1 now? The answer is a box tag, like x1.
```

**Answer:**
```
x3
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) A kind quiet nurse named Leo questioned a quiet stern engineer named Mary.
(2) A quiet tall writer named Hugo called her.
(3) He helped Mary.
(4) He helped a loud short lawyer named Eric.
(5) Mary helped Eric.
(6) He met Hugo.
(7) Leo called the lawyer.

In sentence 4, what does the subject expression 'He' refer to?
The answer is the person's name.
```

**Answer:**
```
Hugo
```

---

## [constraint_satisfaction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/constraint_satisfaction.py)

**Prompt:**
```
Variables/domains:
- 0 <= x0 <= 1
- 0 <= x1 <= 2

Constraints:
1. 2*x1 <= 0
2. 2*x1 == 0
3. -3*x0 + x1 >= -4
Enumerate ALL satisfying assignments in variable order [x0, x1].
The answer is a lexicographically sorted Python list of int lists, or UNSAT.

```

**Answer:**
```
[[0, 0], [1, 0]]
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider the directed graph:

digraph { 0->3; 1->4; 1->5; 2->3; 2->4; 2->5; 3->0; 3->2; 4->5; 5->1; 5->2 }

Find the lexicographically smallest shortest directed path from Node 3 to Node 1.
The answer is a Python list of nodes, or `None` if no path exists.
```

**Answer:**
```
[3, 2, 5, 1]
```

---

## [graph_isomorphism](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Consider two directed graphs described below.

Graph A:
0: 0->2 0->5; 1: 1->2 1->3; 2: 2->0 2->1; 3: 3->4; 4: 4->3 4->5; 5: 5->0 5->4

Graph B:
0: 0->2 0->5; 1: 1->3 1->4; 2: 2->0 2->1; 3: 3->4; 4: 4->3 4->5; 5: 5->0 5->2

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

digraph { 0->0; 1->2; 2->5; 3->4; 4->3; 5->1 }

Queries: [(2, 2)]
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

Node 0 has no outgoing links. Node 1 points to 0. Node 2 points to 4. Node 3 points to 0. Node 4 points to 0, 1. Node 5 points to 1.

In this scenario, a directed edge from U to V means V depends on U (so U is a prerequisite of V).
List all prerequisites of node 0 (recursively), making sure to order base prerequisites first.
Exclude the query node; prerequisites must precede dependents, with lexicographic tie-breaks.
The answer is a Python list of integers.
```

**Answer:**
```
[2, 3, 4, 5, 1]
```

---

## [regex_following](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
The answer is a 2-character string that fully matches the regular expression: (\d)m?
```

**Answer:**
```
6m
```

---

## [regex_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Positive: 'b', 'bb', 'bbb', 'bbbb', 'bbbbb'
Negative: 'acdc', 'adcc', 'ba', 'baaad', 'c', 'ca', 'd', 'ddcad'
The answer is the shortest regex matching all positives and no negatives. Use only literals from Σ={abcd}, concatenation, |, parentheses, and postfix *, +, ?. Break ties lexicographically.
```

**Answer:**
```
b+
```

---

## [regex_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
Text: Why three mother last film effort. Image some figure hair likely.
Regex: \b[A-Z][a-z]+\b
The answer is a JSON array of exact non-overlapping matches, left-to-right, including duplicates. The answer is [] if none.
```

**Answer:**
```
["Why","Image"]
```

---

## [regex_reasoning](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/regex.py)

**Prompt:**
```
A = bab?
B = (bab?)|(c(ac))
Is every string accepted by A also accepted by B?
The answer is Yes or No.
```

**Answer:**
```
Yes
```

---

## [parsing_derivation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
(GRAMMAR)
R0: S -> C
R1: C -> C 'total'
R2: C -> 'total'
R3: D -> B

(STRING)
total total total total total total

(QUESTION)
The answer is the rule labels used in the leftmost derivation of STRING, in order, separated by spaces.
```

**Answer:**
```
R0 R1 R1 R1 R1 R1 R2
```

---

## [continuation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/grammar.py)

**Prompt:**
```
List valid next tokens for this prefix. The answer is the valid tokens sorted alphabetically and separated by |, with STOP at the end if the prefix forms a complete string.
(GRAMMAR)
start -> seq
seq -> 
seq -> expr seq
expr -> '(' seq ')'
expr -> '[' seq ']'
expr -> '<' seq '>'
(PREFIX)
[ [ ]
```

**Answer:**
```
(|<|[|]
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
( [ ] < ) ) ( < > ) < >

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
< >>)<<
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
< < > > < ( )

(TEMPLATE)
> ___ > ___

(SUFFIX)
)

Fill in the 2 blanks (___) so that PREFIX + filled-TEMPLATE + SUFFIX is a grammatical sentence. Fixed tokens of TEMPLATE must remain in place.
The answer is the 4 tokens of the filled TEMPLATE, space-separated.
```

**Answer:**
```
> < > (
```

---

## [table_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/table_qa.py)

**Prompt:**
```
Execute this SQL query on the table named dataframe:

Table 1:
customer,rating
Lindsey Werner,3.4
Shawn Gallegos,2.7
Sheila Olson,1.8
Michael Schwartz,3.8
Andrew Black,2.5


SQL: SELECT COUNT(*) FROM dataframe WHERE CAST(customer AS VARCHAR) LIKE '%ichael Schwartz%'

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
Convert the following table from yaml to json.

- date: 2026-04-11
  qty: 451
- date: 2026-03-07
  qty: 162
- date: 2025-09-15
  qty: 594
- date: 2025-11-10
  qty: 269
- date: 2026-02-25
  qty: 920


The answer is the converted table.
```

**Answer:**
```
[
    {
        "date":"2026-04-11T00:00:00.000",
        "qty":451
    },
    {
        "date":"2026-03-07T00:00:00.000",
        "qty":162
    },
    {
        "date":"2025-09-15T00:00:00.000",
        "qty":594
    },
    {
        "date":"2025-11-10T00:00:00.000",
        "qty":269
    },
    {
        "date":"2026-02-25T00:00:00.000",
        "qty":920
    }
]
```

---

## [diff_prediction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_diff.py)

**Prompt:**
```
Below is the version history of a file.

Version e2a5e0e:
1    | These write democratic
2    | Support but own yes language
3    | Travel great field
4    | Executive letter change every happen hope
5    | Answer weight surface hit bank

Version 25d6020:
1    | These write democratic
2    | Support but own yes language
3    | Travel great field
4    | turn water describe herself very
5    | Executive letter change every happen hope
6    | determine character soon child which
7    | Answer weight surface hit bank

Generate the Unified Diff to transform version 25d6020 into version e2a5e0e.
The answer is the diff chunks only (no file headers), or empty if no changes.
```

**Answer:**
```
@@ -1,7 +1,5 @@
 These write democratic
 Support but own yes language
 Travel great field
-turn water describe herself very
 Executive letter change every happen hope
-determine character soon child which
 Answer weight surface hit bank
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(x: int) -> int:
    print(x)
    return x + 2
def f1(b: int, k: int) -> int:
    print(b)
    return k * b
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(-3)`
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
def f0(s: int) -> int:
    pass
    print(s)
    print(s)
    return s - 4
def f1(h: list) -> list:
    print(h)
    return [0, 1, 2]
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(-3)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
-7
```

---

