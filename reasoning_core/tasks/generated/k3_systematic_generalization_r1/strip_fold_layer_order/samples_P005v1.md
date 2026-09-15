# Samples for P005v1: strip_fold_layer_order

Assigned design choice: Represent the strip as a list of segment labels, apply folds by reversing and flipping sublists, and output the final top-to-bottom labels as a comma-separated string.

Each example shows the generated prompt verbatim and its gold answer.

## Level 0

**Example 1**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 3, 2, 4, 1.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: mountain fold at cut position 1 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 1,4,2,3

**Example 2**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 1, 2, 3, 4.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: mountain fold at cut position 1 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 4,3,2,1

## Level 2

**Example 1**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 6, 7, 1, 5, 2, 3, 4, 8.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: mountain fold at cut position 3 (counting segments from the top).
    Fold 2: mountain fold at cut position 6 (counting segments from the top).
    Fold 3: valley fold at cut position 1 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 1,7,8,4,3,2,5,6

**Example 2**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 7, 8, 3, 5, 2, 6, 4, 1.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: mountain fold at cut position 3 (counting segments from the top).
    Fold 2: mountain fold at cut position 7 (counting segments from the top).
    Fold 3: valley fold at cut position 3 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 4,1,3,6,2,5,7,8

## Level 5

**Example 1**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 6, 9, 11, 3, 13, 12, 4, 14, 7, 5, 2, 10, 8, 1.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: valley fold at cut position 13 (counting segments from the top).
    Fold 2: mountain fold at cut position 4 (counting segments from the top).
    Fold 3: mountain fold at cut position 6 (counting segments from the top).
    Fold 4: valley fold at cut position 8 (counting segments from the top).
    Fold 5: mountain fold at cut position 9 (counting segments from the top).
    Fold 6: mountain fold at cut position 11 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 1,5,2,13,3,11,9,6,12,4,14,7,8,10

**Example 2**

Prompt:

    We have a one-dimensional strip of labeled segments placed side by side, flat at the bottom of a single stack, with layer order equal to the listed order (the first listed segment is on top).
    Initial segment order (top to bottom): 1, 12, 13, 4, 5, 11, 3, 2, 6, 9, 10, 7, 8, 14.
    Now apply folds, in order. A fold at cut position c divides the current strip (counting segments from the top) into a top part and a bottom part. Applying a mountain fold folds the bottom part up onto the top part; applying a valley fold folds the top part down onto the bottom part. The block that is folded on top is turned over, which reverses the order of its segments and mirrors the layers within each of its segments, so that it lands on top in that reversed order.
    Fold 1: mountain fold at cut position 11 (counting segments from the top).
    Fold 2: mountain fold at cut position 9 (counting segments from the top).
    Fold 3: mountain fold at cut position 4 (counting segments from the top).
    Fold 4: valley fold at cut position 8 (counting segments from the top).
    Fold 5: valley fold at cut position 12 (counting segments from the top).
    Fold 6: valley fold at cut position 12 (counting segments from the top).
    After all folds, report the segment labels from top to bottom. Answer with a comma-separated list of integers, no spaces.

Answer: 8,7,1,12,13,4,5,11,14,3,10,9,6,2
