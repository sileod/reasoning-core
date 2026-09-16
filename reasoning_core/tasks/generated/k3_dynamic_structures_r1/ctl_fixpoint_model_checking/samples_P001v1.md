# samples_P001v1

## Level 0

### Example 1

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> d
  b -> a
  c -> c
  d -> a c
Each state carries an atomic proposition (labeling):
  a : q
  b : p
  c : q
  d : q
Formula: EG q
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
acd
```

### Example 2

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> b
  b -> d
  c -> a
  d -> d c
Each state carries an atomic proposition (labeling):
  a : p
  b : p
  c : q
  d : q
Formula: AF p
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
abc
```

## Level 2

### Example 1

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> a d
  b -> a
  c -> a
  d -> f
  e -> c
  f -> c a
Each state carries an atomic proposition (labeling):
  a : p
  b : q
  c : q
  d : p
  e : p
  f : q
Formula: EX AU q q
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
def
```

### Example 2

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> a e
  b -> a b
  c -> a
  d -> f c
  e -> a c
  f -> c a
Each state carries an atomic proposition (labeling):
  a : p
  b : q
  c : p
  d : p
  e : q
  f : p
Formula: EU q EG q
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
b
```

## Level 5

### Example 1

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> g f h
  b -> h b
  c -> b e
  d -> b
  e -> g d a
  f -> d
  g -> d g
  h -> e i h
  i -> g a
Each state carries an atomic proposition (labeling):
  a : q
  b : q
  c : q
  d : q
  e : q
  f : p
  g : p
  h : q
  i : p
Formula: q
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
abcdeh
```

### Example 2

Prompt:

```
Consider a Kripke structure whose states are the letters a, b, ... with transition relation T:
  a -> e c
  b -> g d i
  c -> h d
  d -> e
  e -> g h c
  f -> g f
  g -> i
  h -> f d
  i -> g
Each state carries an atomic proposition (labeling):
  a : p
  b : p
  c : q
  d : q
  e : q
  f : q
  g : q
  h : q
  i : q
Formula: q
Find the set of states satisfying the CTL formula by fixpoint iteration (EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, EU/AU until).
Answer: the satisfying states as a sorted concatenation of single lowercase state letters (e.g. 'abde'); the empty set is 'emptyset'.
```

Answer:

```
cdefghi
```

