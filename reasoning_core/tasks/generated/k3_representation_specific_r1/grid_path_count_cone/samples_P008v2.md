## Level 0
### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with right/down moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 4 rows by 4 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (3, 3).

. . . .
# . # .
. . . .
. . . .

Now an obstacle is placed at cell (2, 1): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
2,1;2,2;2,3;3,1;3,2;3,3|1

### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with knight (monotone) moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 4 rows by 4 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (3, 3).

. . # .
. . # #
. . . #
# . # .

Now the obstacle at cell (1, 2): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
1,2;3,3|2

## Level 2
### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with knight (monotone) moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 4 rows by 4 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (3, 3).

. . . #
# . . .
. # . .
. # # .

Now the obstacle at cell (2, 1): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
2,1;3,3|2

### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with knight (monotone) moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 4 rows by 4 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (3, 3).

. . . #
. . . #
# . . #
. . . .

Now an obstacle is placed at cell (1, 2): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
1,2;3,3|1

## Level 5
### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with knight (monotone) moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 7 rows by 7 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (6, 6).

. # # # # # #
# . . . # # .
. . # # # # .
. . . . . . #
. # # . # . #
. . . # . . #
. # # . . . .

Now an obstacle is placed at cell (2, 1): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
2,1;3,3;4,5;5,4;6,6|2

### Prompt
A robot starts at the top-left (row 0, column 0) and moves on a grid with right/down moves. It can step to any of the cells its move set allows, staying inside the grid and never landing on an obstacle (#). A monotone path is a sequence of allowed steps that is non-decreasing in both row and column. The count at a cell is the number of distinct monotone paths from the start to that cell.

The grid is 7 rows by 7 columns ('.' is open, '#' is an obstacle), rows and columns indexed from 0. The target corner is the bottom-right cell (6, 6).

. . # # # . .
. # # . # . .
. . # # . . #
. . . . . . .
. # . # . . #
. . # # . . .
. . # . . . .

Now the obstacle at cell (4, 6): a single obstacle is toggled (turned off if it was on, on if it was off). All other cells are unchanged.
List every cell (row, col) in reading order (row by row, left to right) whose path count changes, separated by ';', followed by '|' and the new path count at the target corner. For example '2,3;4,5|17'.

### Answer
4,6;5,6;6,6|20

