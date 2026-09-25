## Level 0

### Example 1

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(1, 1)].
  Shape 2: vertices at [(3, 1)].
  Shape 3: vertices at [(0, 3)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
The two sentences use separate datum alignments on the same coordinate axes; each candidate shape keeps its displayed coordinates under both readings. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [-1,3] x [3,6]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [-3,0] x [0,4].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: equal

### Example 2

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(0, 3)].
  Shape 2: vertices at [(2, 1)].
  Shape 3: vertices at [(0, 1)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
Both sentences align the candidate set to the same datum origin and allow the envelope to be translated with the datum. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [-3,1] x [1,2]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [-3,1] x [1,2].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: equal

## Level 2

### Example 1

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(0, 2), (1, 0), (3, 1)].
  Shape 2: vertices at [(0, 1), (2, 1), (3, 1)].
  Shape 3: vertices at [(0, 3), (3, 0), (3, 1)].
  Shape 4: vertices at [(1, 3), (2, 1), (2, 2)].
  Shape 5: vertices at [(0, 1), (1, 0), (2, 2)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
The two sentences use separate datum alignments on the same coordinate axes; each candidate shape keeps its displayed coordinates under both readings. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [-2,2] x [-3,2]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [-4,2] x [-2,2].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: equal

### Example 2

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(0, 1), (1, 1), (3, 1)].
  Shape 2: vertices at [(1, 0), (1, 1), (3, 0)].
  Shape 3: vertices at [(0, 0), (0, 2), (1, 0)].
  Shape 4: vertices at [(0, 0), (0, 2), (2, 2)].
  Shape 5: vertices at [(0, 1), (0, 2), (1, 2)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
The two sentences use separate datum alignments on the same coordinate axes; each candidate shape keeps its displayed coordinates under both readings. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [-5,1] x [2,6]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [-2,1] x [2,8].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: equal

## Level 5

### Example 1

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(0, 0), (0, 2), (0, 3), (1, 0), (2, 0), (3, 1)].
  Shape 2: vertices at [(0, 1), (0, 2), (1, 0), (1, 2), (2, 2), (3, 0)].
  Shape 3: vertices at [(0, 1), (0, 3), (1, 2), (2, 0), (2, 2), (3, 0)].
  Shape 4: vertices at [(0, 0), (0, 1), (1, 3), (2, 1), (2, 2), (3, 1)].
  Shape 5: vertices at [(0, 0), (0, 1), (1, 1), (2, 0), (2, 1), (3, 1)].
  Shape 6: vertices at [(0, 0), (0, 1), (0, 3), (1, 0), (1, 3), (3, 1)].
  Shape 7: vertices at [(0, 0), (0, 1), (1, 1), (1, 3), (2, 2), (3, 0)].
  Shape 8: vertices at [(0, 1), (1, 0), (1, 1), (1, 3), (2, 0), (2, 2)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
Both sentences align the candidate set to the same datum origin and allow the envelope to be translated with the datum. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [3,8] x [-3,6]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [1,4] x [-4,1].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: not_equal

### Example 2

Prompt:

Consider the collection of candidate shapes given in the coordinate plane, each described by a finite set of polygonal vertices:
  Shape 1: vertices at [(0, 3), (1, 0), (1, 3), (2, 0), (2, 1), (3, 1)].
  Shape 2: vertices at [(0, 0), (0, 1), (0, 3), (1, 0), (2, 2), (3, 0)].
  Shape 3: vertices at [(0, 1), (1, 2), (1, 3), (2, 2), (3, 0), (3, 1)].
  Shape 4: vertices at [(0, 2), (0, 3), (1, 3), (2, 0), (2, 1), (3, 1)].
  Shape 5: vertices at [(0, 1), (0, 2), (0, 3), (1, 0), (1, 2), (2, 1)].
  Shape 6: vertices at [(0, 1), (0, 3), (1, 1), (1, 2), (2, 2), (3, 0)].
  Shape 7: vertices at [(0, 0), (0, 1), (1, 0), (1, 1), (1, 2), (3, 1)].
  Shape 8: vertices at [(1, 2), (1, 3), (2, 0), (2, 1), (2, 2), (3, 1)].
The two sentences below each define an acceptance condition for whether a candidate shape is allowed in a tolerance zone.
The two sentences use separate datum alignments on the same coordinate axes; each candidate shape keeps its displayed coordinates under both readings. Sentence 1 accepts a shape if at least one of its vertices lies in the rectangle [-3,5] x [2,4]. Sentence 2 accepts a shape if at least one of its vertices lies in the rectangle [1,9] x [0,7].
Determine whether the two sentences' geometric acceptance conditions admit exactly the same candidate shapes from the collection above.
Answer with exactly one of the two tokens: 'equal' (the acceptance conditions admit exactly the same candidate shapes) or 'not_equal' (they differ on at least one candidate shape).

Answer: equal

