## Level 0

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=3   . * * *
y=2   . * . *
y=1   . * . *
y=0   . * * *
      0 1 2 3

The occupied cells are: {1,0, 1,1, 1,2, 1,3, 2,0, 2,3, 3,0, 3,1, 3,2, 3,3}.

A surgical procedure is planned: add a solid cell at (0,1), filling that empty grid position

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

1 1 0

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=3   * * * *
y=2   * . . *
y=1   * . . *
y=0   * * * *
      0 1 2 3

The occupied cells are: {0,0, 0,1, 0,2, 0,3, 1,0, 1,3, 2,0, 2,3, 3,0, 3,1, 3,2, 3,3}.

A surgical procedure is planned: drill a tunnel through the interior of the cell at (0,2)

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

1 1 0

## Level 2

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=5   * . . . . .
y=4   * . . . . .
y=3   * . . . . .
y=2   . . . . * *
y=1   . . . . * *
y=0   . . . . * *
      0 1 2 3 4 5

The occupied cells are: {0,3, 0,4, 0,5, 4,0, 4,1, 4,2, 5,0, 5,1, 5,2}.

A surgical procedure is planned: add a solid cell at (0,2), filling that empty grid position

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

2 0 0

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=5   . * * * . .
y=4   . * . * . .
y=3   . * . * . .
y=2   . * * * . .
y=1   . . . . . .
y=0   . . . . . .
      0 1 2 3 4 5

The occupied cells are: {1,2, 1,3, 1,4, 1,5, 2,2, 2,5, 3,2, 3,3, 3,4, 3,5}.

A surgical procedure is planned: excise the cell at (1,3), removing that unit of material together with its boundary edges

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

1 1 0

## Level 5

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=8   . * * . . . . . .
y=7   . * * . * * . . .
y=6   . * * . . . . . .
y=5   . . . . . . . . .
y=4   . . . . . . . . .
y=3   . . . * * . . . .
y=2   * * * . . . . . .
y=1   * . * . . . . . .
y=0   * * * . . . . . .
      0 1 2 3 4 5 6 7 8

The occupied cells are: {0,0, 0,1, 0,2, 1,0, 1,2, 1,6, 1,7, 1,8, 2,0, 2,1, 2,2, 2,6, 2,7, 2,8, 3,3, 4,3, 4,7, 5,7}.

A surgical procedure is planned: drill a tunnel through the interior of the cell at (4,7)

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

3 1 0

### Example

**Prompt:**

```
A cubical complex is given by its occupied unit cells (*) marked on the grid below. Coordinates are (x,y): x runs left to right, y runs bottom to top, and each row is labeled by its y value.

y=8   . . . . . . . . .
y=7   . . . . . . . . .
y=6   . . . . . . . * *
y=5   . . . . . . . * *
y=4   . * * * . . . . .
y=3   . * . * . . * * *
y=2   . * * * . . * . *
y=1   . . . . . . * . *
y=0   * * . . . . * * *
      0 1 2 3 4 5 6 7 8

The occupied cells are: {0,0, 1,0, 1,2, 1,3, 1,4, 2,2, 2,4, 3,2, 3,3, 3,4, 6,0, 6,1, 6,2, 6,3, 7,0, 7,3, 7,5, 7,6, 8,0, 8,1, 8,2, 8,3, 8,5, 8,6}.

A surgical procedure is planned: excise the cell at (3,2), removing that unit of material together with its boundary edges

Compute the homology of the complex as it stands BEFORE any surgical change. Report the triple (components, tunnels, cavities) as three integers separated by single spaces, e.g. '2 1 0'.
```

**Answer:**

4 2 0
