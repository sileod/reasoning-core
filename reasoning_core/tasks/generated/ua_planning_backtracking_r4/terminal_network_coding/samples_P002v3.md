# Level 0

## Example 1 (level 0)

**Prompt:**

```
A directed communication network over GF(2) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 1, 0), ('R', 1, 1), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('R', 0, 0)->('R', 1, 0), ('R', 0, 0)->('R', 1, 1), ('R', 0, 1)->('R', 1, 0), ('R', 0, 1)->('R', 1, 1), ('R', 1, 0)->('T',), ('R', 1, 1)->('T',)
The following edges are erased (unavailable): ('R', 0, 0)->('R', 1, 0), ('R', 0, 0)->('R', 1, 1), ('R', 0, 1)->('R', 1, 0), ('R', 0, 1)->('R', 1, 1), ('R', 1, 0)->('T',), ('R', 1, 1)->('T',), ('S',)->('R', 0, 0), ('S',)->('R', 0, 1).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`no`

---

## Example 2 (level 0)

**Prompt:**

```
A directed communication network over GF(2) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 0, 2), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2), ('R', 0, 0)->('T',), ('R', 0, 1)->('T',), ('R', 0, 2)->('T',)
The following edges are erased (unavailable): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`no`

---

# Level 2

## Example 1 (level 2)

**Prompt:**

```
A directed communication network over GF(5) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 0, 2), ('R', 0, 3), ('R', 0, 4), ('R', 1, 0), ('R', 1, 1), ('R', 1, 2), ('R', 1, 3), ('R', 1, 4), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2), ('S',)->('R', 0, 3), ('S',)->('R', 0, 4), ('R', 0, 0)->('R', 1, 0), ('R', 0, 0)->('R', 1, 1), ('R', 0, 0)->('R', 1, 2), ('R', 0, 0)->('R', 1, 3), ('R', 0, 0)->('R', 1, 4), ('R', 0, 1)->('R', 1, 0), ('R', 0, 1)->('R', 1, 1), ('R', 0, 1)->('R', 1, 2), ('R', 0, 1)->('R', 1, 3), ('R', 0, 1)->('R', 1, 4), ('R', 0, 2)->('R', 1, 0), ('R', 0, 2)->('R', 1, 1), ('R', 0, 2)->('R', 1, 2), ('R', 0, 2)->('R', 1, 3), ('R', 0, 2)->('R', 1, 4), ('R', 0, 3)->('R', 1, 0), ('R', 0, 3)->('R', 1, 1), ('R', 0, 3)->('R', 1, 2), ('R', 0, 3)->('R', 1, 3), ('R', 0, 3)->('R', 1, 4), ('R', 0, 4)->('R', 1, 0), ('R', 0, 4)->('R', 1, 1), ('R', 0, 4)->('R', 1, 2), ('R', 0, 4)->('R', 1, 3), ('R', 0, 4)->('R', 1, 4), ('R', 1, 0)->('T',), ('R', 1, 1)->('T',), ('R', 1, 2)->('T',), ('R', 1, 3)->('T',), ('R', 1, 4)->('T',)
The following edges are erased (unavailable): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2), ('S',)->('R', 0, 3), ('S',)->('R', 0, 4).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`no`

---

## Example 2 (level 2)

**Prompt:**

```
A directed communication network over GF(5) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 1, 0), ('R', 1, 1), ('R', 2, 0), ('R', 2, 1), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('R', 0, 0)->('R', 1, 0), ('R', 0, 0)->('R', 1, 1), ('R', 0, 1)->('R', 1, 0), ('R', 0, 1)->('R', 1, 1), ('R', 1, 0)->('R', 2, 0), ('R', 1, 0)->('R', 2, 1), ('R', 1, 1)->('R', 2, 0), ('R', 1, 1)->('R', 2, 1), ('R', 2, 0)->('T',), ('R', 2, 1)->('T',)
The following edges are erased (unavailable): ('R', 1, 0)->('R', 2, 0), ('R', 1, 0)->('R', 2, 1), ('R', 1, 1)->('R', 2, 0), ('R', 1, 1)->('R', 2, 1), ('R', 2, 0)->('T',), ('R', 2, 1)->('T',), ('S',)->('R', 0, 0), ('S',)->('R', 0, 1).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`no`

---

# Level 5

## Example 1 (level 5)

**Prompt:**

```
A directed communication network over GF(13) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 0, 2), ('R', 1, 0), ('R', 1, 1), ('R', 1, 2), ('R', 2, 0), ('R', 2, 1), ('R', 2, 2), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2), ('R', 0, 0)->('R', 1, 0), ('R', 0, 0)->('R', 1, 1), ('R', 0, 0)->('R', 1, 2), ('R', 0, 1)->('R', 1, 0), ('R', 0, 1)->('R', 1, 1), ('R', 0, 1)->('R', 1, 2), ('R', 0, 2)->('R', 1, 0), ('R', 0, 2)->('R', 1, 1), ('R', 0, 2)->('R', 1, 2), ('R', 1, 0)->('R', 2, 0), ('R', 1, 0)->('R', 2, 1), ('R', 1, 0)->('R', 2, 2), ('R', 1, 1)->('R', 2, 0), ('R', 1, 1)->('R', 2, 1), ('R', 1, 1)->('R', 2, 2), ('R', 1, 2)->('R', 2, 0), ('R', 1, 2)->('R', 2, 1), ('R', 1, 2)->('R', 2, 2), ('R', 2, 0)->('T',), ('R', 2, 1)->('T',), ('R', 2, 2)->('T',)
The following edges are erased (unavailable): ('R', 0, 0)->('R', 1, 1), ('R', 1, 1)->('R', 2, 0), ('R', 1, 1)->('R', 2, 1), ('R', 1, 1)->('R', 2, 2), ('R', 2, 1)->('T',), ('R', 2, 2)->('T',), ('S',)->('R', 0, 2).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`yes`

---

## Example 2 (level 5)

**Prompt:**

```
A directed communication network over GF(13) routes a single source symbol x (a field element) from source node ('S',) to receiver node ('T',). Relay nodes forward or mix the field elements they receive, so the receiver recovers x if and only if at least one directed path from ('S',) to ('T',) survives using only working (unerased) edges.
Nodes: ('S',), ('R', 0, 0), ('R', 0, 1), ('R', 0, 2), ('T',)
Edges (u -> v): ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2), ('R', 0, 0)->('T',), ('R', 0, 1)->('T',), ('R', 0, 2)->('T',)
The following edges are erased (unavailable): ('R', 0, 0)->('T',), ('R', 0, 1)->('T',), ('R', 0, 2)->('T',), ('S',)->('R', 0, 0), ('S',)->('R', 0, 1), ('S',)->('R', 0, 2).
Can the receiver recover the source symbol x despite these erasures? Answer exactly 'yes' or 'no'.
```

**Answer:**

`no`

---
