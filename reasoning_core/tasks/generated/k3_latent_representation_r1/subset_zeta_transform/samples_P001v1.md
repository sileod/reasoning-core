## Level 0

### Example 1 (level 0)

Prompt:

A universe of 4 elements is labeled 1..4. Every subset has an integer value:
  {} -> -9
  {1} -> 8
  {2} -> 4
  {1,2} -> -7
  {3} -> 7
  {1,3} -> 7
  {2,3} -> -7
  {1,2,3} -> -7
  {4} -> -1
  {1,4} -> -1
  {2,4} -> -7
  {1,2,4} -> 8
  {3,4} -> 8
  {1,3,4} -> -1
  {2,3,4} -> -4
  {1,2,3,4} -> -1
Perform the upward zeta transform: for each subset S, the transformed value is the sum over all supersets T of S of the original value of T.
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {1}
  Query: {2,3}
  Query: {3,4}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

6,-19,2

### Example 2 (level 0)

Prompt:

A universe of 4 elements is labeled 1..4. Every subset has an integer value:
  {} -> 1
  {1} -> 6
  {2} -> -4
  {1,2} -> -3
  {3} -> -8
  {1,3} -> 5
  {2,3} -> -8
  {1,2,3} -> -8
  {4} -> 3
  {1,4} -> 8
  {2,4} -> 8
  {1,2,4} -> 4
  {3,4} -> -9
  {1,3,4} -> -9
  {2,3,4} -> 3
  {1,2,3,4} -> 1
Perform the upward Mobius transform (inverse of the upward zeta transform): for each subset S, the transformed value is g(S) = sum over supersets T of S of (-1)^|T\S| * value(T).
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {1}
  Query: {1,2,4}
  Query: {1,3,4}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

-18,3,-10

## Level 2

### Example 1 (level 2)

Prompt:

A universe of 5 elements is labeled 1..5. Every subset has an integer value:
  {} -> 9
  {1} -> -10
  {2} -> -10
  {1,2} -> 4
  {3} -> -9
  {1,3} -> 8
  {2,3} -> 0
  {1,2,3} -> -11
  {4} -> 4
  {1,4} -> -5
  {2,4} -> -9
  {1,2,4} -> -4
  {3,4} -> -8
  {1,3,4} -> -8
  {2,3,4} -> 9
  {1,2,3,4} -> -4
  {5} -> -1
  {1,5} -> 7
  {2,5} -> 3
  {1,2,5} -> -2
  {3,5} -> -11
  {1,3,5} -> -10
  {2,3,5} -> 1
  {1,2,3,5} -> 4
  {4,5} -> -5
  {1,4,5} -> 7
  {2,4,5} -> -10
  {1,2,4,5} -> -1
  {3,4,5} -> -8
  {1,3,4,5} -> 9
  {2,3,4,5} -> 8
  {1,2,3,4,5} -> 1
Perform the upward Mobius transform (inverse of the upward zeta transform): for each subset S, the transformed value is g(S) = sum over supersets T of S of (-1)^|T\S| * value(T).
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {1}
  Query: {1,2,4}
  Query: {2,5}
  Query: {1,4,5}
  Query: {1,3,4,5}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

-59,2,24,0,8

### Example 2 (level 2)

Prompt:

A universe of 5 elements is labeled 1..5. Every subset has an integer value:
  {} -> 8
  {1} -> 4
  {2} -> -3
  {1,2} -> 9
  {3} -> 1
  {1,3} -> 4
  {2,3} -> -11
  {1,2,3} -> 11
  {4} -> 8
  {1,4} -> 10
  {2,4} -> -2
  {1,2,4} -> -10
  {3,4} -> -4
  {1,3,4} -> -4
  {2,3,4} -> -11
  {1,2,3,4} -> 3
  {5} -> 9
  {1,5} -> -3
  {2,5} -> 4
  {1,2,5} -> -10
  {3,5} -> -2
  {1,3,5} -> 1
  {2,3,5} -> -3
  {1,2,3,5} -> -10
  {4,5} -> -8
  {1,4,5} -> -1
  {2,4,5} -> 6
  {1,2,4,5} -> -6
  {3,4,5} -> 6
  {1,3,4,5} -> -5
  {2,3,4,5} -> 3
  {1,2,3,4,5} -> -9
Perform the upward zeta transform: for each subset S, the transformed value is the sum over all supersets T of S of the original value of T.
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {3}
  Query: {1,3,4}
  Query: {1,2,3,4}
  Query: {1,2,5}
  Query: {1,2,3,5}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

-30,-15,-6,-35,-19

## Level 5

### Example 1 (level 5)

Prompt:

