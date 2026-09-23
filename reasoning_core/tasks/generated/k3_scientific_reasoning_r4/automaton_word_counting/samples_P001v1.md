## Level 0

### Example 1

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..3.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (0, 3, a)
  (1, 0, a)
  (2, 0, a)
  (3, 0, a)
  (0, 2, b)
  (1, 2, b)
  (2, 0, b)
  (3, 2, b)
Start state: 1
Accepting states: 0, 2, 3
What is the number of words of length exactly 2 that the automaton accepts? Answer with a single non-negative integer.

Answer:

16

### Example 2

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..3.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (0, 1, a)
  (0, 0, a)
  (1, 3, a)
  (1, 0, a)
  (2, 0, a)
  (2, 3, a)
  (3, 3, a)
  (3, 0, a)
  (0, 0, b)
  (0, 3, b)
  (1, 2, b)
  (1, 0, b)
  (2, 0, b)
  (2, 0, b)
  (3, 3, b)
  (3, 0, b)
Start state: 2
Accepting states: 3
What is the number of words of length exactly 2 that the automaton accepts? Answer with a single non-negative integer.

Answer:

21

## Level 2

### Example 1

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..5.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (1, 5, a)
  (2, 1, a)
  (3, 2, a)
  (4, 4, a)
  (5, 3, a)
  (1, 2, b)
  (2, 0, b)
  (3, 5, b)
  (4, 0, b)
  (5, 3, b)
  (3, 0, eps)
Start state: 5
Accepting states: 1, 2, 5
What is the number of words of length exactly 4 that the automaton accepts? Answer with a single non-negative integer.

Answer:

24

### Example 2

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..5.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (0, 3, a)
  (0, 2, a)
  (1, 5, a)
  (1, 3, a)
  (2, 3, a)
  (2, 0, a)
  (3, 5, a)
  (3, 4, a)
  (4, 5, a)
  (4, 2, a)
  (5, 0, a)
  (5, 1, a)
  (0, 1, b)
  (0, 0, b)
  (1, 3, b)
  (1, 5, b)
  (2, 5, b)
  (2, 2, b)
  (3, 3, b)
  (3, 0, b)
  (4, 2, b)
  (4, 3, b)
  (5, 2, b)
  (5, 0, b)
  (2, 1, eps)
  (5, 3, eps)
Start state: 4
Accepting states: 0, 4
What is the number of words of length exactly 4 that the automaton accepts? Answer with a single non-negative integer.

Answer:

475

## Level 5

### Example 1

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..5.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (0, 5, a)
  (1, 4, a)
  (2, 5, a)
  (3, 4, a)
  (4, 5, a)
  (5, 4, a)
  (0, 4, b)
  (1, 5, b)
  (2, 4, b)
  (3, 5, b)
  (4, 2, b)
  (5, 3, b)
  (1, 0, eps)
  (3, 2, eps)
  (5, 4, eps)
Start state: 3
Accepting states: 1, 3, 5
What is the number of words of length exactly 7 that the automaton accepts? Answer with a single non-negative integer.

Answer:

256

### Example 2

Prompt:

Consider an NFA over the alphabet {a, b}.
States are the integers 0..11.
Transitions are (from, to, symbol) triples; the symbol is 'a', 'b', or 'eps' (an epsilon move that may be taken for free before or after any symbol).
Transitions:
  (0, 7, a)
  (1, 8, a)
  (2, 8, a)
  (3, 10, a)
  (4, 11, a)
  (5, 11, a)
  (6, 1, a)
  (7, 2, a)
  (8, 2, a)
  (9, 10, a)
  (10, 11, a)
  (11, 11, a)
  (0, 8, b)
  (1, 8, b)
  (2, 6, b)
  (3, 11, b)
  (4, 11, b)
  (5, 9, b)
  (6, 11, b)
  (7, 11, b)
  (8, 9, b)
  (9, 11, b)
  (10, 11, b)
  (11, 9, b)
Start state: 1
Accepting states: 3, 6, 9
What is the number of words of length exactly 7 that the automaton accepts? Answer with a single non-negative integer.

Answer:

255

