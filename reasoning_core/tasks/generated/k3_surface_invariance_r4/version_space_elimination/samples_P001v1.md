# Samples: version_space_elimination (P001v1)

## Level 0
### Example 1
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (6, 6) -> POSITIVE
  instance (0, 6) -> NEGATIVE
  instance (6, 0) -> NEGATIVE
What is the most-general consistent boundary G? Give it as one tuple of group ids, e.g. (14, 10).

**Answer**
(13, 13)

---

### Example 2
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (5, 0) -> POSITIVE
  instance (0, 0) -> NEGATIVE
  instance (5, 4) -> NEGATIVE
What is the most-general consistent boundary G? Give it as one tuple of group ids, e.g. (14, 10).

**Answer**
(13, 12)

---

## Level 2
### Example 1
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (3, 5) -> POSITIVE
  instance (6, 5) -> NEGATIVE
  instance (3, 6) -> NEGATIVE
Now a new instance appears: (3, 5).
Is its label forced to be positive, forced to be negative, or still unknown? Answer with exactly one word: positive, negative, or unknown.

**Answer**
positive

---

### Example 2
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (5, 1) -> POSITIVE
  instance (3, 1) -> NEGATIVE
  instance (5, 6) -> NEGATIVE
What is the most-specific consistent boundary S? Give it as one tuple of group ids, e.g. (5, 2).

**Answer**
(5, 1)

---

## Level 5
### Example 1
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (0, 6, 7, 7) -> POSITIVE
  instance (2, 6, 7, 7) -> NEGATIVE
  instance (0, 2, 7, 7) -> NEGATIVE
  instance (0, 6, 4, 7) -> NEGATIVE
  instance (0, 6, 7, 4) -> NEGATIVE
What is the most-specific consistent boundary S? Give it as one tuple of group ids, e.g. (5, 2).

**Answer**
(0, 6, 7, 7)

---

### Example 2
**Prompt**
Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.
Group contents: 8={0,1}; 9={2,3}; 10={4,5}; 11={6,7}; 12={0,1,2,3}; 13={4,5,6,7}; 14={0,1,2,3,4,5,6,7} (leaves 0-7 are singletons; 14 is all 8).
A conjunctive hypothesis assigns each feature one group and covers an instance (a tuple of leaves) if every feature's group contains its leaf.
You receive labeled examples and maintain the version-space boundaries: S = most-specific consistent hypotheses, G = most-general consistent ones.
Examples:
  instance (3, 4, 6, 6) -> POSITIVE
  instance (1, 4, 6, 6) -> NEGATIVE
  instance (3, 0, 6, 6) -> NEGATIVE
  instance (3, 4, 5, 6) -> NEGATIVE
  instance (3, 4, 6, 0) -> NEGATIVE
Now a new instance appears: (1, 1, 6, 3).
Is its label forced to be positive, forced to be negative, or still unknown? Answer with exactly one word: positive, negative, or unknown.

**Answer**
negative

---
