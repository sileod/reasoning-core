## Level 0
### Prompt
A coalitional game has players labeled 0..2. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 5
   subset 1: value 4
   subset 2: value 0
   subset 3: value 3
   subset 4: value 4
   subset 5: value 2
   subset 6: value 2
   subset 7: value 3
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..2, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
1/6 -11/6 -1/3

### Prompt
A coalitional game has players labeled 0..2. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 3
   subset 1: value 3
   subset 2: value 1
   subset 3: value 2
   subset 4: value 5
   subset 5: value 1
   subset 6: value 3
   subset 7: value 1
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..2, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
-7/6 -7/6 1/3

## Level 2
### Prompt
A coalitional game has players labeled 0..4. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 1
   subset 1: value 5
   subset 2: value 6
   subset 3: value 11
   subset 4: value 3
   subset 5: value 11
   subset 6: value 5
   subset 7: value 11
   subset 8: value 4
   subset 9: value 5
   subset 10: value 9
   subset 11: value 2
   subset 12: value 9
   subset 13: value 10
   subset 14: value 6
   subset 15: value 10
   subset 16: value 10
   subset 17: value 5
   subset 18: value 9
   subset 19: value 11
   subset 20: value 5
   subset 21: value 9
   subset 22: value 11
   subset 23: value 0
   subset 24: value 6
   subset 25: value 10
   subset 26: value 1
   subset 27: value 7
   subset 28: value 3
   subset 29: value 1
   subset 30: value 0
   subset 31: value 11
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..4, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
109/30 173/60 29/30 83/60 17/15

### Prompt
A coalitional game has players labeled 0..4. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 0
   subset 1: value 7
   subset 2: value 9
   subset 3: value 9
   subset 4: value 9
   subset 5: value 3
   subset 6: value 0
   subset 7: value 1
   subset 8: value 0
   subset 9: value 8
   subset 10: value 0
   subset 11: value 4
   subset 12: value 8
   subset 13: value 6
   subset 14: value 6
   subset 15: value 1
   subset 16: value 5
   subset 17: value 5
   subset 18: value 3
   subset 19: value 10
   subset 20: value 9
   subset 21: value 2
   subset 22: value 3
   subset 23: value 1
   subset 24: value 3
   subset 25: value 6
   subset 26: value 5
   subset 27: value 8
   subset 28: value 7
   subset 29: value 5
   subset 30: value 0
   subset 31: value 10
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..4, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
17/5 47/30 23/20 79/60 77/30

## Level 5
### Prompt
A coalitional game has players labeled 0..5. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 7
   subset 1: value 10
   subset 2: value 0
   subset 3: value 0
   subset 4: value 3
   subset 5: value 1
   subset 6: value 6
   subset 7: value 5
   subset 8: value 3
   subset 9: value 5
   subset 10: value 5
   subset 11: value 16
   subset 12: value 12
   subset 13: value 11
   subset 14: value 18
   subset 15: value 19
   subset 16: value 9
   subset 17: value 10
   subset 18: value 0
   subset 19: value 2
   subset 20: value 10
   subset 21: value 14
   subset 22: value 7
   subset 23: value 2
   subset 24: value 14
   subset 25: value 13
   subset 26: value 7
   subset 27: value 15
   subset 28: value 11
   subset 29: value 14
   subset 30: value 16
   subset 31: value 7
   subset 32: value 10
   subset 33: value 4
   subset 34: value 12
   subset 35: value 14
   subset 36: value 12
   subset 37: value 17
   subset 38: value 14
   subset 39: value 3
   subset 40: value 19
   subset 41: value 14
   subset 42: value 17
   subset 43: value 18
   subset 44: value 9
   subset 45: value 12
   subset 46: value 5
   subset 47: value 17
   subset 48: value 5
   subset 49: value 12
   subset 50: value 18
   subset 51: value 3
   subset 52: value 16
   subset 53: value 11
   subset 54: value 14
   subset 55: value 20
   subset 56: value 2
   subset 57: value 2
   subset 58: value 2
   subset 59: value 1
   subset 60: value 8
   subset 61: value 2
   subset 62: value 6
   subset 63: value 17
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..5, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
137/60 17/15 199/60 13/30 -3/10 47/15

### Prompt
A coalitional game has players labeled 0..5. The value map gives the value v(S) for each subset S (represented by its bit-mask of players included):
   subset 0: value 10
   subset 1: value 5
   subset 2: value 11
   subset 3: value 10
   subset 4: value 20
   subset 5: value 0
   subset 6: value 8
   subset 7: value 15
   subset 8: value 12
   subset 9: value 18
   subset 10: value 7
   subset 11: value 0
   subset 12: value 20
   subset 13: value 2
   subset 14: value 11
   subset 15: value 19
   subset 16: value 20
   subset 17: value 14
   subset 18: value 17
   subset 19: value 2
   subset 20: value 17
   subset 21: value 10
   subset 22: value 14
   subset 23: value 16
   subset 24: value 19
   subset 25: value 2
   subset 26: value 3
   subset 27: value 3
   subset 28: value 6
   subset 29: value 17
   subset 30: value 16
   subset 31: value 6
   subset 32: value 3
   subset 33: value 8
   subset 34: value 5
   subset 35: value 20
   subset 36: value 17
   subset 37: value 14
   subset 38: value 8
   subset 39: value 3
   subset 40: value 11
   subset 41: value 1
   subset 42: value 17
   subset 43: value 20
   subset 44: value 2
   subset 45: value 11
   subset 46: value 0
   subset 47: value 7
   subset 48: value 6
   subset 49: value 14
   subset 50: value 12
   subset 51: value 3
   subset 52: value 20
   subset 53: value 0
   subset 54: value 9
   subset 55: value 1
   subset 56: value 20
   subset 57: value 3
   subset 58: value 13
   subset 59: value 3
   subset 60: value 13
   subset 61: value 18
   subset 62: value 20
   subset 63: value 1
Compute the Shapley value vector, where player i's Shapley value is the average of its marginal contribution v(S u {i}) - v(S) over all random orders of the players.
Give the answer as the list of reduced fractions for players 0..5, space-separated, e.g. for 3 players '3/2 1/2 5/2'.
### Answer
-123/20 -217/60 61/30 23/30 19/15 -33/10

