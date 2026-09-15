# Level 0

**Prompt:**

```
Using single linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..2, entry (i,j) is d(i,j), d(i,i)=0.
0 5 3
5 0 12
3 12 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the minimum of the two distances to that cluster. Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(0, 2, '3'), (0, 1, '5')]
```

**Prompt:**

```
Using single linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..2, entry (i,j) is d(i,j), d(i,i)=0.
0 10 5
10 0 12
5 12 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the minimum of the two distances to that cluster. Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(0, 2, '5'), (0, 1, '10')]
```

# Level 2

**Prompt:**

```
Using average linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..2, entry (i,j) is d(i,j), d(i,i)=0.
0 5 3
5 0 12
3 12 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the size-weighted mean of the two distances to that cluster (UPGMA). Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(0, 2, '3'), (0, 1, '17/2')]
```

**Prompt:**

```
Using average linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..4, entry (i,j) is d(i,j), d(i,i)=0.
0 4 5 10 11
4 0 11 12 5
5 11 0 5 11
10 12 5 0 8
11 5 11 8 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the size-weighted mean of the two distances to that cluster (UPGMA). Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(0, 1, '4'), (2, 3, '5'), (0, 4, '8'), (0, 2, '19/2')]
```

# Level 5

**Prompt:**

```
Using complete linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..5, entry (i,j) is d(i,j), d(i,i)=0.
0 12 3 8 1 5
12 0 5 11 9 12
3 5 0 1 4 11
8 11 1 0 2 8
1 9 4 2 0 5
5 12 11 8 5 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the maximum of the two distances to that cluster. Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(0, 4, '1'), (2, 3, '1'), (0, 5, '5'), (0, 2, '11'), (0, 1, '12')]
```

**Prompt:**

```
Using complete linkage agglomerative hierarchical clustering, cluster these points by their distance matrix: rows are points 0..2, entry (i,j) is d(i,j), d(i,i)=0.
0 11 9
11 0 1
9 1 0

Repeatedly merge the two current clusters with the smallest linkage distance; after merging, replace them by one cluster whose index is the smallest original index among their members, and recompute its distance to every other cluster as the maximum of the two distances to that cluster. Report every merge as a tuple (i,j,height) in merge order, with i<j the two cluster indices being merged at that step. Give each height as a fully reduced fraction (e.g. 3/2); integers as themselves (e.g. 4). Output only the list of tuples, in order.
```

**Answer:**

```
[(1, 2, '1'), (0, 1, '11')]
```
