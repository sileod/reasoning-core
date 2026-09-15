# P033v1 samples

## Level 0

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 2 | tb 3
  P0 | score 5 | tb 3
  P0 | score 5 | tb 3
  P0 | score 5 | tb 1

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P0 with score 5 and tb 1.

Compute the lag by 1 of the query row's score: the score of the immediately preceding item in the partition order, or empty if there is none. Answer with an integer, or write NONE if there is no preceding item.

**Answer:**

2

---

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 4 | tb 4
  P0 | score 3 | tb 2
  P0 | score 1 | tb 2
  P0 | score 3 | tb 3
  P0 | score 2 | tb 3

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P0 with score 2 and tb 3.

Compute the running total of score over items in the partition of the query row, cumulated in the order stated above, up to and including the query row. What is that running total? Answer with an integer.

**Answer:**

3

---

## Level 2

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 4 | tb 3
  P0 | score 5 | tb 6
  P0 | score 2 | tb 2
  P0 | score 6 | tb 5
  P0 | score 7 | tb 3
  P0 | score 6 | tb 3
  P1 | score 4 | tb 3
  P1 | score 4 | tb 7
  P1 | score 2 | tb 3
  P1 | score 5 | tb 7
  P1 | score 1 | tb 6
  P1 | score 5 | tb 6

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P1 with score 5 and tb 6.

Compute a window over the query row's partition consisting of the query row and the 2 rows immediately preceding it in the partition order (a frame of at most 3 rows). How many rows are in that window? Answer with a non-negative integer.

**Answer:**

3

---

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 1 | tb 3
  P0 | score 1 | tb 2
  P0 | score 4 | tb 6
  P0 | score 3 | tb 3
  P0 | score 2 | tb 5
  P0 | score 5 | tb 4
  P1 | score 3 | tb 6
  P1 | score 6 | tb 6
  P1 | score 1 | tb 7
  P1 | score 1 | tb 3
  P1 | score 3 | tb 1
  P1 | score 3 | tb 5

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P0 with score 5 and tb 4.

Compute the rank of the query row within its partition, ordered as stated above, using competition ranking (ties share the same rank and the next rank skips). What is the rank? Answer with an integer.

**Answer:**

6

---

## Level 5

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 5 | tb 6
  P0 | score 6 | tb 10
  P0 | score 10 | tb 8
  P0 | score 3 | tb 3
  P0 | score 8 | tb 2
  P0 | score 3 | tb 3
  P0 | score 7 | tb 3
  P0 | score 2 | tb 5
  P0 | score 1 | tb 5
  P1 | score 2 | tb 9
  P1 | score 10 | tb 9
  P1 | score 9 | tb 2
  P1 | score 1 | tb 4
  P1 | score 9 | tb 8
  P1 | score 5 | tb 5
  P1 | score 9 | tb 9
  P1 | score 3 | tb 3
  P2 | score 4 | tb 10
  P2 | score 9 | tb 1
  P2 | score 7 | tb 7
  P2 | score 8 | tb 2
  P2 | score 8 | tb 9
  P2 | score 9 | tb 10
  P2 | score 5 | tb 6
  P2 | score 9 | tb 3
  P2 | score 2 | tb 10
  P2 | score 2 | tb 9

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P2 with score 2 and tb 9.

Compute the running total of score over items in the partition of the query row, cumulated in the order stated above, up to and including the query row. What is that running total? Answer with an integer.

**Answer:**

2

---

**Prompt:**

Below is a table of items. Each item belongs to a partition (the part column), has a numeric score, and a secondary numeric tiebreak value tb.

Items:
  P0 | score 5 | tb 7
  P0 | score 10 | tb 2
  P0 | score 2 | tb 9
  P0 | score 4 | tb 2
  P0 | score 2 | tb 4
  P0 | score 6 | tb 1
  P0 | score 3 | tb 4
  P0 | score 6 | tb 5
  P1 | score 6 | tb 3
  P1 | score 8 | tb 6
  P1 | score 7 | tb 10
  P1 | score 4 | tb 8
  P1 | score 3 | tb 9
  P1 | score 9 | tb 6
  P1 | score 4 | tb 5
  P1 | score 5 | tb 6
  P1 | score 5 | tb 7
  P2 | score 7 | tb 5
  P2 | score 3 | tb 4
  P2 | score 9 | tb 8
  P2 | score 9 | tb 1
  P2 | score 5 | tb 4
  P2 | score 2 | tb 5
  P2 | score 8 | tb 9
  P2 | score 6 | tb 7
  P2 | score 2 | tb 8

Within each partition, items are ordered by score ascending, then tb ascending, then id ascending (ids P<i>_r<j> sort lexicographically). The query row is the item P0 with score 6 and tb 5.

Compute a window over the query row's partition consisting of the query row and the 3 rows immediately preceding it in the partition order (a frame of at most 4 rows). What is the sum of score over that window? Answer with an integer.

**Answer:**

21

---
