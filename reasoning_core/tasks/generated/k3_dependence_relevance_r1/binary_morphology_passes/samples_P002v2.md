## Level 0

Start with this binary image (0 = background, 1 = foreground), 4 rows by 4 columns:
1101
1111
1111
0111
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Dilate using a vertical bar (the center cell plus its up and down neighbors): a cell becomes foreground if any of the covered in-bounds cells is foreground.
Pass 2: Open using a vertical bar (the center cell plus its up and down neighbors): erode, then dilate, both with the same structuring element.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 14

## Level 0

Start with this binary image (0 = background, 1 = foreground), 4 rows by 4 columns:
0111
0111
0000
0000
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Erode using a horizontal bar (the center cell plus its left and right neighbors): a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground.
Pass 2: Dilate using a full 3-by-3 square: a cell becomes foreground if any of the covered in-bounds cells is foreground.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 6

## Level 2

Start with this binary image (0 = background, 1 = foreground), 6 rows by 6 columns:
000000
000000
001000
000100
000000
000000
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Close using a horizontal bar (the center cell plus its left and right neighbors): dilate, then erode, both with the same structuring element.
Pass 2: Close using a cross (the center cell plus its up, down, left, and right neighbors): dilate, then erode, both with the same structuring element.
Pass 3: Erode using a full 3-by-3 square: a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 2

## Level 2

Start with this binary image (0 = background, 1 = foreground), 6 rows by 6 columns:
000100
000100
000100
000000
000000
000000
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Open using a vertical bar (the center cell plus its up and down neighbors): erode, then dilate, both with the same structuring element.
Pass 2: Close using a horizontal bar (the center cell plus its left and right neighbors): dilate, then erode, both with the same structuring element.
Pass 3: Erode using a horizontal bar (the center cell plus its left and right neighbors): a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 3

## Level 5

Start with this binary image (0 = background, 1 = foreground), 9 rows by 9 columns:
000000000
000111110
001111110
011111110
011111110
011111110
011111110
011111110
000000000
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Dilate using a cross (the center cell plus its up, down, left, and right neighbors): a cell becomes foreground if any of the covered in-bounds cells is foreground.
Pass 2: Erode using a full 3-by-3 square: a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground.
Pass 3: Dilate using a full 3-by-3 square: a cell becomes foreground if any of the covered in-bounds cells is foreground.
Pass 4: Close using a cross (the center cell plus its up, down, left, and right neighbors): dilate, then erode, both with the same structuring element.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 46

## Level 5

Start with this binary image (0 = background, 1 = foreground), 9 rows by 9 columns:
000000000
000000000
000010000
000000000
000000000
000000000
000000000
000000000
000000000
Apply these binary-morphology passes one after another, always treating cells outside the image as 0 (background).
Pass 1: Hit-miss transform detecting a foreground 2-by-2 corner, meaning the cell and its right and down neighbors are all foreground while the down-right diagonal cell is background (the other cells do not matter): the output cell is foreground only at exact matches of that foreground/background pattern entirely inside the image.
Pass 2: Dilate using a cross (the center cell plus its up, down, left, and right neighbors): a cell becomes foreground if any of the covered in-bounds cells is foreground.
Pass 3: Erode using a horizontal bar (the center cell plus its left and right neighbors): a cell stays foreground only if the whole structuring element fits inside and every covered cell is foreground.
Pass 4: Hit-miss transform detecting a foreground 2-by-2 corner, meaning the cell and its right and down neighbors are all foreground while the down-right diagonal cell is background (the other cells do not matter): the output cell is foreground only at exact matches of that foreground/background pattern entirely inside the image.
Report the final number of foreground cells (cells equal to 1). The answer is a single integer.

**Answer**: 1

