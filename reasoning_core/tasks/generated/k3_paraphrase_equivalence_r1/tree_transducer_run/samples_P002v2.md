# Samples for tree_transducer_run (P002v2)

## Level 0

### Example 1

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label c children ['0']
  0: label a children ['0-0', '0-1']
  0-0: label l (leaf)
  0-1: label l children ['0-1-0']
  0-1-0: label b (leaf)
Rules (per 'state/label'):
  p/a: leaf alpha
  p/b: node beta with children: child 1 in s (in that order)
  p/c: node gamma with children: child 0 in q (in that order)
  p/d: node theta with children: child 0 in s (in that order)
  q/a: leaf delta
  q/b: leaf alpha
  q/c: node rho with children: child 1 in p (in that order)
  q/d: node alpha with children: child 0 in q, child 1 in r (in that order)
  r/a: node zeta with children: child 1 in q, child 0 in r (in that order)
  r/b: node omicron with children: child 0 in p, child 1 in q (in that order)
  r/c: node theta with children: child 0 in q, child 1 in r (in that order)
  r/d: node nu with children: child 1 in p (in that order)
  s/a: node gamma with children: child 0 in r, child 1 in p (in that order)
  s/b: node kappa with children: child 0 in s (in that order)
  s/c: leaf lambda
  s/d: node theta with children: child 0 in q (in that order)
Start state: s
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`lambda`

### Example 2

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label a children ['0']
  0: label c children ['0-0']
  0-0: label a children ['0-0-0', '0-0-1']
  0-0-0: label i (leaf)
  0-0-1: label f (leaf)
Rules (per 'state/label'):
  p/a: node zeta with children: child 1 in r, child 0 in p (in that order)
  p/b: node eta with children: child 0 in p (in that order)
  p/c: node rho with children: child 0 in s (in that order)
  p/d: node iota with children: child 1 in s (in that order)
  q/a: node mu with children: child 1 in q (in that order)
  q/b: leaf iota
  q/c: leaf nu
  q/d: leaf xi
  r/a: node rho with children: child 1 in q (in that order)
  r/b: leaf gamma
  r/c: node eta with children: child 0 in r (in that order)
  r/d: leaf kappa
  s/a: node lambda with children: child 0 in r, child 1 in q (in that order)
  s/b: node rho with children: child 1 in r, child 0 in r (in that order)
  s/c: node omicron with children: child 1 in p, child 0 in q (in that order)
  s/d: node gamma with children: child 0 in r, child 1 in p (in that order)
Start state: p
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`0-0-0`

## Level 2

### Example 1

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label d children ['0', '1']
  0: label f (leaf)
  1: label j children ['1-0', '1-1', '1-2']
  1-0: label b (leaf)
  1-1: label g (leaf)
  1-2: label e children ['1-2-0', '1-2-1']
  1-2-0: label e (leaf)
  1-2-1: label h children ['1-2-1-0', '1-2-1-1']
  1-2-1-0: label g children ['1-2-1-0-0']
  1-2-1-1: label i children ['1-2-1-1-0', '1-2-1-1-1']
  1-2-1-0-0: label f (leaf)
  1-2-1-1-0: label j (leaf)
  1-2-1-1-1: label d (leaf)
Rules (per 'state/label'):
  p/a: leaf rho
  p/b: leaf epsilon
  p/c: leaf gamma
  p/d: leaf omicron
  p/e: leaf iota
  p/f: leaf gamma
  q/a: none
  q/b: leaf kappa
  q/c: leaf omicron
  q/d: node xi with children: child 0 in r, child 1 in s, child 2 in q (in that order)
  q/e: node beta with children: child 1 in p (in that order)
  q/f: node delta with children: child 0 in p, child 1 in s, child 2 in u (in that order)
  r/a: node nu with children: child 2 in s, child 0 in r, child 1 in q (in that order)
  r/b: node xi with children: child 1 in q (in that order)
  r/c: node delta with children: child 2 in t, child 1 in t (in that order)
  r/d: node kappa with children: child 1 in s, child 2 in p, child 0 in s (in that order)
  r/e: leaf zeta
  r/f: node gamma with children: child 0 in p (in that order)
  s/a: node nu with children: child 2 in q (in that order)
  s/b: node mu with children: child 1 in s, child 0 in p (in that order)
  s/c: node beta with children: child 0 in q (in that order)
  s/d: node lambda with children: child 2 in r, child 1 in s, child 0 in r (in that order)
  s/e: leaf alpha
  s/f: node gamma with children: child 0 in t, child 2 in u (in that order)
  t/a: none
  t/b: node beta with children: child 2 in s, child 0 in t (in that order)
  t/c: leaf xi
  t/d: node mu with children: child 0 in r (in that order)
  t/e: node xi with children: child 0 in u (in that order)
  t/f: node rho with children: child 2 in u, child 0 in s (in that order)
  u/a: node epsilon with children: child 0 in p, child 1 in r, child 2 in t (in that order)
  u/b: leaf delta
  u/c: none
  u/d: node epsilon with children: child 1 in p (in that order)
  u/e: leaf epsilon
  u/f: node epsilon with children: child 0 in u, child 1 in u (in that order)
