# Level 0

### Example 1
**Prompt:**
```
A read-once Boolean formula over 5 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  (((not (((not x0) AND x1) AND x2)) OR x3) OR x4)

Current assignment:
  x0 = 0, x1 = 0, x2 = 1, x3 = 0, x4 = 0
The formula evaluates to 1 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[1];[]
```

### Example 2
**Prompt:**
```
A read-once Boolean formula over 5 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  ((((x0 AND (not x1)) OR x2) OR x3) AND x4)

Current assignment:
  x0 = 0, x1 = 1, x2 = 1, x3 = 0, x4 = 0
The formula evaluates to 0 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[4];[]
```


# Level 2

### Example 1
**Prompt:**
```
A read-once Boolean formula over 9 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  ((not x0) OR ((((not x1) OR (not ((not x2) OR (not x3)))) AND (((not x4) OR x5) OR (x6 OR x7))) AND x8))

Current assignment:
  x0 = 0, x1 = 1, x2 = 1, x3 = 0, x4 = 0, x5 = 0, x6 = 1, x7 = 0, x8 = 1
The formula evaluates to 1 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[0];[]
```

### Example 2
**Prompt:**
```
A read-once Boolean formula over 9 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  (not (x0 AND (x1 OR (not ((not x2) AND ((not x3) AND ((not (((not x4) AND (x5 OR (not x6))) AND (not x7))) AND (not x8))))))))

Current assignment:
  x0 = 1, x1 = 0, x2 = 0, x3 = 0, x4 = 1, x5 = 0, x6 = 0, x7 = 1, x8 = 0
The formula evaluates to 1 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[1,2,3,8];[(4 7)]
```


# Level 5

### Example 1
**Prompt:**
```
A read-once Boolean formula over 15 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  (((x0 AND x1) OR (not x2)) OR (((not ((not x3) AND x4)) OR x5) OR ((((x6 OR (not (x7 OR (not x8)))) AND x9) OR (not (x10 OR (x11 AND x12)))) OR (not (x13 AND x14)))))

Current assignment:
  x0 = 1, x1 = 0, x2 = 1, x3 = 0, x4 = 1, x5 = 1, x6 = 1, x7 = 1, x8 = 0, x9 = 0, x10 = 1, x11 = 1, x12 = 0, x13 = 1, x14 = 1
The formula evaluates to 1 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[5];[]
```

### Example 2
**Prompt:**
```
A read-once Boolean formula over 15 input bits uses each input exactly once. Its parse tree (AND, OR, NOT gates) is:

  ((((not x0) OR (((not x1) AND x2) OR x3)) OR (not x4)) OR (not ((x5 OR ((x6 AND x7) AND (not x8))) OR ((x9 AND x10) AND ((x11 AND x12) AND ((not x13) AND (not x14)))))))

Current assignment:
  x0 = 1, x1 = 1, x2 = 1, x3 = 1, x4 = 0, x5 = 1, x6 = 0, x7 = 0, x8 = 0, x9 = 0, x10 = 1, x11 = 1, x12 = 1, x13 = 1, x14 = 0
The formula evaluates to 1 under this assignment.

Define:
  * A single bit i is 'critical' if flipping only bit i (leaving all others as assigned) changes the formula's output.
  * An unordered pair {i,j} with i<j is a 'critical pair' if flipping both i and j together changes the output, but neither i alone nor j alone is critical.

Find:
  1. the sorted list of critical bits,
  2. the sorted list of critical pairs, ordered lexicographically by (i,j).

Answer exactly in this format, with [] for an empty list:
  [critical bits...];[(pair1),(pair2),...]
where each bit is an index and each pair is (i j) with i<j. Example (for a different instance): if bits 0 and 3 are critical and pairs (1 2), (2 4) are critical, answer:
  [0,3];[(1 2),(2 4)]
```
**Answer:**
```
[];[(3 4)]
```


