## Level 0
### Example 1 (mode: idem)
Prompt:

A transformation on the set {0,...,2} is recorded as a tuple (f(0),f(1),...,f(2)), so tuple t means t[i] is the image of i. Given generators (1,2,1), (1,1,2), composing two maps a then b sends x to b(a(x)). A map e is idempotent when composing it with itself leaves it unchanged, e(e(i))=e(i) for all i. Among the maps in the closure, how many are idempotent? Answer one integer.

Answer: 2

### Example 2 (mode: size)
Prompt:

A transformation on the set {0,...,2} is recorded as a tuple (f(0),f(1),...,f(2)), so tuple t means t[i] is the image of i. Given generators (2,0,0), (0,2,2), composing two maps a then b sends x to b(a(x)). Consider every map reachable as a nonempty composition of the generators (the closure). How many distinct maps are in this closure? Answer one integer.

Answer: 2

## Level 2
### Example 1 (mode: witness)
Prompt:

A transformation on the set {0,...,4} is recorded as a tuple (f(0),f(1),...,f(4)), so tuple t means t[i] is the image of i. Given generators (2,1,1,3,3), (3,3,2,1,2), (2,3,2,1,1), (1,3,1,2,2), composing two maps a then b sends x to b(a(x)). Give a nonempty word of generator numbers, 0-indexed, whose composition equals the map (3,3,3,1,3). A word 'i1,i2,...,im' means apply generator i1 first, then i2, ..., then im. Give numbers separated by commas, e.g. '2,0,1'.

Answer: 1,1,0,1

### Example 2 (mode: orbit)
Prompt:

A transformation on the set {0,...,4} is recorded as a tuple (f(0),f(1),...,f(4)), so tuple t means t[i] is the image of i. Given generators (4,3,3,2,2), (3,4,3,3,3), (3,4,2,2,4), (3,3,4,2,2), composing two maps a then b sends x to b(a(x)). The orbit of an element i under the map (3,3,2,3,3) is the set of distinct values reached by repeatedly applying the map, {i, f(i), f(f(i)), ...} until a value repeats. Starting from element 4, how many distinct elements are in its orbit? Answer one integer.

Answer: 2

## Level 5
### Example 1 (mode: size)
Prompt:

A transformation on the set {0,...,6} is recorded as a tuple (f(0),f(1),...,f(6)), so tuple t means t[i] is the image of i. Given generators (2,0,4,4,0,0,0), (4,2,2,4,4,4,0), (4,2,0,2,0,4,0), (2,0,0,4,2,2,0), composing two maps a then b sends x to b(a(x)). Consider every map reachable as a nonempty composition of the generators (the closure). How many distinct maps are in this closure? Answer one integer.

Answer: 81

### Example 2 (mode: size)
Prompt:

A transformation on the set {0,...,6} is recorded as a tuple (f(0),f(1),...,f(6)), so tuple t means t[i] is the image of i. Given generators (4,4,5,4,4,1,5), (4,5,5,1,4,1,1), (4,4,1,1,1,5,4), (1,1,5,1,5,4,1), composing two maps a then b sends x to b(a(x)). Consider every map reachable as a nonempty composition of the generators (the closure). How many distinct maps are in this closure? Answer one integer.

Answer: 87

