## Level 0
### Example 1
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [1]
object 1 has attributes [2]
object 2 has attributes [0]
For an attribute set X, its closure X'' is the set of attributes that every object carrying all of X also carries. Compute the closure of [1]. Answer with one sorted list of attribute ids, e.g. [0, 2].

**Answer:**
[1]

### Example 2
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [1]
object 1 has attributes []
A concept (maximal rectangle) is a pair (E, I) where E is a maximal set of objects, I is the attribute set they all share, and E = {o: I ⊆ obj(o)} with I closed. List ALL concepts as [([objs], [attrs]), ...]: each extent and intent sorted ascending, the list sorted lexicographically by then by extent then intent.

**Answer:**
[([], [0]), ([0], [1]), ([0, 1], [])]

### Example 3
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [0, 3, 4]
object 1 has attributes [0, 1, 2, 4]
object 2 has attributes [1, 2, 3, 4]
object 3 has attributes [0, 1, 2, 3]
object 4 has attributes [1, 2, 4]
An implication X -> Y holds iff every object carrying all of X also carries all of Y. Does [0, 1, 2, 3, 4] -> [0, 1, 2, 3] hold here? Answer exactly 'yes' or 'no'.

**Answer:**
no

## Level 2
### Example 1
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [0, 1, 3, 4, 9, 10, 12, 13, 15, 16, 17, 18]
object 1 has attributes [0, 2, 4, 5, 6, 7, 9, 11, 12, 13, 15, 18]
object 2 has attributes [1, 2, 3, 6, 7, 10, 15, 18]
object 3 has attributes [2, 3, 4, 5, 6, 7, 10, 13, 14, 16, 17, 18]
object 4 has attributes [0, 1, 3, 5, 6, 7, 8, 14]
object 5 has attributes [3, 6, 8, 9, 18]
object 6 has attributes [0, 2, 5, 8, 9, 11, 18]
object 7 has attributes [0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 16]
object 8 has attributes [1, 2, 3, 4, 6, 8, 10, 11, 14, 15]
object 9 has attributes [4, 5, 8, 10, 15, 16, 17, 18]
object 10 has attributes [1, 4, 5, 6, 8, 9, 10, 11, 14, 15]
object 11 has attributes [0, 1, 4, 8, 11, 14, 15, 16, 18]
object 12 has attributes [0, 2, 3, 5, 7, 9, 12, 13, 14, 15, 16, 18]
object 13 has attributes [1, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16]
object 14 has attributes [1, 2, 5, 6, 10, 11, 15, 16, 18]
object 15 has attributes [4, 5, 6, 11, 13, 14, 15, 16, 18]
object 16 has attributes [1, 3, 4, 9, 10, 16]
object 17 has attributes [8, 9, 10, 11, 12, 15]
object 18 has attributes [0, 4, 5, 6, 11, 17]
An implication X -> Y holds iff every object carrying all of X also carries all of Y. Does [0, 1, 11, 12, 14, 15, 16] -> [0, 8, 9, 12, 16] hold here? Answer exactly 'yes' or 'no'.

**Answer:**
no

### Example 2
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [0, 1, 2, 3, 4, 5, 8]
object 1 has attributes [1, 2, 3, 5, 8]
object 2 has attributes [0, 2, 3, 4, 5, 6, 7]
object 3 has attributes [2, 5]
object 4 has attributes [6, 7]
object 5 has attributes [1, 5, 6, 7]
object 6 has attributes [3, 5, 6, 7, 8]
object 7 has attributes [2, 7, 8]
object 8 has attributes [0, 2, 4, 7, 8]
For an attribute set X, its closure X'' is the set of attributes that every object carrying all of X also carries. Compute the closure of [0, 1, 2, 3, 5, 6, 7, 8]. Answer with one sorted list of attribute ids, e.g. [0, 2].

**Answer:**
[0, 1, 2, 3, 4, 5, 6]

