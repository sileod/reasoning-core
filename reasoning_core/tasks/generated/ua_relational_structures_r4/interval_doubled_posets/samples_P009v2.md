# Samples for interval_doubled_posets (P009v2)

## Level 0

### Example 1

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,2 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (0,1) (1,2). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [1, 2] of the current poset; double the interval [1.0, 1.1] of the current poset. After all doublings, consider the element 1.0.0 and the element 1.0.1. Does the element 1.0.1 directly cover the element 1.0.0 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 1.0.0 and 1.0.1.

**Answer:**

YES

### Example 2

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,2 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (0,1) (1,2). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [0, 1] of the current poset; double the interval [0.0, 1.0] of the current poset. After all doublings, consider the element 1.0.0 and the element 1.0.1. Does the element 1.0.1 directly cover the element 1.0.0 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 1.0.0 and 1.0.1.

**Answer:**

YES

## Level 2

### Example 1

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,4 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (0,1) (1,2) (1,3) (3,4). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [1, 3] of the current poset; double the interval [1.0, 2] of the current poset; double the interval [1.1.0, 3.1] of the current poset. After all doublings, consider the element 1.1.0.1 and the element 3.0.1. Does the element 3.0.1 directly cover the element 1.1.0.1 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 1.1.0.1 and 3.0.1.

**Answer:**

NO

### Example 2

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,4 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (1,3) (2,3) (2,4). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [2, 4] of the current poset; double the interval [2.0, 2.1] of the current poset; double the interval [2.0.1, 2.1.0] of the current poset. After all doublings, consider the element 2.0.1.1 and the element 2.1.1. Does the element 2.1.1 directly cover the element 2.0.1.1 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 2.0.1.1 and 2.1.1.

**Answer:**

NO

## Level 5

### Example 1

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,7 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (0,2) (1,2) (0,3) (3,4) (1,5) (4,5) (5,6) (5,7). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [1, 5] of the current poset; double the interval [0, 4] of the current poset; double the interval [0.0, 3.0] of the current poset; double the interval [0.0.0, 4.0] of the current poset; double the interval [5.1, 6] of the current poset. After all doublings, consider the element 0.1.0.0 and the element 0.1.0.1. Does the element 0.1.0.1 directly cover the element 0.1.0.0 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 0.1.0.0 and 0.1.0.1.

**Answer:**

YES

### Example 2

**Prompt:**

Consider a finite poset (partially ordered set) whose elements are named 0,1,...,7 and whose cover relations (immediate orderings, a direct successor of b when a<b and no element lies strictly between) are: (0,3) (0,4) (1,5) (2,5) (3,5) (4,5) (5,6) (6,7). Here a<b means the reflexive-transitive closure, and elements are comparable when one is below the other in that closure. A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. Elements outside the interval keep their identity. Order between copies: for originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; additionally u''<=v' holds only when u<v strictly (so the two layers stay distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and t-copy<=o iff t<=o. Apply the following doublings in order, each to the current poset (intervals are named by the current element identities): double the interval [2, 5] of the current poset; double the interval [3, 7] of the current poset; double the interval [7.0, 7.1] of the current poset; double the interval [3.0, 3.1] of the current poset; double the interval [4, 6.0] of the current poset. After all doublings, consider the element 5.0.0.0 and the element 5.0.0.1. Does the element 5.0.0.1 directly cover the element 5.0.0.0 (i.e. x<y and no element lies strictly between them in the final poset)? Reply exactly YES or NO. The compared elements are 5.0.0.0 and 5.0.0.1.

**Answer:**

YES
