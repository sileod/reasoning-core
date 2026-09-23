# samples_P011v1

## Level 0

### Example 1

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 14.
Customer 0 has demand 2 at (16, 9).
Customer 1 has demand 5 at (-1, -11).
Customer 2 has demand 2 at (19, -3).
Customer 3 has demand 1 at (7, -15).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
0-2-3-1
```

### Example 2

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 14.
Customer 0 has demand 1 at (12, 11).
Customer 1 has demand 2 at (-6, 15).
Customer 2 has demand 5 at (-7, 15).
Customer 3 has demand 3 at (-15, -14).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
0-1-2-3
```

## Level 2

### Example 1

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 20.
Customer 0 has demand 1 at (33, 30).
Customer 1 has demand 5 at (13, 17).
Customer 2 has demand 7 at (-32, 4).
Customer 3 has demand 7 at (13, -36).
Customer 4 has demand 3 at (-11, -4).
Customer 5 has demand 7 at (20, 14).
Customer 6 has demand 3 at (34, 36).
Customer 7 has demand 6 at (-5, 26).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
5-0-6-1 | 7-2-4 | 3
```

### Example 2

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 20.
Customer 0 has demand 3 at (-5, 13).
Customer 1 has demand 2 at (16, 2).
Customer 2 has demand 6 at (12, 10).
Customer 3 has demand 3 at (25, -23).
Customer 4 has demand 6 at (13, -7).
Customer 5 has demand 6 at (16, -14).
Customer 6 has demand 5 at (33, 24).
Customer 7 has demand 3 at (21, -14).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
0-2-6-1 | 5-3-7-4
```

## Level 5

### Example 1

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 29.
Customer 0 has demand 2 at (-30, 42).
Customer 1 has demand 1 at (-34, -21).
Customer 2 has demand 1 at (-29, 42).
Customer 3 has demand 3 at (-23, 41).
Customer 4 has demand 3 at (-18, -48).
Customer 5 has demand 9 at (-47, 17).
Customer 6 has demand 3 at (-33, -32).
Customer 7 has demand 4 at (-4, 38).
Customer 8 has demand 2 at (21, -19).
Customer 9 has demand 8 at (-53, -1).
Customer 10 has demand 5 at (15, 15).
Customer 11 has demand 5 at (40, -46).
Customer 12 has demand 10 at (21, 1).
Customer 13 has demand 9 at (54, -5).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
0-2-3-7-10 | 4-6-1-9-5 | 8-11-13-12
```

### Example 2

**Prompt:**

```
A depot sits at the origin (0, 0).
Vehicle capacity is 29.
Customer 0 has demand 6 at (-15, 60).
Customer 1 has demand 3 at (-4, -51).
Customer 2 has demand 9 at (12, -10).
Customer 3 has demand 4 at (-7, -4).
Customer 4 has demand 4 at (-21, 0).
Customer 5 has demand 7 at (-23, -52).
Customer 6 has demand 5 at (-20, -60).
Customer 7 has demand 8 at (-2, 19).
Customer 8 has demand 2 at (58, 2).
Customer 9 has demand 1 at (47, 10).
Customer 10 has demand 2 at (24, 24).
Customer 11 has demand 5 at (16, 23).
Customer 12 has demand 9 at (-50, 26).
Customer 13 has demand 7 at (12, 35).

Begin with one single-customer route per customer. Repeatedly consider all remaining pairs of routes in decreasing order of the savings d(0,i)+d(0,j)-d(i,j) where i is one endpoint of the first route and j one endpoint of the second route; use the pair giving the largest such savings (ties broken by smaller first-id then smaller second-id of the two routes, then shorter first route, then shorter second route), flip route orientations as needed so the two endpoints meet, and join the routes end-to-end whenever the sum of their demands does not exceed capacity; skip a pair whose combined demand exceeds capacity. Stop when no capacity-feasible pair improves by merging. Give the final routes as ordered customer-ID sequences: IDs joined by '-' in travel order, routes separated by ' | ', e.g. '1-2-3 | 0'.
```

**Answer:**

```
13-0-12-4 | 1-6-5-3 | 2-8-9-10-11-7
```
