## Level 0

### Example 1

**Prompt:**

There are 5 elements {0, 1, 2, 3, 4} laid out on a line. A betweenness triple (a,b,c) states that b lies strictly between a and c in the line. You are given this list of betweenness triples: [(4,2,1), (0,4,2), (0,4,3), (4,2,3)]. Count how many distinct line orders of the 5 elements satisfy every one of these triples, where an order and its mirror image count as two different orders. Answer with a single integer, the count.

**Answer:**

4

### Example 2

**Prompt:**

There are 5 elements {0, 1, 2, 3, 4} on a line, where a betweenness triple (a,b,c) means b lies strictly between a and c. No single line order satisfies all of the given triples because they contradict one another: [(1,0,4), (1,2,4), (1,3,2), (2,0,4), (3,2,4), (1,3,4), (3,0,4), (3,2,0), (1,0,2)]. Scanning the triples in the order they are listed, report the first triple that, combined with the ones before it, makes the constraints impossible. Answer exactly as that triple in the form (a,b,c).

**Answer:**

(1,0,2)


## Level 2

### Example 1

**Prompt:**

There are 6 elements {0, 1, 2, 3, 4, 5} laid out on a line. A betweenness triple (a,b,c) states that b lies strictly between a and c in the line. You are given this list of betweenness triples: [(0,2,1), (3,0,1), (3,0,2), (0,5,1), (3,0,4)]. Count how many distinct line orders of the 6 elements satisfy every one of these triples, where an order and its mirror image count as two different orders. Answer with a single integer, the count.

**Answer:**

16

### Example 2

**Prompt:**

There are 6 elements {0, 1, 2, 3, 4, 5} arranged on a line, and a betweenness triple (a,b,c) means b lies strictly between a and c. The given triples pin the line order down to two mirror-image possibilities. Here they are: [(5,0,4), (1,2,0), (2,0,4), (5,1,4), (1,3,4), (1,0,4), (1,2,4), (5,1,2), (5,3,0), (5,3,4), (5,1,3), (3,0,4), (3,2,0), (1,3,2), (3,2,4), (5,2,4), (1,3,0), (5,1,0), (5,2,0), (5,3,2)]. Rebuild the line order and write it as a comma-separated list of the 6 integers, in the orientation that is lexicographically smallest among the two (i.e. the one starting with the smaller leading integer).

**Answer:**

4,0,2,3,1,5


## Level 5

### Example 1

**Prompt:**

There are 7 elements {0, 1, 2, 3, 4, 5, 6} laid out on a line. A betweenness triple (a,b,c) states that b lies strictly between a and c in the line. You are given this list of betweenness triples: [(3,5,4), (3,4,2), (3,5,6), (3,2,0), (3,4,1), (3,4,0), (4,2,6), (5,0,6), (3,5,2), (3,4,6), (3,2,1), (4,2,0), (5,2,1)]. Count how many distinct line orders of the 7 elements satisfy every one of these triples, where an order and its mirror image count as two different orders. Answer with a single integer, the count.

**Answer:**

6

### Example 2

**Prompt:**

There are 7 elements {0, 1, 2, 3, 4, 5, 6} arranged on a line, and a betweenness triple (a,b,c) means b lies strictly between a and c. The given triples pin the line order down to two mirror-image possibilities. Here they are: [(2,3,6), (5,4,1), (5,0,6), (5,1,6), (5,3,1), (5,0,1), (5,3,4), (2,0,6), (4,0,6), (3,0,1), (0,1,6), (2,3,1), (5,2,1), (5,2,3), (2,1,6), (4,1,6), (5,2,6), (3,4,1), (5,3,0), (2,4,6), (5,2,4), (5,4,6), (2,4,1), (5,2,0), (5,4,0), (3,0,6), (2,3,4), (2,3,0), (5,3,6), (3,1,6), (3,4,0), (4,0,1), (2,4,0)]. Rebuild the line order and write it as a comma-separated list of the 7 integers, in the orientation that is lexicographically smallest among the two (i.e. the one starting with the smaller leading integer).

**Answer:**

5,2,3,4,0,1,6