## Level 5
### Example 1
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 16, 19, 20, 21, 22, 24, 25, 26, 27, 29, 30, 31, 32, 33, 35, 36, 37, 39]
object 1 has attributes [1, 3, 4, 5, 6, 8, 9, 12, 13, 17, 18, 22, 24, 26, 28, 29, 32, 34, 37]
object 2 has attributes [0, 2, 5, 6, 10, 12, 13, 14, 18, 19, 21, 22, 24, 26, 27, 29, 31, 32, 35, 36, 38]
object 3 has attributes [0, 4, 5, 6, 8, 9, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 28, 30, 34, 35, 36, 38, 39]
object 4 has attributes [2, 3, 4, 5, 6, 12, 13, 17, 18, 23, 24, 25, 26, 27, 30, 32, 33, 34, 37, 38, 39]
object 5 has attributes [4, 5, 6, 7, 8, 10, 11, 12, 13, 20, 21, 22, 23, 24, 25, 30, 31, 32, 34, 36, 37]
object 6 has attributes [1, 2, 6, 7, 10, 14, 16, 18, 20, 22, 23, 24, 25, 29, 35, 36]
object 7 has attributes [3, 5, 6, 7, 8, 11, 13, 15, 16, 19, 20, 22, 24, 26, 27, 29, 30, 37, 38]
object 8 has attributes [0, 1, 2, 3, 4, 5, 8, 9, 12, 14, 15, 16, 21, 24, 25, 26, 27, 28, 29, 34]
object 9 has attributes [1, 2, 6, 7, 8, 11, 13, 14, 17, 19, 24, 28, 30, 32, 33, 34, 35, 36, 37, 38]
object 10 has attributes [0, 7, 8, 9, 10, 12, 13, 16, 17, 18, 22, 24, 25, 26, 29, 30, 31, 33, 34, 35, 36, 37]
object 11 has attributes [0, 1, 3, 4, 5, 6, 8, 12, 13, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 29, 30, 33, 35, 38]
object 12 has attributes [1, 3, 4, 5, 8, 9, 13, 15, 16, 17, 19, 21, 26, 28, 29, 30, 31, 33, 36, 39]
object 13 has attributes [1, 2, 3, 7, 9, 12, 13, 14, 15, 17, 20, 22, 27, 28, 31, 32, 34, 35, 36, 37, 39]
object 14 has attributes [1, 2, 3, 4, 5, 8, 12, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 29, 31, 32, 33, 34, 37]
object 15 has attributes [0, 1, 3, 5, 8, 9, 11, 12, 15, 16, 18, 19, 21, 22, 23, 24, 25, 26, 28, 31, 35, 38, 39]
object 16 has attributes [1, 3, 4, 5, 8, 9, 10, 13, 14, 16, 17, 18, 21, 24, 25, 26, 27, 29, 30, 31, 32, 36, 37, 39]
object 17 has attributes [1, 4, 5, 6, 7, 8, 11, 13, 17, 22, 23, 27, 28, 30, 31, 32, 35, 37, 38, 39]
object 18 has attributes [0, 2, 5, 6, 7, 9, 10, 13, 17, 18, 20, 28, 29, 33, 35, 36, 37, 39]
object 19 has attributes [1, 2, 5, 7, 13, 14, 15, 17, 19, 21, 22, 29, 30, 31, 33, 35, 36, 38]
object 20 has attributes [0, 1, 2, 4, 6, 7, 8, 9, 11, 12, 13, 14, 18, 19, 20, 21, 22, 26, 27, 28, 30, 31, 32, 33, 36, 37, 38, 39]
object 21 has attributes [1, 3, 4, 6, 7, 10, 11, 12, 14, 17, 18, 19, 22, 23, 29, 30, 32, 33, 36, 37, 39]
object 22 has attributes [0, 1, 2, 3, 4, 7, 9, 11, 12, 16, 17, 21, 24, 26, 27, 28, 30, 34, 36, 38, 39]
object 23 has attributes [1, 4, 5, 6, 7, 9, 12, 13, 14, 18, 19, 22, 23, 25, 26, 28, 29, 30, 31, 33, 34, 37, 38]
object 24 has attributes [0, 2, 4, 5, 6, 7, 10, 11, 14, 15, 17, 18, 21, 23, 24, 26, 29, 30, 33, 34, 35, 36, 38]
object 25 has attributes [1, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 27, 28, 29, 30, 31, 32, 33, 34, 35]
object 26 has attributes [1, 2, 5, 9, 10, 12, 15, 17, 18, 20, 21, 22, 24, 26, 27, 32, 33, 34, 35, 36, 39]
object 27 has attributes [2, 4, 5, 6, 7, 8, 9, 12, 13, 16, 22, 23, 26, 27, 28, 31, 32, 33, 34, 35, 36, 37, 39]
object 28 has attributes [4, 6, 7, 11, 14, 15, 16, 17, 20, 23, 24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 38, 39]
object 29 has attributes [0, 2, 5, 6, 9, 10, 11, 13, 14, 17, 22, 23, 24, 25, 29, 30, 31, 32, 36, 38, 39]
object 30 has attributes [0, 2, 3, 4, 5, 8, 9, 12, 18, 20, 21, 24, 25, 27, 29, 30, 31, 32, 33, 34, 38, 39]
object 31 has attributes [5, 6, 7, 9, 10, 12, 14, 16, 17, 18, 22, 24, 26, 29, 30, 31, 32, 33, 34, 37, 38, 39]
object 32 has attributes [0, 1, 3, 4, 5, 6, 13, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 39]
object 33 has attributes [0, 5, 6, 7, 8, 10, 13, 14, 15, 21, 23, 24, 25, 27, 30, 32, 33, 34, 35, 37, 38]
object 34 has attributes [1, 3, 4, 6, 8, 10, 14, 15, 16, 20, 21, 23, 24, 28, 29, 34, 36, 37, 38, 39]
object 35 has attributes [0, 1, 3, 8, 9, 10, 11, 12, 16, 18, 19, 23, 24, 27, 28, 30, 32, 34, 38, 39]
object 36 has attributes [0, 2, 3, 4, 5, 12, 13, 14, 17, 18, 19, 24, 26, 27, 29, 33, 34, 36, 37]
object 37 has attributes [1, 9, 11, 13, 14, 15, 17, 19, 21, 22, 24, 25, 32, 33, 35, 36, 37]
object 38 has attributes [0, 2, 8, 9, 10, 11, 13, 14, 15, 16, 18, 25, 27, 28, 29, 30, 31, 34, 37]
object 39 has attributes [0, 2, 3, 4, 5, 6, 7, 13, 14, 16, 19, 20, 21, 22, 24, 26, 28, 30, 31, 33, 35, 38]
An implication X -> Y holds iff every object carrying all of X also carries all of Y. Does [4, 7, 9, 12, 13, 15, 18, 19, 21, 25, 26, 27, 31, 32, 34, 35, 36, 38, 39] -> [8, 9, 17, 25, 29, 38] hold here? Answer exactly 'yes' or 'no'.

