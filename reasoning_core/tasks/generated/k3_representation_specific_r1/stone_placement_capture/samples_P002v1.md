## Level 0
### Example 1
**Prompt:**
Consider a 9x9 Go board. Black stones are 1, white stones are 2, empty points are 0.
1 0 0 0 0 0 0 0 0
0 0 2 0 0 0 0 1 0
0 0 2 1 2 0 0 0 0
0 0 1 0 1 0 0 0 2
0 1 1 1 1 0 0 0 2
1 1 1 1 1 0 1 2 0
1 2 2 2 2 0 0 0 2
1 1 1 1 1 2 2 0 1
0 0 0 0 2 0 1 0 0
Black (black) plays a stone at row 6, column 5. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=4; released=9; adj2=3

### Example 2
**Prompt:**
Consider a 9x9 Go board. Black stones are 1, white stones are 2, empty points are 0.
0 1 1 1 1 0 0 0 0
1 2 2 2 2 0 0 2 0
1 2 2 2 2 1 0 2 1
2 1 1 1 1 0 0 1 0
0 0 0 0 0 0 1 2 0
1 0 1 0 2 0 0 0 1
0 0 0 1 0 2 2 0 1
2 1 1 1 1 0 0 0 0
0 2 2 0 2 0 0 1 0
Black (black) plays a stone at row 1, column 5. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=8; released=11; adj1=6

## Level 2
### Example 1
**Prompt:**
Consider a 13x13 Go board. Black stones are 1, white stones are 2, empty points are 0.
0 0 0 2 0 0 0 0 0 1 0 2 0
0 0 0 0 2 0 2 2 0 2 0 2 0
2 0 0 0 0 0 1 2 1 0 1 2 2
2 0 1 0 1 0 1 0 0 1 0 0 0
1 1 1 0 1 1 1 1 0 2 0 2 0
0 0 0 1 2 2 2 2 1 0 0 0 1
0 0 2 1 2 2 2 2 0 0 0 0 2
0 1 0 1 2 2 2 2 1 0 0 0 0
0 0 0 1 2 2 2 2 1 1 1 0 1
0 2 0 0 1 1 1 1 0 2 0 0 0
0 2 2 0 1 0 0 0 2 0 0 0 0
2 2 0 0 0 2 0 1 2 0 0 0 0
0 2 1 1 1 2 0 0 2 1 0 0 0
Black (black) plays a stone at row 6, column 8. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=16; released=15; adj1=12

### Example 2
**Prompt:**
Consider a 13x13 Go board. Black stones are 1, white stones are 2, empty points are 0.
0 0 0 0 0 2 1 0 0 2 0 1 0
0 0 2 0 0 1 1 0 0 0 2 2 1
2 2 1 1 0 0 2 0 0 0 0 0 1
2 1 0 0 0 0 0 0 0 0 0 0 0
0 1 0 2 0 0 0 1 0 2 0 0 0
0 0 0 1 0 1 2 0 0 2 1 0 0
0 1 0 0 0 0 0 0 1 0 0 1 0
0 0 1 1 1 1 2 1 0 0 0 2 0
0 1 2 2 2 1 1 1 0 0 1 0 2
0 1 2 2 2 1 2 0 0 0 2 0 1
1 0 2 2 2 1 0 0 0 0 0 0 0
1 0 1 1 1 0 0 1 0 0 0 0 0
0 0 0 2 1 1 0 0 0 1 2 1 0
Black (black) plays a stone at row 10, column 1. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=9; released=11; adj1=8