A universe of 6 elements is labeled 1..6. Every subset has an integer value:
  {} -> 6
  {1} -> -1
  {2} -> 7
  {1,2} -> 4
  {3} -> 11
  {1,3} -> 10
  {2,3} -> 8
  {1,2,3} -> 8
  {4} -> 6
  {1,4} -> -2
  {2,4} -> -3
  {1,2,4} -> 8
  {3,4} -> 12
  {1,3,4} -> -3
  {2,3,4} -> 8
  {1,2,3,4} -> 1
  {5} -> 8
  {1,5} -> 5
  {2,5} -> 14
  {1,2,5} -> -11
  {3,5} -> -1
  {1,3,5} -> -11
  {2,3,5} -> 7
  {1,2,3,5} -> -5
  {4,5} -> -12
  {1,4,5} -> -11
  {2,4,5} -> 8
  {1,2,4,5} -> -2
  {3,4,5} -> 6
  {1,3,4,5} -> -8
  {2,3,4,5} -> -12
  {1,2,3,4,5} -> -8
  {6} -> -7
  {1,6} -> -6
  {2,6} -> -8
  {1,2,6} -> -1
  {3,6} -> 8
  {1,3,6} -> -5
  {2,3,6} -> 4
  {1,2,3,6} -> -6
  {4,6} -> 2
  {1,4,6} -> 13
  {2,4,6} -> -6
  {1,2,4,6} -> -2
  {3,4,6} -> 11
  {1,3,4,6} -> -13
  {2,3,4,6} -> 11
  {1,2,3,4,6} -> 4
  {5,6} -> 0
  {1,5,6} -> 9
  {2,5,6} -> -5
  {1,2,5,6} -> 3
  {3,5,6} -> 4
  {1,3,5,6} -> 0
  {2,3,5,6} -> 3
  {1,2,3,5,6} -> -1
  {4,5,6} -> -1
  {1,4,5,6} -> 3
  {2,4,5,6} -> -10
  {1,2,4,5,6} -> 5
  {3,4,5,6} -> 3
  {1,3,4,5,6} -> 10
  {2,3,4,5,6} -> -12
  {1,2,3,4,5,6} -> -2
Perform the upward zeta transform: for each subset S, the transformed value is the sum over all supersets T of S of the original value of T.
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {3,4}
  Query: {5}
  Query: {2,5}
  Query: {3,5}
  Query: {1,2,4,5}
  Query: {4,6}
  Query: {2,4,6}
  Query: {1,2,3,5,6}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

8,-24,-28,-27,-7,16,-12,-3

### Example 2 (level 5)

Prompt:

A universe of 6 elements is labeled 1..6. Every subset has an integer value:
  {} -> 8
  {1} -> 6
  {2} -> 5
  {1,2} -> 2
  {3} -> -10
  {1,3} -> 5
  {2,3} -> -2
  {1,2,3} -> 14
  {4} -> -7
  {1,4} -> 12
  {2,4} -> -6
  {1,2,4} -> 1
  {3,4} -> -7
  {1,3,4} -> -14
  {2,3,4} -> -5
  {1,2,3,4} -> 8
  {5} -> 10
  {1,5} -> -2
  {2,5} -> 0
  {1,2,5} -> -5
  {3,5} -> -5
  {1,3,5} -> -2
  {2,3,5} -> -3
  {1,2,3,5} -> -8
  {4,5} -> 3
  {1,4,5} -> 1
  {2,4,5} -> -4
  {1,2,4,5} -> 6
  {3,4,5} -> -8
  {1,3,4,5} -> -10
  {2,3,4,5} -> 10
  {1,2,3,4,5} -> 13
  {6} -> -2
  {1,6} -> -9
  {2,6} -> -9
  {1,2,6} -> 1
  {3,6} -> 1
  {1,3,6} -> -4
  {2,3,6} -> -6
  {1,2,3,6} -> -2
  {4,6} -> -3
  {1,4,6} -> -6
  {2,4,6} -> -7
  {1,2,4,6} -> -5
  {3,4,6} -> -14
  {1,3,4,6} -> -5
  {2,3,4,6} -> -1
  {1,2,3,4,6} -> -4
  {5,6} -> -13
  {1,5,6} -> -14
  {2,5,6} -> -13
  {1,2,5,6} -> 0
  {3,5,6} -> 11
  {1,3,5,6} -> 8
  {2,3,5,6} -> 2
  {1,2,3,5,6} -> -5
  {4,5,6} -> 1
  {1,4,5,6} -> 3
  {2,4,5,6} -> 13
  {1,2,4,5,6} -> 11
  {3,4,5,6} -> -11
  {1,3,4,5,6} -> 5
  {2,3,4,5,6} -> 1
  {1,2,3,4,5,6} -> 14
Perform the upward zeta transform: for each subset S, the transformed value is the sum over all supersets T of S of the original value of T.
Report the transformed value at each queried subset, in the order the queries are listed, as a comma-separated list of integers.
  Query: {4}
  Query: {1,2,4}
  Query: {1,5}
  Query: {4,5}
  Query: {2,3,4,6}
  Query: {2,5,6}
  Query: {1,2,3,5,6}
  Query: {1,2,4,5,6}
Answer format: a single comma-separated list of integers, one per query in order.

Answer:

-15,44,15,48,10,23,9,25