**Answer:**
no

### Example 2
**Prompt:**
Objects and attributes form an incidence context:
object 0 has attributes [0, 1, 2, 3, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16, 17]
object 1 has attributes [1, 2, 4, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17]
object 2 has attributes [2, 3, 7, 8, 10, 11, 12, 13, 14, 15]
object 3 has attributes [3, 4, 5, 6, 7, 9, 10, 13, 14, 15, 16, 17]
object 4 has attributes [1, 2, 3, 4, 5, 7, 9, 10, 11, 13, 15, 17]
object 5 has attributes [1, 2, 3, 5, 7, 8, 11, 12, 13, 14, 16, 17]
object 6 has attributes [0, 1, 3, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17]
object 7 has attributes [0, 1, 2, 3, 6, 7, 9, 11, 12, 13, 14, 16, 17]
object 8 has attributes [0, 2, 4, 5, 6, 7, 9, 10, 11, 12, 13, 15, 16, 17]
object 9 has attributes [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 15, 16]
object 10 has attributes [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15]
object 11 has attributes [0, 1, 2, 4, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17]
object 12 has attributes [0, 1, 2, 3, 4, 5, 6, 9, 14, 15, 17]
object 13 has attributes [0, 4, 5, 9, 11, 13, 14]
object 14 has attributes [0, 3, 5, 6, 8, 9, 10, 11, 12, 13, 15, 16]
object 15 has attributes [0, 2, 3, 4, 5, 6, 7, 9, 13, 15, 16]
object 16 has attributes [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 16, 17]
object 17 has attributes [0, 3, 6, 8, 9, 10, 12, 14, 15, 17]
For an attribute set X, its closure X'' is the set of attributes that every object carrying all of X also carries. Compute the closure of [0, 2, 3, 9, 10, 11, 16]. Answer with one sorted list of attribute ids, e.g. [0, 2].

**Answer:**
[0, 2, 3, 5, 6, 8, 9, 10, 11, 12, 16, 17]