## Level 5
### Example 1
**Prompt:**
Consider a 19x19 Go board. Black stones are 1, white stones are 2, empty points are 0.
0 1 0 2 0 0 1 2 2 0 0 2 0 0 1 0 0 0 2
0 0 1 0 1 0 1 2 2 1 2 0 0 0 0 0 0 0 0
0 0 2 2 1 2 1 2 2 1 0 2 0 0 2 0 1 0 2
1 0 0 0 0 1 1 2 2 1 0 2 1 0 0 0 2 0 0
0 0 0 2 0 0 1 2 2 1 0 0 0 0 1 0 0 0 0
0 0 0 0 1 2 1 2 2 1 1 0 0 2 0 0 1 1 0
0 1 2 0 0 0 1 1 1 0 0 0 1 2 0 1 1 0 0
0 1 0 0 2 0 0 0 0 0 2 0 2 0 2 2 0 0 2
0 0 0 2 0 0 2 0 0 0 0 0 1 0 0 0 0 0 2
0 2 0 0 0 2 0 2 0 0 0 0 2 0 0 0 0 0 2
0 0 1 0 2 0 0 1 0 0 0 2 2 0 0 0 2 0 2
2 0 2 2 1 0 0 0 0 1 0 0 2 0 0 0 0 0 0
2 1 1 0 0 1 0 0 1 0 1 0 0 0 0 0 0 2 0
0 0 0 2 2 0 0 0 2 0 1 0 0 2 2 0 0 1 0
1 2 0 0 0 0 0 0 0 0 1 0 1 0 0 0 2 0 0
1 0 1 2 2 0 1 0 0 0 1 0 0 1 2 0 0 0 0
0 0 1 2 1 0 0 0 0 0 0 2 0 0 0 0 0 1 0
0 2 0 0 0 0 1 0 1 0 0 0 2 2 0 0 2 0 0
2 0 2 0 0 2 0 0 0 0 0 0 0 0 2 0 2 0 0
Black (black) plays a stone at row 0, column 9. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=12; released=13; adj1=13

### Example 2
**Prompt:**
Consider a 19x19 Go board. Black stones are 1, white stones are 2, empty points are 0.
0 0 0 0 0 1 2 1 0 0 0 2 0 0 2 0 1 1 1
0 0 0 0 2 0 0 0 0 1 2 1 0 0 0 2 0 0 0
0 1 1 0 0 0 0 0 0 0 0 2 2 0 0 0 2 0 0
0 0 1 0 1 1 1 0 0 0 2 2 1 1 0 0 0 2 0
1 0 1 1 1 1 1 1 1 2 0 0 0 0 0 0 0 0 1
0 0 0 2 2 2 2 2 2 1 0 0 0 0 0 0 0 0 0
0 0 1 2 2 2 2 2 2 1 0 0 0 1 2 0 0 0 0
1 0 1 1 1 1 1 1 1 0 2 0 0 0 1 0 1 1 0
0 1 2 2 0 0 0 0 0 0 0 0 2 1 0 0 2 0 0
0 2 2 0 0 0 1 2 2 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 2 0 1 0 1 0 0 0 2 0 0 2 2
0 2 0 0 0 0 0 0 0 2 0 2 1 1 1 0 1 0 0
0 1 1 0 0 2 0 0 0 2 0 1 2 0 2 0 0 1 0
1 1 0 0 2 0 1 0 1 0 0 1 0 1 1 2 0 1 0
2 1 0 1 0 2 0 0 0 0 0 0 0 0 0 1 2 1 0
0 0 0 0 0 0 0 1 0 0 0 0 0 0 2 2 0 0 0
1 0 2 1 0 0 0 0 0 0 0 1 2 1 0 0 0 0 1
0 0 0 0 1 0 0 2 0 1 0 0 0 0 0 0 0 2 0
0 0 0 0 0 1 0 2 0 0 0 0 0 1 0 0 2 1 1
Black (black) plays a stone at row 5, column 2. Under Go rules a captured group is removed and its liberties released. Report, in this order: captured=N and released=N for the number of stones captured and the number of liberties released (omit any that are 0), then adj1=L and adj2=L for the number of liberties of each color's stones adjacent to the played stone after resolution. Omit adj entries with no adjacent stones of that color.

**Answer:**
captured=12; released=15; adj1=33
