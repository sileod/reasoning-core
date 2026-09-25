## Level 0
### Example 1
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: c -> a

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: a -> null
Answer: False

### Example 2
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: a -> null; b -> b

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: (a -> a * emp)
Answer: False

## Level 2
### Example 1
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c, d}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: the heap is empty

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: ((c -> a -* b -> d) -* a -> c)
Answer: False

### Example 2
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c, d}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: b -> b; d -> a

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: (d -> a * b -> b)
Answer: True

## Level 5
### Example 1
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c, d}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: a -> a; d -> c

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: (a -> c * (b -> d -* (emp * c -> null)))
Answer: False

### Example 2
Prompt:
Consider a heap whose locations are drawn from the set {a, b, c, d}, where each location has at most one outgoing pointer, and a pointer may target any location in the set or the special value null. The heap is described by listing its points-to facts; any location not listed has no outgoing pointer.

The heap is: a -> d; c -> c; d -> b

Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap (no pointers). A * B holds iff the heap can be split into two disjoint heaps (disjoint sets of locations holding pointers) with one satisfying A and the other satisfying B. A -* B holds iff for every heap h' disjoint from the current heap (built only from locations that currently hold no pointer here) that satisfies A, merging h' into the current heap yields a heap satisfying B.

Decide whether the following assertion is true of the given heap, and state your conclusion as exactly the single word 'true' or 'false'.

Assertion: (((b -> b * emp) -* a -> b) -* (c -> null * (a -> d -* c -> null)))
Answer: False
