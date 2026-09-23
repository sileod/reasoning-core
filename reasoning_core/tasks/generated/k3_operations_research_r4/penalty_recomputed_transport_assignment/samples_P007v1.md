## Level 0

### Example 1
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [9, 2, 9]. Column demands: [1, 14, 5]. Cost matrix (row, column):
2, 8, 6;
2, 7, 4;
1, 2, 6
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:0=1;0:1=5;0:2=3;1:2=2;2:1=9`

### Example 2
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [7, 4, 9]. Column demands: [5, 12, 3]. Cost matrix (row, column):
5, 3, 9;
9, 7, 6;
8, 4, 5
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:0=5;0:1=2;1:1=1;1:2=3;2:1=9`
## Level 2

### Example 1
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [11, 5, 9, 7, 5, 2, 11]. Column demands: [10, 2, 2, 1, 6, 20, 9]. Cost matrix (row, column):
6, 7, 2, 8, 6, 9, 12;
6, 1, 7, 4, 12, 6, 10;
7, 11, 10, 2, 2, 10, 12;
5, 3, 1, 2, 8, 10, 8;
13, 9, 4, 4, 10, 9, 3;
12, 13, 8, 12, 13, 4, 5;
1, 12, 10, 11, 3, 8, 5
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:2=2;0:5=9;1:1=2;1:5=3;2:4=6;2:5=3;3:3=1;3:5=3;3:6=3;4:6=5;5:5=2;6:0=10;6:6=1`

### Example 2
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [3, 7, 1, 2, 26, 3, 8]. Column demands: [8, 5, 5, 3, 11, 6, 12]. Cost matrix (row, column):
10, 7, 6, 10, 4, 5, 5;
13, 13, 6, 10, 13, 5, 11;
1, 1, 13, 9, 10, 9, 4;
5, 1, 9, 5, 7, 6, 10;
3, 11, 10, 1, 8, 2, 12;
9, 3, 4, 12, 5, 5, 11;
4, 2, 9, 9, 8, 7, 12
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:6=3;1:2=5;1:6=2;2:6=1;3:1=2;4:0=8;4:3=3;4:4=3;4:5=6;4:6=6;5:4=3;6:1=3;6:4=5`
## Level 5

### Example 1
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [4, 5, 1, 10, 7, 21, 14, 16, 4, 2, 3, 3, 5]. Column demands: [9, 8, 5, 6, 15, 5, 1, 2, 2, 6, 8, 5, 23]. Cost matrix (row, column):
8, 11, 1, 7, 6, 11, 3, 9, 12, 9, 5, 2, 2;
11, 3, 4, 4, 7, 7, 9, 16, 2, 11, 10, 14, 16;
16, 7, 10, 13, 9, 9, 5, 3, 12, 13, 11, 12, 12;
5, 19, 8, 12, 19, 2, 8, 2, 9, 11, 18, 8, 8;
5, 2, 10, 1, 16, 9, 5, 19, 8, 18, 12, 17, 16;
1, 15, 18, 14, 1, 19, 14, 8, 5, 7, 2, 14, 5;
17, 1, 3, 17, 11, 13, 3, 5, 17, 13, 16, 10, 13;
10, 18, 2, 16, 12, 3, 2, 6, 16, 13, 6, 1, 11;
4, 11, 17, 10, 7, 3, 3, 11, 1, 1, 18, 11, 16;
1, 17, 15, 19, 1, 4, 9, 3, 7, 8, 9, 2, 6;
10, 5, 16, 18, 11, 4, 16, 1, 8, 10, 10, 9, 10;
1, 3, 18, 1, 8, 4, 12, 11, 18, 10, 4, 17, 3;
13, 15, 9, 11, 16, 11, 3, 16, 5, 19, 3, 1, 3
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:12=4;1:4=3;1:8=2;2:6=1;3:0=5;3:5=5;4:0=1;4:3=6;5:10=8;5:12=13;6:1=7;6:4=7;7:0=3;7:2=5;7:4=3;7:9=2;7:12=3;8:9=4;9:4=2;10:1=1;10:7=2;11:12=3;12:11=5`

### Example 2
**Prompt:**

A transportation problem has supply per origin row and demand per destination column, with a cost matrix where row i, column j is the per-unit cost. Row supplies: [15, 1, 14, 5, 2, 7, 1, 1, 2, 8, 4, 10, 25]. Column demands: [2, 1, 18, 2, 11, 9, 2, 11, 15, 9, 1, 9, 5]. Cost matrix (row, column):
13, 8, 19, 11, 3, 18, 10, 17, 16, 13, 4, 13, 8;
18, 13, 6, 11, 4, 14, 5, 1, 8, 14, 1, 17, 14;
9, 9, 18, 9, 1, 7, 10, 5, 10, 14, 8, 11, 8;
10, 3, 10, 6, 7, 4, 18, 17, 13, 1, 18, 4, 12;
5, 19, 13, 17, 19, 3, 5, 12, 13, 2, 13, 1, 7;
12, 6, 5, 5, 1, 7, 12, 17, 9, 16, 1, 2, 5;
9, 19, 9, 9, 16, 3, 12, 4, 4, 10, 8, 7, 11;
14, 8, 13, 18, 12, 15, 2, 13, 17, 7, 5, 6, 8;
15, 5, 13, 1, 17, 5, 13, 18, 7, 19, 18, 13, 3;
5, 13, 18, 14, 16, 8, 6, 4, 13, 8, 4, 6, 4;
12, 17, 2, 9, 9, 12, 9, 5, 8, 17, 18, 15, 3;
7, 11, 14, 17, 5, 13, 3, 1, 1, 4, 2, 10, 7;
14, 6, 15, 5, 18, 1, 19, 14, 18, 17, 14, 12, 7
Run Vogel's Approximation Method (VAM): at each round compute, for each remaining line, the penalty as the difference between its two smallest costs among remaining lines, commit the line with the largest penalty by saturating its cheapest remaining cell, reduce supply/demand, and remove exhausted lines; tie-break any equal penalties by larger line index, then by cheaper cell cost, then by larger opposite index. Continue until supply and demand are exhausted.
Output the allocation map as a semicolon-separated list of 'row:col=amount' entries sorted by row then column. Example format: '0:1=5;1:0=3;2:2=7'.

**Answer:** `0:0=1;0:7=3;0:8=4;0:9=4;0:10=1;0:11=2;1:7=1;2:4=11;2:7=3;3:9=5;4:0=1;4:6=1;5:11=7;6:8=1;7:6=1;8:3=2;9:7=3;9:12=5;10:2=4;11:8=10;12:1=1;12:2=14;12:5=9;12:7=1`
