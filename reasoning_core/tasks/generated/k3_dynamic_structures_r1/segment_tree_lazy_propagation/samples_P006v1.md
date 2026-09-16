# Level 0
## Example
The array has size 5 with 1-based inclusive intervals.
Initial: [15, -14, -16, -4, -1]
Apply range-set of -14 to [2,3].
Query range-sum on [3,3].
Apply range-set of -13 to [2,2].
Query range-min on [3,3].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-14;-14

## Example
The array has size 5 with 1-based inclusive intervals.
Initial: [-2, 10, -7, -10, -5]
Apply range-set of -11 to [2,4].
Query range-sum on [1,1].
Apply range-set of 8 to [1,3].
Query range-sum on [5,5].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-2;-5


# Level 2
## Example
The array has size 9 with 1-based inclusive intervals.
Initial: [-15, 17, -3, -16, 7, 5, 15, 10, 0]
Apply range-set of -19 to [2,9].
Query range-min on [5,9].
Apply range-set of 14 to [6,8].
Apply range-add of 15 to [4,4].
Query range-min on [4,9].
Apply range-add of 20 to [8,8].
Query range-sum on [1,5].
Apply range-set of 0 to [1,7].
Apply range-add of -6 to [2,5].
Query range-sum on [9,9].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-19;-19;-76;-19

## Example
The array has size 9 with 1-based inclusive intervals.
Initial: [6, 14, 10, 12, -3, 13, -19, 2, 14]
Apply range-add of 7 to [8,9].
Apply range-add of 2 to [9,9].
Query range-min on [2,6].
Apply range-set of 18 to [8,8].
Query range-sum on [5,5].
Apply range-set of 19 to [7,9].
Query range-sum on [3,4].
Apply range-add of 13 to [8,8].
Apply range-set of 5 to [7,9].
Apply range-set of 13 to [1,7].
Query range-sum on [9,9].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-3;-3;22;5


# Level 5
## Example
The array has size 15 with 1-based inclusive intervals.
Initial: [12, -19, 16, -4, 8, 17, -4, 13, 15, -3, 10, 11, -6, -14, -2]
Apply range-add of -20 to [15,15].
Query range-sum on [15,15].
Apply range-add of -1 to [9,11].
Query range-min on [3,4].
Apply range-add of 18 to [4,7].
Query range-sum on [4,4].
Apply range-set of -15 to [10,14].
Apply range-add of 11 to [4,15].
Apply range-add of -1 to [9,9].
Query range-sum on [11,11].
Apply range-add of -7 to [4,12].
Query range-sum on [12,15].
Apply range-set of 8 to [11,15].
Apply range-set of 0 to [13,14].
Query range-sum on [12,12].
Apply range-set of 8 to [7,13].
Query range-min on [15,15].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-22;-4;14;-4;-30;8;8

## Example
The array has size 15 with 1-based inclusive intervals.
Initial: [16, 13, -4, -6, 19, 11, 15, 6, -20, -12, -2, -13, 3, -2, -19]
Apply range-add of -14 to [5,12].
Query range-min on [1,7].
Apply range-set of 14 to [5,6].
Apply range-add of 4 to [12,14].
Query range-sum on [1,12].
Apply range-set of -10 to [5,10].
Apply range-set of -17 to [5,12].
Query range-sum on [13,15].
Apply range-set of 3 to [8,11].
Apply range-set of 13 to [5,8].
Query range-sum on [13,15].
Apply range-add of 11 to [13,15].
Apply range-add of -4 to [11,14].
Apply range-set of -19 to [10,15].
Query range-sum on [12,14].
Apply range-set of -15 to [12,15].
Apply range-set of -12 to [2,7].
Apply range-add of -3 to [6,14].
Query range-sum on [5,9].
Apply range-set of -14 to [10,12].
Query range-sum on [10,10].
Answer is a single integer per query, in query order, separated by semicolons.
Answer:
-6;-59;-10;-10;-57;-32;-14


