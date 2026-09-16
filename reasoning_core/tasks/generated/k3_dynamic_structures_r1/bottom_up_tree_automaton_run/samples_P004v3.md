# samples_P004v3


## Level 0

### Example 1

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s0 s1 s1)

Leaf symbols map to sets of states:
  s0 -> {s0 s1}
  s1 -> {s0 s1}
  s2 -> {s0 s1}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0 s0} -> {s1}
  s0 with children {s0 s1} -> {s0 s1}
  s0 with children {s1 s1} -> {s0}
  s1 with children {s0} -> {s0 s1}
  s1 with children {s0 s0} -> {s0}
  s1 with children {s0 s1} -> {s0 s1}
  s1 with children {s1} -> {s0}
  s1 with children {s1 s1} -> {s1}
  s2 with children {s0} -> {s0}
  s2 with children {s0 s0} -> {s0 s1}
  s2 with children {s0 s1} -> {s0 s1}
  s2 with children {s1} -> {s1}
  s2 with children {s1 s1} -> {s1}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{s0 s1}|yes
```

### Example 2

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s2 s1)

Leaf symbols map to sets of states:
  s0 -> {s0}
  s1 -> {s0 s1}
  s2 -> {s0}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0} -> {s1}
  s0 with children {s0 s0} -> {s1}
  s0 with children {s0 s1} -> {s0 s1}
  s0 with children {s1} -> {s0 s1}
  s0 with children {s1 s1} -> {s1}
  s1 with children {s0} -> {s0 s1}
  s1 with children {s0 s0} -> {s0}
  s1 with children {s0 s1} -> {s0 s1}
  s1 with children {s1} -> {s1}
  s1 with children {s1 s1} -> {s0 s1}
  s2 with children {s0} -> {s1}
  s2 with children {s1} -> {s0 s1}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{s0 s1}|yes
```


## Level 2

### Example 1

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s0 (s1 (s2 (s3 s3 s3))) (s2 s1 s1))

Leaf symbols map to sets of states:
  s0 -> {s0}
  s1 -> {s0}
  s2 -> {s0 s1}
  s3 -> {s1}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0 s0} -> {s0}
  s0 with children {s0 s1} -> {s0 s1}
  s1 with children {s0} -> {s0}
  s1 with children {s0 s0} -> {s0 s1}
  s1 with children {s0 s1} -> {s0}
  s1 with children {s1} -> {s0}
  s1 with children {s1 s1} -> {s0}
  s2 with children {s0} -> {s0}
  s2 with children {s0 s0} -> {s0 s1}
  s2 with children {s0 s1} -> {s1}
  s2 with children {s1} -> {s0 s1}
  s2 with children {s1 s1} -> {s0}
  s3 with children {s0} -> {s0}
  s3 with children {s0 s0} -> {s0}
  s3 with children {s0 s1} -> {s0}
  s3 with children {s1} -> {s0 s1}
  s3 with children {s1 s1} -> {s0}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{s0 s1}|yes
```

### Example 2

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s1 s3 (s3 (s2 s0 s0) s0))

Leaf symbols map to sets of states:
  s0 -> {s1}
  s1 -> {s0}
  s2 -> {s0 s1}
  s3 -> {s0}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0} -> {s0 s1}
  s0 with children {s0 s0} -> {s1}
  s0 with children {s0 s1} -> {s0}
  s0 with children {s1} -> {s0}
  s0 with children {s1 s1} -> {s0}
  s2 with children {s0} -> {s0 s1}
  s2 with children {s0 s0} -> {s0}
  s2 with children {s0 s1} -> {s0 s1}
  s2 with children {s1} -> {s0}
  s2 with children {s1 s1} -> {s1}
  s3 with children {s0} -> {s1}
  s3 with children {s0 s0} -> {s0}
  s3 with children {s0 s1} -> {s0 s1}
  s3 with children {s1} -> {s0 s1}
  s3 with children {s1 s1} -> {s0}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{}|no
```


## Level 5

### Example 1

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s0 (s1 (s2 (s3 s4)) (s2 s2)) (s1 (s4 (s4 s3)) (s4 (s2 s3))))

