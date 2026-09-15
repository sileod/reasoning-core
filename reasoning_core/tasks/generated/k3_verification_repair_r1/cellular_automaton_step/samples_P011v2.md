# Level 0

### Prompt

An elementary cellular automaton (ECA) of length 6 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 1, 001 -> 1, 010 -> 1, 011 -> 0, 100 -> 0, 101 -> 0, 110 -> 0, 111 -> 0. Here cells beyond the ends wrap around to the opposite end (periodic boundary). The initial row is 011011. Apply the rule for 1 step(s). What is the state (0 or 1) of the cell at position 3 (0-indexed from the left) after 1 step(s)? Answer 0 or 1.

### Answer

0

### Prompt

An elementary cellular automaton (ECA) of length 6 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 0, 001 -> 0, 010 -> 1, 011 -> 1, 100 -> 1, 101 -> 1, 110 -> 1, 111 -> 1. Here cells beyond the ends are treated as 0 (zero boundary). The initial row is 100111. Apply the rule for 2 step(s). How many live cells (1s) are in the row after 2 step(s)? Answer a non-negative integer.

### Answer

6

# Level 2

### Prompt

An elementary cellular automaton (ECA) of length 10 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 1, 001 -> 1, 010 -> 0, 011 -> 0, 100 -> 1, 101 -> 1, 110 -> 0, 111 -> 1. Here cells beyond the ends wrap around to the opposite end (periodic boundary). The initial row is 1000010000. Apply the rule for 3 step(s). What is the full row after 3 step(s)? Answer as a string of 0s and 1s of length 10.

### Answer

0100101001

### Prompt

An elementary cellular automaton (ECA) of length 10 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 1, 001 -> 1, 010 -> 1, 011 -> 1, 100 -> 0, 101 -> 1, 110 -> 1, 111 -> 0. Here cells beyond the ends wrap around to the opposite end (periodic boundary). The initial row is 0001111111. Apply the rule for 3 step(s). What is the full row after 3 step(s)? Answer as a string of 0s and 1s of length 10.

### Answer

0111110000

# Level 5

### Prompt

An elementary cellular automaton (ECA) of length 16 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 0, 001 -> 0, 010 -> 1, 011 -> 0, 100 -> 0, 101 -> 1, 110 -> 1, 111 -> 1. Here cells beyond the ends are treated as 0 (zero boundary). The initial row is 0110100011111010. Apply the rule for 7 step(s). How many live cells (1s) are in the row after 7 step(s)? Answer a non-negative integer.

### Answer

2

### Prompt

An elementary cellular automaton (ECA) of length 16 is updated synchronously. The new value of each cell depends on itself, its left neighbor, and its right neighbor according to the local rule. Here the transitions are: 000 -> 0, 001 -> 1, 010 -> 0, 011 -> 1, 100 -> 0, 101 -> 1, 110 -> 0, 111 -> 0. Here cells beyond the ends are treated as 0 (zero boundary). The initial row is 0110001100101000. Apply the rule for 7 step(s). How many live cells (1s) are in the row after 7 step(s)? Answer a non-negative integer.

### Answer

3