Start state: r
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`1`

### Example 2

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label e children ['0', '1']
  0: label h (leaf)
  1: label g children ['1-0']
  1-0: label k children ['1-0-0']
  1-0-0: label h children ['1-0-0-0']
  1-0-0-0: label e children ['1-0-0-0-0', '1-0-0-0-1']
  1-0-0-0-0: label c (leaf)
  1-0-0-0-1: label l (leaf)
Rules (per 'state/label'):
  p/a: node theta with children: child 1 in t, child 0 in r (in that order)
  p/b: node kappa with children: child 1 in p (in that order)
  p/c: node epsilon with children: child 1 in r (in that order)
  p/d: node theta with children: child 1 in q (in that order)
  p/e: node xi with children: child 1 in u (in that order)
  p/f: leaf alpha
  q/a: node mu with children: child 1 in u (in that order)
  q/b: node kappa with children: child 0 in t (in that order)
  q/c: none
  q/d: node zeta with children: child 1 in u (in that order)
  q/e: leaf iota
  q/f: leaf theta
  r/a: none
  r/b: none
  r/c: none
  r/d: node delta with children: child 1 in q (in that order)
  r/e: node zeta with children: child 1 in t (in that order)
  r/f: node theta with children: child 1 in r, child 0 in s (in that order)
  s/a: leaf delta
  s/b: node omicron with children: child 1 in t (in that order)
  s/c: node delta with children: child 1 in t (in that order)
  s/d: leaf gamma
  s/e: node omicron with children: child 0 in s (in that order)
  s/f: none
  t/a: leaf beta
  t/b: leaf alpha
  t/c: leaf gamma
  t/d: node delta with children: child 0 in s, child 1 in p (in that order)
  t/e: leaf epsilon
  t/f: leaf alpha
  u/a: none
  u/b: leaf iota
  u/c: leaf mu
  u/d: node eta with children: child 0 in r, child 1 in u (in that order)
  u/e: node kappa with children: child 0 in s, child 1 in q (in that order)
  u/f: node nu with children: child 0 in r (in that order)
Start state: t
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`epsilon`

## Level 5

### Example 1

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label a children ['0', '1']
  0: label i children ['0-0', '0-1']
  1: label b (leaf)
  0-0: label b children ['0-0-0']
  0-1: label h (leaf)
  0-0-0: label a children ['0-0-0-0']
  0-0-0-0: label g children ['0-0-0-0-0', '0-0-0-0-1']
  0-0-0-0-0: label d children ['0-0-0-0-0-0']
  0-0-0-0-1: label l (leaf)
  0-0-0-0-0-0: label k children ['0-0-0-0-0-0-0', '0-0-0-0-0-0-1']
  0-0-0-0-0-0-0: label a (leaf)
  0-0-0-0-0-0-1: label c children ['0-0-0-0-0-0-1-0', '0-0-0-0-0-0-1-1', '0-0-0-0-0-0-1-2']
  0-0-0-0-0-0-1-0: label g (leaf)
  0-0-0-0-0-0-1-1: label d (leaf)
  0-0-0-0-0-0-1-2: label d (leaf)
Rules (per 'state/label'):
  p/a: node rho with children: child 0 in r, child 2 in u (in that order)
  p/b: node theta with children: child 2 in t, child 1 in r, child 0 in u (in that order)
  p/c: none
  p/d: leaf kappa
  p/e: leaf epsilon
  p/f: node rho with children: child 0 in r, child 1 in s (in that order)
  p/g: leaf theta
  q/a: leaf eta
  q/b: leaf theta
  q/c: node rho with children: child 0 in u (in that order)
  q/d: node lambda with children: child 2 in p, child 0 in r, child 1 in p (in that order)
  q/e: node mu with children: child 2 in p, child 1 in r (in that order)
  q/f: leaf epsilon
  q/g: leaf beta
  r/a: node gamma with children: child 2 in p, child 1 in t, child 0 in u (in that order)
  r/b: leaf rho
  r/c: node alpha with children: child 1 in q (in that order)
  r/d: none
  r/e: node kappa with children: child 1 in p (in that order)
  r/f: leaf delta
  r/g: leaf rho
  s/a: node iota with children: child 2 in r (in that order)
  s/b: node rho with children: child 2 in r (in that order)
  s/c: node iota with children: child 1 in r, child 0 in p (in that order)
  s/d: node zeta with children: child 2 in s, child 0 in p, child 1 in s (in that order)
  s/e: node theta with children: child 1 in t (in that order)
  s/f: node omicron with children: child 2 in r, child 0 in u, child 1 in t (in that order)
  s/g: node kappa with children: child 0 in r, child 1 in r, child 2 in q (in that order)
  t/a: node omicron with children: child 1 in u, child 2 in q (in that order)
  t/b: leaf alpha
  t/c: node gamma with children: child 2 in t (in that order)
  t/d: node nu with children: child 1 in t, child 0 in s (in that order)
  t/e: leaf theta
  t/f: node kappa with children: child 0 in s, child 2 in r (in that order)
  t/g: node alpha with children: child 0 in t, child 2 in q, child 1 in p (in that order)
  u/a: leaf iota
  u/b: node omicron with children: child 2 in r, child 1 in s, child 0 in r (in that order)
  u/c: leaf omicron
  u/d: node alpha with children: child 0 in r (in that order)
  u/e: node xi with children: child 0 in s (in that order)
  u/f: none
  u/g: node rho with children: child 2 in u (in that order)
