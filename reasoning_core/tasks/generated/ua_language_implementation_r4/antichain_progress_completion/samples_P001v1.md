### Level 0

**Prompt**:

Progress across a system is tracked over 2 independent lanes, and a time is a 2-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (0, 3), (3, 0). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0), (0, 2), (1, 2), (1, 3), (2, 2).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0), (0, 2), (1, 2), (2, 2)

**Prompt**:

Progress across a system is tracked over 2 independent lanes, and a time is a 2-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (1, 2), (2, 1). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0), (0, 3), (1, 1), (2, 3), (3, 3).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0), (0, 3), (1, 1)

### Level 2

**Prompt**:

Progress across a system is tracked over 2 independent lanes, and a time is a 2-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (0, 7), (5, 2), (6, 1), (7, 0). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0), (0, 1), (0, 8), (2, 4), (3, 1), (3, 2), (5, 1).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0), (0, 1), (2, 4), (3, 1), (3, 2), (5, 1)

**Prompt**:

Progress across a system is tracked over 2 independent lanes, and a time is a 2-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (0, 7), (3, 4), (6, 1), (7, 0). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0), (0, 8), (1, 0), (3, 3), (3, 4), (4, 2), (5, 4).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0), (1, 0), (3, 3), (3, 4), (4, 2)

### Level 5

**Prompt**:

Progress across a system is tracked over 3 independent lanes, and a time is a 3-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (0, 2, 11), (0, 6, 7), (4, 5, 4), (6, 6, 1), (7, 1, 5), (7, 4, 2), (9, 1, 3). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0, 0), (0, 2, 16), (1, 5, 8), (2, 8, 3), (5, 3, 4), (6, 4, 0), (6, 6, 5), (7, 0, 4), (7, 1, 2), (7, 3, 1).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0, 0), (1, 5, 8), (2, 8, 3), (5, 3, 4), (6, 4, 0), (7, 0, 4), (7, 1, 2), (7, 3, 1)

**Prompt**:

Progress across a system is tracked over 3 independent lanes, and a time is a 3-tuple of non-negative integers, one coordinate per lane. A new time can follow an earlier one only when it is at least as large in every lane, so later work makes progress by advancing individual lanes (forks and joins of parallel work). The current frontier is the set of furthest-progress times observed: (1, 4, 8), (1, 7, 5), (1, 12, 0), (4, 5, 4), (5, 5, 3), (7, 3, 3), (11, 1, 1). A frontier element f still precedes a time T when f[i] <= T[i] for every lane i and f is not equal to T; such an f means work has not yet finished passing T. A queried time T is therefore COMPLETE exactly when no frontier element still precedes it.
The queried times are: (0, 0, 0), (1, 3, 3), (4, 3, 6), (4, 4, 8), (4, 6, 0), (4, 9, 4), (6, 8, 2), (7, 4, 8), (7, 8, 6), (8, 1, 6).
List the queried times that are COMPLETE, in lexicographic order (compare lane by lane, first lane smallest first), as tuples separated by comma-space, for example '(0, 1), (2, 0)'. If no queried time is complete, write the single word 'none'.

**Answer**: (0, 0, 0), (1, 3, 3), (4, 3, 6), (4, 6, 0), (6, 8, 2), (8, 1, 6)
