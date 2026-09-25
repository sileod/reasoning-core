# Samples for independence_axiom_entailment (P010v1)

## Level 0

### Example 1

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {4} ; {1,2} | {3}
  {2} ; {1,3} | {4}
  {2,3} ; {1} | {4}

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {2} ; {3,4} | {1}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

no

### Example 2

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {1,3} ; {2} | {4}
  {3,4} ; {1} | {2}
  {4} ; {1,2} | {3}

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {1,3} ; {4} | {2}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

no

## Level 2

### Example 1

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {2,3,4} ; {5} | {1}
  {4} ; {1} | {2,3,5}
  {2,4,5} ; {3} | {1}
  {1} ; {3,4,5} | {2}

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {5} ; {2} | {1,4}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

yes

### Example 2

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {2,3} ; {5} | {1,4}
  {1,3,4} ; {5} | {2}
  {4} ; {1,5} | {2,3}
  {2,5} ; {1,3} | {4}
Assume the underlying distribution is strictly positive (so the intersection axiom applies).

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {1,4} ; {3} | {2,5}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

no

## Level 5

### Example 1

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {2,3,5} ; {4,6} | {1}
  {2,3,4} ; {1,6} | {5}
  {1,4,5,6} ; {2} | {3}
  {2} ; {3,4,5,6} | {1}
  {1,3,5,6} ; {4} | {2}

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {4,6} ; {2,3} | {1}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

yes

### Example 2

**Prompt:**

```
Given the following conditional independence statements over a set of variables U, where (A ; B | C) means A is conditionally independent of B given C, and the three sets in each statement are pairwise disjoint and nonempty, together, they cover nothing in particular:
  {1,5} ; {2,3} | {4,6}
  {3,6} ; {1,4,5} | {2}
  {4} ; {1,5} | {2,3,6}
  {2,3,6} ; {5} | {1,4}
  {5} ; {1,2,3,6} | {4}

Using the graphoid axioms (symmetry, decomposition, weak union, contraction, and intersection only when positivity holds), decide whether each statement below follows from the premises.
Statement: {5} ; {2} | {4,6}
Respond with the word yes when it follows and the word no when it does not follow.
```

**Answer:**

yes
