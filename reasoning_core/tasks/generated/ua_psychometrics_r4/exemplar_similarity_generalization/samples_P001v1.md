## Level 0

**Example 1**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2
label B   3  1  1
label A   1  2  2
label B   1  0  2
label A   2  0  2

Feature weights (one per dimension, applied to every exemplar):
        1.2  0.9  0.6

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        0  0  2

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * max(0, 1 - |x - m| / 3).
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
A
```

**Example 2**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2
label B   3  1  0
label B   0  2  0
label A   3  2  0
label A   0  0  3

Feature weights (one per dimension, applied to every exemplar):
        1.5  1.5  1.5

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        3  0  0

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * max(0, 1 - |x - m| / 3).
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
B
```

## Level 2

**Example 1**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2  d3
label A   0  4  2  1
label B   0  1  1  2
label B   0  0  3  1
label A   2  2  3  4
label B   0  3  0  2
label A   2  3  4  3

Feature weights (one per dimension, applied to every exemplar):
        1.8  1  0.8  1.8

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        3  ?  1  3

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * 0.5^|x - m|.
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
A
```

**Example 2**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2  d3  d4
label A   2  1  3  2  2
label A   3  1  2  3  1
label B   2  3  2  1  4
label B   0  2  3  3  2
label B   3  2  1  1  3
label A   2  4  4  1  4

Feature weights (one per dimension, applied to every exemplar):
        1.6  1.3  1.2  1.1  1.3

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        ?  4  0  3  1

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * 0.5^|x - m|.
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
A
```

## Level 5

**Example 1**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2  d3  d4  d5  d6
label B   6  4  6  3  6  0  6
label B   5  4  1  5  3  0  7
label B   7  5  4  7  7  3  1
label B   5  0  4  6  2  0  6
label B   5  2  5  2  5  5  3
label A   7  5  0  3  0  2  0
label A   6  4  3  2  1  1  0
label A   4  7  1  5  3  6  1
label A   4  5  1  1  1  5  1
label A   6  2  3  3  7  0  6

Feature weights (one per dimension, applied to every exemplar):
        1.2  1.2  1.3  0.6  2.6  2.6  2.3

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        4  ?  ?  7  5  ?  2

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * max(0, 1 - |x - m| / 7).
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
B
```

**Example 2**

Prompt:
```
Remembered exemplars:
dim     d0  d1  d2  d3  d4  d5  d6
label B   0  0  4  4  3  5  5
label A   1  4  1  2  4  6  1
label B   4  6  0  5  0  0  0
label B   3  0  6  6  1  1  4
label A   3  6  1  3  6  6  5
label A   1  5  3  4  0  2  2
label B   2  0  4  5  4  4  5
label A   4  1  3  5  2  6  0

Feature weights (one per dimension, applied to every exemplar):
        0.6  2  1.9  1.9  2.4  2  1.7

Novel stimulus (a '?' marks a dimension whose value was not observed, so it is skipped):
        5  4  6  ?  ?  ?  0

Similarity kernel: For an observed dimension d with exemplar value m and stimulus value x, its similarity contribution is weight_d * 0.5^|x - m|.
Sum an exemplar's contributions over observed dimensions to get its similarity to the stimulus.
Category score = the summed similarity of ALL exemplars of that category.
Classify the stimulus into the category with the higher summed score; on a tie, choose A.
Give only the winning category label.
```

Answer:
```
A
```

