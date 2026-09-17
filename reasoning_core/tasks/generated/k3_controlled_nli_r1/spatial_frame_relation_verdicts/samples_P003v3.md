# P003v3 samples

## Level 0

### Example 1

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
Cedar: parent map; offset (0, 1); turns 0.
Elm: parent map; offset (-4, 0); turns 0.
Birch: parent map; offset (3, -2); turns 0.
Birch is the observer. Evaluate: 'Elm is behind Cedar'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
Give yes/no verdicts in intrinsic, relative, absolute order, separated by spaces. Format example: yes no yes.
```

**Answer:**
```
yes yes yes
```

### Example 2

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
Elm: parent map; offset (2, 1); turns 3.
Cedar: parent map; offset (-3, -3); turns 0.
Hazel: parent map; offset (-1, 0); turns 2.
Cedar is the observer. Evaluate: 'Hazel is in front of Elm'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
List exactly the frames making the claim true, in intrinsic, relative, absolute order, comma-separated; use none if no frame does. Format example: intrinsic, absolute.
```

**Answer:**
```
intrinsic
```

## Level 2

### Example 1

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
plate1: parent map; offset (-2, -6); turns 1.
plate2: parent plate1; offset (6, -3); turns 0.
Hazel: parent plate2; offset (-10, 10); turns 2.
Dahlia: parent plate1; offset (-2, 6); turns 1.
Elm: parent plate1; offset (0, -3); turns 0.
Elm is the observer. Evaluate: 'Hazel is left of Dahlia'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
Give yes/no verdicts in intrinsic, relative, absolute order, separated by spaces. Format example: yes no yes.
```

**Answer:**
```
yes yes no
```

### Example 2

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
plate1: parent map; offset (6, -3); turns 2.
plate2: parent plate1; offset (-1, 4); turns 2.
Aster: parent plate1; offset (10, 2); turns 2.
Hazel: parent plate1; offset (9, -4); turns 1.
Iris: parent plate1; offset (10, -6); turns 0.
Aster is the observer. Evaluate: 'Iris is in front of Hazel'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
List exactly the frames making the claim true, in intrinsic, relative, absolute order, comma-separated; use none if no frame does. Format example: intrinsic, absolute.
```

**Answer:**
```
intrinsic, relative, absolute
```

## Level 5

### Example 1

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
plate1: parent map; offset (-5, -8); turns 3.
plate2: parent plate1; offset (-3, -5); turns 3.
plate3: parent plate2; offset (-2, -5); turns 2.
plate4: parent plate3; offset (-5, -9); turns 2.
plate5: parent plate4; offset (1, 7); turns 0.
Hazel: parent plate4; offset (2, -24); turns 3.
Iris: parent plate5; offset (5, -28); turns 2.
Dahlia: parent plate4; offset (1, -16); turns 3.
Iris is the observer. Evaluate: 'Dahlia is behind Hazel'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
Give yes/no verdicts in intrinsic, relative, absolute order, separated by spaces. Format example: yes no yes.
```

**Answer:**
```
no yes yes
```

### Example 2

**Prompt:**
```
A stage map has east as +x and north as +y. All objects are treated as points.
The map pose is (0, 0), facing north. Each pose below gives its position as (right, forward) offsets in its parent pose, and its facing as a number of clockwise quarter-turns from the parent facing. These are fixed nested poses, not successive movements. Compose the coordinate transforms from the map outward.
plate1: parent map; offset (7, 6); turns 3.
plate2: parent plate1; offset (-4, 6); turns 1.
plate3: parent plate2; offset (-9, -6); turns 0.
plate4: parent plate3; offset (6, 6); turns 0.
plate5: parent plate4; offset (-1, 8); turns 1.
Hazel: parent plate5; offset (-3, 4); turns 0.
Aster: parent plate5; offset (1, -3); turns 2.
Birch: parent plate4; offset (8, -11); turns 2.
Birch is the observer. Evaluate: 'Hazel is behind Aster'.
Use the displacement from the reference (second named object) to the subject. The front axis is the reference facing for intrinsic, the observer facing for relative, and north for absolute. In every frame, right is 90 degrees clockwise from front; left and behind are the opposites of right and front. A claim is true exactly when the displacement has a strictly positive dot product with its named axis; zero is false. Other components and distances do not matter. Observer position does not change the axes.
List exactly the frames making the claim true, in intrinsic, relative, absolute order, comma-separated; use none if no frame does. Format example: intrinsic, absolute.
```

**Answer:**
```
intrinsic, relative
```