Leaf symbols map to sets of states:
  s0 -> {s1 s2}
  s1 -> {s0 s2}
  s2 -> {s0}
  s3 -> {s0 s2}
  s4 -> {s2}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0 s1} -> {s0 s1 s2}
  s0 with children {s0 s2} -> {s0}
  s0 with children {s1 s1} -> {s1 s2}
  s0 with children {s1 s2} -> {s0 s2}
  s0 with children {s2 s2} -> {s1}
  s1 with children {s0} -> {s0 s1 s2}
  s1 with children {s0 s0} -> {s0 s1 s2}
  s1 with children {s0 s1} -> {s1 s2}
  s1 with children {s0 s2} -> {s0}
  s1 with children {s1} -> {s2}
  s1 with children {s1 s1} -> {s2}
  s1 with children {s1 s2} -> {s2}
  s1 with children {s2} -> {s0 s1 s2}
  s1 with children {s2 s2} -> {s1}
  s2 with children {s0} -> {s1}
  s2 with children {s0 s0} -> {s0 s2}
  s2 with children {s0 s1} -> {s0 s2}
  s2 with children {s0 s2} -> {s0 s2}
  s2 with children {s1} -> {s0 s2}
  s2 with children {s1 s1} -> {s2}
  s2 with children {s1 s2} -> {s1}
  s2 with children {s2} -> {s0 s2}
  s2 with children {s2 s2} -> {s0}
  s3 with children {s0} -> {s0 s1}
  s3 with children {s0 s0} -> {s0 s1}
  s3 with children {s0 s1} -> {s0 s1 s2}
  s3 with children {s0 s2} -> {s0 s1 s2}
  s3 with children {s1} -> {s0 s1 s2}
  s3 with children {s1 s1} -> {s0 s1 s2}
  s3 with children {s1 s2} -> {s0 s1}
  s3 with children {s2} -> {s1 s2}
  s3 with children {s2 s2} -> {s0 s1 s2}
  s4 with children {s0} -> {s0 s1 s2}
  s4 with children {s0 s0} -> {s1}
  s4 with children {s0 s1} -> {s0 s1}
  s4 with children {s0 s2} -> {s1 s2}
  s4 with children {s1} -> {s0 s1}
  s4 with children {s1 s1} -> {s1 s2}
  s4 with children {s1 s2} -> {s2}
  s4 with children {s2} -> {s0 s1 s2}
  s4 with children {s2 s2} -> {s0 s1 s2}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{s0 s1 s2}|yes
```

### Example 2

Prompt:

```
A nondeterministic bottom-up tree automaton is defined over an ordered tree.

Tree (symbols are the node labels; children of an internal node follow it in parentheses, leaves have none):
(s3 (s2 s0))

Leaf symbols map to sets of states:
  s0 -> {s0 s1 s2}
  s1 -> {s2}
  s2 -> {s0 s2}
  s3 -> {s1 s2}
  s4 -> {s0 s1}

Transition rules: parent symbol with a child-state tuple gives the result state set
  s0 with children {s0} -> {s1 s2}
  s0 with children {s0 s0} -> {s0 s1 s2}
  s0 with children {s0 s1} -> {s0 s1 s2}
  s0 with children {s0 s2} -> {s0 s1 s2}
  s0 with children {s1} -> {s0 s1 s2}
  s0 with children {s1 s1} -> {s0 s1}
  s0 with children {s1 s2} -> {s1}
  s0 with children {s2} -> {s1}
  s0 with children {s2 s2} -> {s0 s1 s2}
  s1 with children {s0} -> {s0 s1 s2}
  s1 with children {s0 s0} -> {s2}
  s1 with children {s0 s1} -> {s0}
  s1 with children {s0 s2} -> {s0 s1 s2}
  s1 with children {s1} -> {s1}
  s1 with children {s1 s1} -> {s0 s1 s2}
  s1 with children {s1 s2} -> {s0 s1 s2}
  s1 with children {s2} -> {s0 s1}
  s1 with children {s2 s2} -> {s0 s1 s2}
  s2 with children {s0} -> {s0 s1 s2}
  s2 with children {s0 s0} -> {s1}
  s2 with children {s0 s1} -> {s1 s2}
  s2 with children {s0 s2} -> {s1 s2}
  s2 with children {s1} -> {s0 s1 s2}
  s2 with children {s1 s1} -> {s0 s1 s2}
  s2 with children {s1 s2} -> {s0}
  s2 with children {s2} -> {s0}
  s2 with children {s2 s2} -> {s0 s1 s2}
  s3 with children {s0} -> {s1}
  s3 with children {s1} -> {s0 s2}
  s3 with children {s2} -> {s2}
  s4 with children {s0} -> {s1}
  s4 with children {s0 s0} -> {s0}
  s4 with children {s0 s1} -> {s0 s1 s2}
  s4 with children {s0 s2} -> {s0}
  s4 with children {s1} -> {s0}
  s4 with children {s1 s1} -> {s0 s1 s2}
  s4 with children {s1 s2} -> {s0 s1 s2}
  s4 with children {s2} -> {s1}
  s4 with children {s2 s2} -> {s0 s2}

Compute the set of states reachable at the root, combining child-state sets bottom-up: a child reaches whatever its sub-automaton computes, and a parent with children reaching states S1..Sk reaches every union over a compatible rule. It accepts iff its root state set is non-empty.

Answer as one line: the root state set in braces (states written as s<n>, space-separated, in increasing order; {} if empty) followed by |yes or |no. Example: {s0 s2}|yes
```

Answer:

```
{s0 s1 s2}|yes
```