Start state: s
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`iota()`

### Example 2

**Prompt:**

```
A top-down (root-to-leaves) tree transducer runs over an input tree. Each node has a label and an ordered list of children indexed 0, 1, 2, ... The transducer assigns a state to each visited node and applies the matching (state, label) rule.
  - 'leaf WORD': emit the leaf word WORD and stop at this node;
  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' where each listed child (by index) is visited under its STATE, in the listed order (a child may be dropped or reordered; only listed children are visited);
  - 'none': no rule applies, the run is stuck (fails) at this node.
Visited children are emitted in pre-order from the root.
Input tree ('*' is the root; each non-leaf line shows label and children indices):
  *: label f children ['0', '1']
  0: label a (leaf)
  1: label j children ['1-0', '1-1']
  1-0: label a (leaf)
  1-1: label g children ['1-1-0']
  1-1-0: label c children ['1-1-0-0', '1-1-0-1']
  1-1-0-0: label i children ['1-1-0-0-0']
  1-1-0-1: label f children ['1-1-0-1-0', '1-1-0-1-1']
  1-1-0-0-0: label g (leaf)
  1-1-0-1-0: label l children ['1-1-0-1-0-0']
  1-1-0-1-1: label l children ['1-1-0-1-1-0']
  1-1-0-1-0-0: label d (leaf)
  1-1-0-1-1-0: label a (leaf)
Rules (per 'state/label'):
  p/a: node lambda with children: child 0 in u (in that order)
  p/b: leaf epsilon
  p/c: node delta with children: child 0 in s, child 1 in t (in that order)
  p/d: node alpha with children: child 1 in p, child 0 in p (in that order)
  p/e: leaf omicron
  p/f: leaf lambda
  p/g: leaf theta
  q/a: node rho with children: child 1 in r (in that order)
  q/b: leaf kappa
  q/c: leaf nu
  q/d: leaf alpha
  q/e: leaf epsilon
  q/f: none
  q/g: node theta with children: child 0 in q (in that order)
  r/a: node theta with children: child 0 in t, child 1 in r (in that order)
  r/b: node rho with children: child 1 in q (in that order)
  r/c: node iota with children: child 1 in q (in that order)
  r/d: leaf theta
  r/e: node beta with children: child 1 in s, child 0 in q (in that order)
  r/f: node nu with children: child 1 in q, child 0 in s (in that order)
  r/g: node theta with children: child 1 in q, child 0 in t (in that order)
  s/a: node rho with children: child 0 in u (in that order)
  s/b: node alpha with children: child 0 in r, child 1 in r (in that order)
  s/c: leaf zeta
  s/d: node delta with children: child 0 in r, child 1 in q (in that order)
  s/e: node alpha with children: child 1 in p (in that order)
  s/f: leaf zeta
  s/g: node epsilon with children: child 0 in u (in that order)
  t/a: node beta with children: child 1 in s (in that order)
  t/b: node gamma with children: child 0 in u (in that order)
  t/c: leaf rho
  t/d: node omicron with children: child 1 in q (in that order)
  t/e: leaf alpha
  t/f: leaf theta
  t/g: node epsilon with children: child 0 in t, child 1 in u (in that order)
  u/a: node lambda with children: child 0 in u (in that order)
  u/b: node lambda with children: child 1 in t (in that order)
  u/c: leaf zeta
  u/d: node delta with children: child 1 in q, child 0 in q (in that order)
  u/e: leaf gamma
  u/f: node alpha with children: child 1 in p (in that order)
  u/g: node eta with children: child 1 in t (in that order)
Start state: p
Run the transducer. If it completes, answer the serialized output tree in parenthesized prefix notation (a leaf is its word; a node with template WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line.
If the run gets stuck, answer the path from the root to the FIRST stuck node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root itself is never the first stuck node.
```

**Answer:**

`lambda`
