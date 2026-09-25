# Crystal Signature Transfer P001v1 - samples

## Level 0

### Example 1

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 2}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 1. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [1, 2]
row 1: [1, 1]

i = 1, alphabet size n = 2.
```

Answer:

```
[[0, 1]]
```

### Example 2

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 3}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 2. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [3, 3]
row 1: [2, 2]

i = 2, alphabet size n = 3.
```

Answer:

```
[[0, 1]]
```

## Level 2

### Example 1

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 2}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 1. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [2, 2]
row 1: [2, 1]

i = 1, alphabet size n = 2.
```

Answer:

```
[[0, 1]]
```

### Example 2

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 2}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 1. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [1, 2, 1, 2, 1]
row 1: [1, 1, 1, 1, 2]

i = 1, alphabet size n = 2.
```

Answer:

```
[[0, 2], [0, 0]]
```

## Level 5

### Example 1

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 5}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 3. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [1, 4]
row 1: [4, 2]
row 2: [5, 1]
row 3: [3, 1]
row 4: [5, 4]
row 5: [5, 5]
row 6: [3, 2]
row 7: [3, 4]

i = 3, alphabet size n = 5.
```

Answer:

```
[[1, 0]]
```

### Example 2

Prompt:

```
A word is written into a grid of cells; each cell holds a letter from the alphabet {1, ..., 4}.
The reading word is read BOTTOM row to TOP row, left to right within each row (bottom-to-top reading word).

Apply the crystal RAISING operator e_i for i = 3. Its signature rule: restrict the reading word to the two letters i and i+1; bracket-match each letter i with the nearest unmatched letter i+1 after it (matched pairs are removed). Of the letters that remain unmatched, e_i changes the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null move and changes nothing.
Apply e_i over and over until it becomes a null move.

List the cell coordinates [row, column] of the entries that change, in the order they change (0-indexed row counted from the top, column from the left). If nothing changes, answer [].

Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below (reading word 1 2 1 1 3 1, bottom row first) the entries that change are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].

row 0: [4, 1, 3, 1, 4, 2, 1, 4]
row 1: [3, 4, 1, 3, 4, 3, 1, 1]
row 2: [3, 2, 2, 4, 1, 2, 4, 2]
row 3: [1, 3, 2, 3, 4, 4, 3, 3]
row 4: [4, 1, 4, 1, 3, 1, 1, 4]

i = 3, alphabet size n = 4.
```

Answer:

```
[]
```
