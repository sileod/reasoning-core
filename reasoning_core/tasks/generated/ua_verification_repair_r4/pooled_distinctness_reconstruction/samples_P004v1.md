# Samples P004v1

## Level 0

### Example 1

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {1, 3} -- exactly 1 distinct type.
Pool 2: items {1, 3} -- at least 1 distinct types.
Pool 3: items {1, 2, 3} -- at least 1 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[[1, 3]] and []

### Example 2

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {1, 2} -- exactly 1 distinct type.
Pool 2: items {1, 3} -- exactly 2 distinct types.
Pool 3: items {0, 1, 2, 3} -- at most 2 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[[1, 2]] and [[1, 3], [2, 3]]

## Level 2

### Example 1

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3, 4, 5]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {2, 3} -- exactly 2 distinct types.
Pool 2: items {0, 2, 4, 5} -- exactly 1 distinct type.
Pool 3: items {2, 4, 5} -- exactly 1 distinct type.
Pool 4: items {0, 5} -- at most 1 distinct types.
Pool 5: items {1, 2, 3, 5} -- exactly 3 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[[0, 2], [0, 4], [0, 5], [2, 4], [2, 5], [4, 5]] and [[0, 1], [0, 3], [1, 2], [1, 3], [1, 4], [1, 5], [2, 3], [3, 4], [3, 5]]

### Example 2

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3, 4, 5]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {0, 1} -- exactly 1 distinct type.
Pool 2: items {1, 2, 4, 5} -- at most 3 distinct types.
Pool 3: items {0, 1, 2, 3, 4, 5} -- at least 1 distinct types.
Pool 4: items {1, 2, 3} -- at most 2 distinct types.
Pool 5: items {2, 3, 4} -- exactly 2 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[[0, 1]] and []

## Level 5

### Example 1

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3, 4, 5, 6]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {0, 3} -- exactly 2 distinct types.
Pool 2: items {0, 1, 2, 3, 4, 5, 6} -- at least 1 distinct types.
Pool 3: items {0, 1, 3, 4, 5} -- exactly 2 distinct types.
Pool 4: items {1, 2, 4, 5} -- at most 3 distinct types.
Pool 5: items {2, 3, 5} -- at least 2 distinct types.
Pool 6: items {0, 1} -- at most 2 distinct types.
Pool 7: items {0, 1, 3, 5, 6} -- exactly 2 distinct types.
Pool 8: items {0, 1, 2, 3, 4, 6} -- at least 2 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[] and [[0, 3]]

### Example 2

**Prompt:**

The items are labeled by the IDs [0, 1, 2, 3, 4, 5, 6]. Each item carries a hidden "type" (two items with the same type are indistinguishable). Several overlapping pools -- subsets of items -- are given; each pool reports a count about the distinct types present among its members, and every pool either reports the exact number of distinct types, an upper bound (at most), or a lower bound (at least). A "consistent typing" assigns a type to every item so that every pool report holds; at least one such typing exists.

The pools are:
Pool 1: items {1, 6} -- exactly 2 distinct types.
Pool 2: items {1, 5} -- exactly 2 distinct types.
Pool 3: items {0, 2, 5} -- exactly 2 distinct types.
Pool 4: items {0, 1} -- exactly 2 distinct types.
Pool 5: items {1, 2, 3, 4, 5, 6} -- at least 2 distinct types.
Pool 6: items {1, 2, 4, 5} -- at most 3 distinct types.
Pool 7: items {1, 2, 4, 5, 6} -- at least 1 distinct types.
Pool 8: items {0, 2, 3} -- at least 1 distinct types.

Two items are FORCED SAME when every consistent typing places them in the same type, and FORCED DIFFERENT when every consistent typing places them in different types.

List every forced same-type pair and every forced different-type pair. Write each pair as a two-item list a<b. Give the answer as two sorted lists: the list of forced same pairs, then the word "and", then the list of forced different pairs; use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]].

Answer:

[] and [[0, 1], [1, 5], [1, 6]]

