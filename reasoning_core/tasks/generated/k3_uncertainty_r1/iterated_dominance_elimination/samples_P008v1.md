# Samples P008v1

## Level 0

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..1); column player chooses a column (cols 0..1); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(2,4), (4,6)]
      [(2,4), (5,3)]

**Answer:**

    ((1,), (0,))

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..1); column player chooses a column (cols 0..1); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(3,1), (6,5)]
      [(4,2), (5,2)]

**Answer:**

    ((0,), (1,))

## Level 2

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..2); column player chooses a column (cols 0..2); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(3,13), (8,1), (7,4)]
      [(10,4), (13,9), (5,3)]
      [(9,5), (6,5), (11,3)]

**Answer:**

    ((1,), (1,))

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..2); column player chooses a column (cols 0..2); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(1,14), (1,13), (1,10)]
      [(3,1), (10,6), (11,11)]
      [(2,14), (4,14), (9,5)]

**Answer:**

    ((1,), (2,))

## Level 5

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..3); column player chooses a column (cols 0..3); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(26,12), (17,19), (10,1), (1,25)]
      [(6,8), (16,10), (14,9), (5,5)]
      [(23,4), (26,25), (18,4), (20,22)]
      [(6,8), (26,17), (16,10), (10,10)]

**Answer:**

    ((2,), (1,))

**Prompt:**

    Below is the bimatrix of a two-player game. Row player chooses a row (rows 0..3); column player chooses a column (cols 0..3); each entry is (row payoff, column payoff). Repeatedly delete every pure strategy that is strictly dominated by another pure strategy of the same player (a strategy dominates another when its payoff is never worse and strictly better in at least one entry). After each deletion re-scan both players because new dominances can emerge. Continue until no further deletion is possible.
    Report the surviving strategy sets as two sorted tuples (surviving_rows, surviving_cols), e.g. ((0, 2), (1,)).
    Game:
      [(4,17), (25,4), (9,10), (14,18)]
      [(2,22), (5,16), (16,21), (18,22)]
      [(14,16), (19,4), (16,25), (19,12)]
      [(16,13), (11,7), (21,5), (22,10)]

**Answer:**

    ((3,), (0,))

