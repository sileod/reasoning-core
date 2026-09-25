# samples_P005v1  consensus_cut_minimum

## Level 0

### Example 1

Prompt:

Along the integer line from position 0 to position 6 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [1, 3) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
  [0, 4) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 1

### Example 2

Prompt:

Along the integer line from position 0 to position 6 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [0, 6) weight 2: each of its cells contributes +2 if covered by a 'plus' run and -2 if covered by a 'minus' run.
  [1, 3) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 2

## Level 2

### Example 1

Prompt:

Along the integer line from position 0 to position 10 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [5, 7) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
  [1, 5) weight 1: each of its cells contributes +1 if covered by a 'plus' run and -1 if covered by a 'minus' run.
  [2, 8) weight 4: each of its cells contributes +4 if covered by a 'plus' run and -4 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 2

### Example 2

Prompt:

Along the integer line from position 0 to position 10 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [4, 8) weight 4: each of its cells contributes +4 if covered by a 'plus' run and -4 if covered by a 'minus' run.
  [5, 7) weight 4: each of its cells contributes +4 if covered by a 'plus' run and -4 if covered by a 'minus' run.
  [5, 7) weight 2: each of its cells contributes +2 if covered by a 'plus' run and -2 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 1

## Level 5

### Example 1

Prompt:

Along the integer line from position 0 to position 15 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [5, 15) weight 4: each of its cells contributes +4 if covered by a 'plus' run and -4 if covered by a 'minus' run.
  [8, 12) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
  [6, 8) weight 1: each of its cells contributes +1 if covered by a 'plus' run and -1 if covered by a 'minus' run.
  [3, 13) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
  [1, 11) weight 2: each of its cells contributes +2 if covered by a 'plus' run and -2 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 5

### Example 2

Prompt:

Along the integer line from position 0 to position 15 the valuation sign is constant between cuts and toggles (+ then - then +, ...) at every cut. The sign to the left of position 0 is +.
There are valuations, each an interval [s, e) of adjacent cells with a shared weight w:
  [0, 12) weight 1: each of its cells contributes +1 if covered by a 'plus' run and -1 if covered by a 'minus' run.
  [2, 12) weight 1: each of its cells contributes +1 if covered by a 'plus' run and -1 if covered by a 'minus' run.
  [3, 11) weight 1: each of its cells contributes +1 if covered by a 'plus' run and -1 if covered by a 'minus' run.
  [2, 14) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
  [5, 7) weight 3: each of its cells contributes +3 if covered by a 'plus' run and -3 if covered by a 'minus' run.
For every valuation its signed total (sum of +w contributions minus sum of -w contributions) must equal 0.
Find the minimum number of cuts achieving this. Answer with one integer (the fewest cuts).

Answer: 5
