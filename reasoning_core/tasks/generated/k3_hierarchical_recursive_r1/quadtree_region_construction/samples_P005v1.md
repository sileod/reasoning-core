## Level 0
### Prompt
```
Consider the 2x2 binary grid below, where '#' is black (occupied) and '.' is white (empty):
..
#.

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GWWBW
```
### Prompt
```
Consider the 2x2 binary grid below, where '#' is black (occupied) and '.' is white (empty):
#.
#.

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GBWBW
```
## Level 2
### Prompt
```
Consider the 8x8 binary grid below, where '#' is black (occupied) and '.' is white (empty):
.....###
.#######
.####.#.
.#####.#
.####..#
.#######
.#######
.##.####

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GGGWWWBGWWBBGWBWBBGGWBBBBGBWBBGBWWBGGWBWBBGWBWBGBBBWGGBWBBGWBBBBB
```
### Prompt
```
Consider the 4x4 binary grid below, where '#' is black (occupied) and '.' is white (empty):
###.
#..#
..##
...#

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GGBBBWGBWWBWGBBWB
```
## Level 5
### Prompt
```
Consider the 8x8 binary grid below, where '#' is black (occupied) and '.' is white (empty):
........
.......#
....####
.####...
.###..#.
..#####.
...####.
....#..#

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GGWWGWWWBGWWBBGWGWWWBGBBBWGBBWWGGWBWWBWGWBWWGGWWBBGBWBWGBBBWGBWWB
```
### Prompt
```
Consider the 8x8 binary grid below, where '#' is black (occupied) and '.' is white (empty):
...###..
...###..
...###..
........
##......
........
..##....
..##....

Build its region quadtree by recursively subdividing the square into four equal quadrants (top-left, top-right, bottom-left, bottom-right). A quadrant that is entirely black encodes as 'B', entirely white encodes as 'W', and a mixed quadrant encodes as 'G' followed by the encodings of its four children in order, recursing down to single cells. The whole grid is always non-uniform, so its root is 'G'. Give the pre-order string encoding of the root quadtree (W and B are always leaves; G always has exactly four children). The answer is just the token string.
```
### Answer
```
GGWGWBWBWGWBWWGBWGBBWWWGGBBWWWWBW
```
