# 📖 Task Gallery

[`arithmetics`](#arithmetics) · [`math_word_problem`](#math_word_problem) · [`equation_system`](#equation_system) · [`tptp_consistency_repair`](#tptp_consistency_repair) · [`planar_geometry_relations`](#planar_geometry_relations) · [`rewrite_system`](#rewrite_system) · [`most_probable_evidence`](#most_probable_evidence) · [`most_probable_outcome`](#most_probable_outcome) · [`evidence_retrieval`](#evidence_retrieval) · [`multistep_nli`](#multistep_nli) · [`multistep_evidence_retrieval`](#multistep_evidence_retrieval) · [`multistep_abduction`](#multistep_abduction) · [`logic_qa`](#logic_qa) · [`sequential_induction`](#sequential_induction) · [`navigation`](#navigation) · [`coreference`](#coreference) · [`graph_pathfinding`](#graph_pathfinding) · [`graph_successors`](#graph_successors) · [`graph_dependencies`](#graph_dependencies) · [`locate_error`](#locate_error) · [`string_transduction`](#string_transduction) · [`code_runnability`](#code_runnability) · [`code_execution`](#code_execution) · [`code_input_deduction`](#code_input_deduction) · [`analogical_case_retrieval`](#analogical_case_retrieval)

---

## [arithmetics](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Evaluate 6 / -4.
The answer is a number.
```

**Answer:**
```
-1.5
```

---

## [math_word_problem](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/arithmetics.py)

**Prompt:**
```
Sana has 9 more tokens than Omar. Zara has half as many tokens as Omar. Omar has 12 tokens. How many tokens does Sana have? Answer with s a number.
```

**Answer:**
```
21
```

---

## [equation_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/equation_system.py)

**Prompt:**
```
Solve the following system of equations for the variable 'X1'.

System:
  -X1 + X2 + 25 = 0

The answer is the value of X1, or 'No solution' / 'Multiple solutions'.
```

**Answer:**
```
Multiple solutions
```

---

## [tptp_consistency_repair](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_tptp.py)

**Prompt:**
```
The clauses below are unsatisfiable.
Find all individual clauses whose deletion makes them satisfiable.
The answer is the clause numbers, ordered, space-separated.
Clauses:
1. (subset(X1,X2)|~member(member_of_1_not_of_2(X1,X2),X2))
2. (~subset(X1,X1))
3. (subset(X1,X2)|member(member_of_1_not_of_2(X1,X2),X1))
```

**Answer:**
```
1 2 3
```

---

## [planar_geometry_relations](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/math_geometry.py)

**Prompt:**
```
Given points: A=(-3, 5); B=(-1, 0); J=(-5/2, 0); S=(-1, 5); T=(-1/2, 1); U=(0, 2); X=(-4, -5).
Definitions: J is the midpoint of S and X. T is the midpoint of B and U.
Question: Where is point T relative to directed line SA?
Answer is one of: left, right, on.
```

**Answer:**
```
left
```

---

## [rewrite_system](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/binding.py)

**Prompt:**
```
Normalize by the ordered rewrite rules. At each step, use the first applicable rule in the listed order, searching outermost-first and left-to-right.

Rules:
- if(false,X,Y) -> Y
- fst(pair(X,Y)) -> X
- id(X) -> X
- snd(pair(X,Y)) -> Y
- const(X,Y) -> X
- if(true,X,Y) -> X

Term: snd(pair(unit,if(false,c,if(false,false,true))))

The answer is the normal form.
```

**Answer:**
```
true
```

---

## [most_probable_evidence](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
Factor a is independently true with probability 0.1.
Factor b is independently true with probability 0.7.
The observation holds exactly when (factor a or factor b).
We observe it.
Which hidden fact values form the most probable complete explanation?

Hidden fact values:
0. a
1. not a
2. b
3. not b

Answer with space-separated indexes.
```

**Answer:**
```
1 2
```

---

## [most_probable_outcome](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/probabilistic_reasoning.py)

**Prompt:**
```
A deck contains 6 orange cards and 8 purple cards.
Two cards are drawn without replacing the first card.
Which statement is more likely?
A: the first selected card is orange.
B: the first selected card is purple.

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
[0] Catherine is the only person in the room.
[1] all old people in the room are quiet
[2] Carolyn is mike tagged
[3] all quiet people in the room are quiet
[4] no quiet person in the room is quiet
[5] not everyone in the room who is delta tagged is juliet tagged
Hypothesis:
Catherine is juliet tagged

Which statements in the premise contradict the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
0 5
```

---

## [multistep_nli](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
bruno is careful.
bruno is approved.
bruno helps alice.
david is approved.
bruno is verified.
clara trusts alice.
Every careful entity that is also approved is trained.
Whenever x is trained, x is verified.
If a person is trained and trusted, then that person is careful.
Anyone trusts to someone who is helps to a third person is advises to that third person.
For all x, if x is trusted, then x is active.
Whenever x advises y and y trusts z, x helps z.
People reached by helps from a verified person are careful.

Hypothesis:
alice helps david.

Classify the hypothesis as entailment, contradiction, or neutral. The answer is one label.
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
[0] alice is active.
[1] alice is trusted.
[2] alice trusts clara.
[3] alice is not careful.
[4] david is approved.
[5] bruno trusts david.
[6] Anyone who is active and trusted is trained.
[7] Being trained implies being verified.
[8] If a person is trusted and approved, then that person is verified.
[9] If a person is trained and approved, then that person is not verified.
[10] A person is trained when they advises someone active.
[11] From x is verified and x is careful, it follows that x is active.
[12] Every careful entity is trusted.

Hypothesis:
alice is not verified.

Which premise statements are necessary to contradict the hypothesis, meaning removing any one of them breaks that result?
Answer with space-separated indexes.
```

**Answer:**
```
0 1 6 7
```

---

## [multistep_abduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
[0] alice is trained.
[1] david is careful.
[2] Every trained entity is verified.
[3] Whenever x is verified, x is approved.

Hypothesis:
clara is approved.

Candidate Facts:
[0] alice advises clara.
[1] clara is not trained.
[2] clara is careful.
[3] david does not trusts bruno.
[4] clara is trained.
[5] alice trusts bruno.

Which candidate facts, if added to the premise, make the premise entail the hypothesis?
Answer with space-separated indexes.
```

**Answer:**
```
4
```

---

## [logic_qa](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/logic_depth.py)

**Prompt:**
```
Premise:
alice trusts david.
david is active.
alice helps david.
alice is trusted.
alice is approved.
clara advises bruno.
clara trusts alice.
Anyone who trusts someone active is careful.
Every careful entity is approved.
Anyone whom a careful person helps is trained.
Anyone trusts to someone who is helps to a third person is advises to that third person.
From x trusts y and y advises z, it follows that x helps z.
If a careful person is helps to someone, then that other person is trusted.

Question:
How many entities are trusted?

Answer with one integer.
```

**Answer:**
```
2
```

---

## [sequential_induction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/sequential_induction.py)

**Prompt:**
```
Infer U[n]. Max recurrence degree: 0. Ops: +, -, *, **.
Use n.
Sequence: [0, 2, 6, 12, 20, 30, 42, 56]
Initial terms: []
The answer is the RHS only.
```

**Answer:**
```
n + n**2
```

---

## [navigation](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/navigation.py)

**Prompt:**
```
Grid [0,4]x[0,4], N=+y, E=+x.
Initial Facts:
- A starts at (2, 2).
- B is right of A.
- A is left of C.
- C is below A.
- B starts at (4, 3).
- A is below B.
- B is in the same column as C.
- C is below B.

Steps:
1. C and A swap positions.

What is the final Manhattan distance between B and C? The answer is an integer.
```

**Answer:**
```
3
```

---

## [coreference](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/coreference.py)

**Prompt:**
```
(1) An old tall scientist named Anna avoided a stern young teacher named Luke.
(2) She thanked Luke.
(3) Anna helped him.
(4) An old short teacher named Lena called the scientist.
(5) An old tall teacher named Hugo met Lena.
(6) The scientist met Lena.
(7) Anna watched a short young farmer named Noah.

In sentence 3, what does the object expression 'him' refer to?
The answer is the person's name.
```

**Answer:**
```
Luke
```

---

## [graph_pathfinding](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
Find the lexicographically smallest shortest directed path from node 3 to node 5.
Answer with space-separated nodes, or `None` if no path exists.

Graph:
0: 0->2 0->3; 1: 1->2; 2: 2->0 2->1 2->3; 3: 3->0 3->2 3->5; 4: 4->5; 5: 5->3 5->4
```

**Answer:**
```
3 5
```

---

## [graph_successors](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
For each query (x, k), give the k-th successor of x by following directed edges k times.
Answer with space-separated integers in query order.

Graph:
0: 0->3; 1: 1->5; 2: 2->1; 3: 3->2; 4: 4->0; 5: 5->4

Queries:
[(1, 1)]
```

**Answer:**
```
5
```

---

## [graph_dependencies](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/graph_operations.py)

**Prompt:**
```
List all ancestors of node 2.
Order them so predecessors come before successors, with lexicographic tie-breaks.
Answer with space-separated indexes.

Graph:
Nodes [0, 1, 2, 3, 4, 5] and directed edges: (0, 2), (0, 5), (1, 2), (3, 2), (4, 2).
```

**Answer:**
```
0 1 3 4
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
expr -> '⟨' seq '⟩'
expr -> '⟦' seq '⟧'
expr -> '⟪' seq '⟫'

(STRING)
⟧ ⟪ ⟦ ⟧ ⟪ ⟫ ⟫

The answer is the shortest contiguous span from STRING that ends at the first invalid token and occurs only once in STRING.
Mark the invalid token as >>token<<.
If the token alone is enough, answer just >>token<<.
If STRING is fully grammatical, answer OK.
If all shown tokens are valid but more are needed, answer INCOMPLETE.
One line only.
```

**Answer:**
```
>>⟧<<
```

---

## [string_transduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/string_transduction.py)

**Prompt:**
```
String: abdceeac
Operations:
- sort ascending
- rotate left by 3
Answer with the final string.
```

**Answer:**
```
ccdeeaab
```

---

## [code_runnability](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Predict whether this Python call runs successfully or raises an exception.
```python
def f0(w: int) -> int:
    w = w + f0(w)
    print(w)
    return w + 8
def f1(a: int, w: list) -> list:
    while a >= -3:
        b = 7 + 5
        a = a - 2
    return w
def endpoint(x0: int) -> int:
    return f0(x0)

```
Call: `endpoint(2)`
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
def f0(e: str, d: int) -> str:
    d *= d
    d = f"out={d}"
    print(e)
    return d
def f1(b: str) -> int:
    a = 4 * 1
    return a
def endpoint(x0: str, x1: int) -> str:
    return f0(x0, x1)

```
Call: `endpoint('x', -3)`
The answer is the exact Python `repr` of the returned value.
````

**Answer:**
```
'out=9'
```

---

## [code_input_deduction](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/code_execution.py)

**Prompt:**
````
Find the smallest integer x in [-6, 9] such that `endpoint(x) == target`.
Answer with the integer.

```python
def f0(n: int) -> int:
    pass
    return n * 4


def endpoint(x):
    return f0(x) % 5

```

Target: 2
````

**Answer:**
```
-2
```

---

## [analogical_case_retrieval](https://github.com/sileod/reasoning-core/blob/main/reasoning_core/tasks/formal_analogies.py)

**Prompt:**
```
Cases show facts that imply one new fact.
Object names and link names may be consistently renamed, and each link direction may be consistently reversed.

M0
a is alpha-linked to b.
c is alpha-linked to b.
c is beta-linked to a.
b is gamma-linked to a.
Implies: a is gamma-linked to c.

M1
e is alpha-linked to a.
c is beta-linked to d.
d is beta-linked to a.
e is beta-linked to d.
Implies: b is gamma-linked to e.

M2
b is alpha-linked to c.
c is alpha-linked to a.
a is beta-linked to b.
c is gamma-linked to b.
Implies: b is beta-linked to c.

M3
b is alpha-linked to a.
a is beta-linked to b.
a is gamma-linked to c.
c is gamma-linked to b.
Implies: b is gamma-linked to a.

Query
v is delta-linked to x.
v is delta-linked to y.
v is delta-linked to z.
y is delta-linked to z.
u is epsilon-linked to v.
x is epsilon-linked to u.
z is epsilon-linked to v.
u is gamma-linked to x.
Implies:
```

**Answer:**
```
x is delta-linked to u.
```

---

