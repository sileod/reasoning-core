# samples_P002v2 - circular_digest_mapping

## Level 0

### Example 1

**Prompt:**

```
A circular DNA molecule has circumference 90 base pairs, with integer coordinates on [0, 90). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 2 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [9, 81] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 2 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [10, 80] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [9, 33, 10, 38].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A1 to cut site B0.
```

**Answer:**

```
33
```

### Example 2

**Prompt:**

```
A circular DNA molecule has circumference 90 base pairs, with integer coordinates on [0, 90). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 2 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [39, 51] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 2 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [40, 50] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [39, 8, 40, 3].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A1 to cut site B0.
```

**Answer:**

```
8
```

## Level 2

### Example 1

**Prompt:**

```
A circular DNA molecule has circumference 200 base pairs, with integer coordinates on [0, 200). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 4 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [67, 20, 78, 35] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 3 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [60, 9, 131] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [50, 17, 20, 23, 9, 46, 35].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A0 to cut site B2.
```

**Answer:**

```
119
```

### Example 2

**Prompt:**

```
A circular DNA molecule has circumference 200 base pairs, with integer coordinates on [0, 200). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 4 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [34, 37, 15, 114] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 3 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [5, 118, 77] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [26, 5, 3, 37, 15, 63, 51].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A3 to cut site B0.
```

**Answer:**

```
140
```

## Level 5

### Example 1

**Prompt:**

```
A circular DNA molecule has circumference 365 base pairs, with integer coordinates on [0, 365). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 6 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [41, 28, 18, 33, 93, 152] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 5 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [166, 19, 60, 50, 70] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [34, 7, 28, 18, 33, 80, 13, 6, 60, 50, 36].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A0 to cut site B0.
```

**Answer:**

```
34
```

### Example 2

**Prompt:**

```
A circular DNA molecule has circumference 365 base pairs, with integer coordinates on [0, 365). Two restriction enzymes cut it at distinct sites.
- Enzyme A cuts at 6 sites. Going clockwise from the A-cut site at coordinate 0, successive A-cut sites are separated by fragments: [59, 40, 12, 63, 1, 190] (in clockwise order). A-fragment i runs clockwise from A-cut site Ai to A-cut site A(i+1).
- Enzyme B cuts at 5 sites. Going clockwise from the B-cut site B0, successive B-cut sites are separated by fragments: [25, 60, 162, 16, 102] (clockwise order; the coordinate of B0 is to be determined). B-fragment i runs clockwise from B-cut site Bi to B-cut site B(i+1).
- Cutting with both enzymes, going clockwise from the cut site at coordinate 0 (which is an A-cut), the combined fragments are: [59, 37, 3, 12, 10, 53, 1, 6, 162, 16, 6].
Infer the map. Give the clockwise distance (an integer number of base pairs) from cut site A4 to cut site B3.
```

**Answer:**

```
169
```
