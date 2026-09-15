Level 0
Prompt: An 4-by-4 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 3, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 1. What is the Morton (Z-order) index of the cell at column 3, row 3? Answer with a single integer.
Answer: 15

Prompt: An 4-by-4 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 3, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 1. The cell at column 3, row 2 has a neighbor one cell to the west (column decreases by 1). What is the Morton (Z-order) index of that neighbor cell? Answer with a single integer.
Answer: 12

Level 2
Prompt: An 16-by-16 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 15, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 3. What is the Morton (Z-order) index of the cell at column 3, row 12? Answer with a single integer.
Answer: 165

Prompt: An 16-by-16 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 15, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 3. The cell at column 11, row 10 has a neighbor one cell to the north (row decreases by 1). What is the Morton (Z-order) index of that neighbor cell? Answer with a single integer.
Answer: 199

Level 5
Prompt: An 128-by-128 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 127, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 6. Which cell has Morton (Z-order) index 7747? Answer as its column and row, written 'column,row'.
Answer: 105,49

Prompt: An 128-by-128 grid of cells is numbered in Z-order (Morton) curve index. For columns and rows numbered 0 to 127, index bit position 2i holds column bit i and position 2i+1 holds row bit i, for i from 0 to 6. The cell at column 98, row 29 has a neighbor one cell to the north (row decreases by 1). What is the Morton (Z-order) index of that neighbor cell? Answer with a single integer.
Answer: 5796

