# Samples for extensive_form_to_bimatrix (P002v3)

## Level 0

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 2 branches.
- Branch 1: Player 2 node #1 has 2 actions:
    - action 1 -> terminal: payoff (-2,3)
    - action 2 -> terminal: chance { 2/3: (-4,0), 1/3: (-1,1) }
- Branch 2: Player 2 node #2 has 2 actions:
    - action 1 -> terminal: payoff (-2,-1)
    - action 2 -> terminal: payoff (-3,3)

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#2 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (-2,3) | (-2,3) | (-3,1/3) | (-3,1/3) ; (-2,-1) | (-3,3) | (-2,-1) | (-3,3)

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 2 branches.
- Branch 1: Player 2 node #1 has 2 actions:
    - action 1 -> terminal: payoff (3,2)
    - action 2 -> terminal: payoff (-3,-2)
- Branch 2: Player 2 node #2 has 2 actions:
    - action 1 -> terminal: payoff (-4,-1)
    - action 2 -> terminal: payoff (0,-2)

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#2 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (3,2) | (3,2) | (-3,-2) | (-3,-2) ; (-4,-1) | (0,-2) | (-4,-1) | (0,-2)

## Level 2

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 2 branches.
- Branch 1: Player 2 node #1 has 4 actions:
    - action 1 -> terminal: payoff (-8,-4)
    - action 2 -> terminal: payoff (7,-1)
    - action 3 -> terminal: payoff (5,-1)
    - action 4 -> terminal: chance { 2/3: (-8,-3), 1/3: (7,-2) }
- Branch 2: Player 2 node #2 has 4 actions:
    - action 1 -> terminal: chance { 1/2: (10,6), 1/2: (-7,5) }
    - action 2 -> terminal: payoff (9,-3)
    - action 3 -> terminal: chance { 2/3: (-6,-4), 1/3: (-10,9) }
    - action 4 -> terminal: payoff (1,-3)

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#2 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (-8,-4) | (-8,-4) | (-8,-4) | (-8,-4) | (7,-1) | (7,-1) | (7,-1) | (7,-1) | (5,-1) | (5,-1) | (5,-1) | (5,-1) | (-3,-8/3) | (-3,-8/3) | (-3,-8/3) | (-3,-8/3) ; (3/2,11/2) | (9,-3) | (-22/3,1/3) | (1,-3) | (3/2,11/2) | (9,-3) | (-22/3,1/3) | (1,-3) | (3/2,11/2) | (9,-3) | (-22/3,1/3) | (1,-3) | (3/2,11/2) | (9,-3) | (-22/3,1/3) | (1,-3)

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 3 branches.
- Branch 1: Player 2 node #1 has 2 actions:
    - action 1 -> terminal: payoff (-5,-1)
    - action 2 -> terminal: payoff (2,0)
- Branch 2: Player 2 node #2 has 2 actions:
    - action 1 -> terminal: payoff (0,9)
    - action 2 -> terminal: chance { 1/2: (-2,-4), 1/2: (-6,3) }
- Branch 3: Player 2 node #3 has 2 actions:
    - action 1 -> terminal: chance { 1/2: (1,7), 1/2: (2,2) }
    - action 2 -> terminal: payoff (6,0)

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#3 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (-5,-1) | (-5,-1) | (-5,-1) | (-5,-1) | (2,0) | (2,0) | (2,0) | (2,0) ; (0,9) | (0,9) | (-4,-1/2) | (-4,-1/2) | (0,9) | (0,9) | (-4,-1/2) | (-4,-1/2) ; (3/2,9/2) | (6,0) | (3/2,9/2) | (6,0) | (3/2,9/2) | (6,0) | (3/2,9/2) | (6,0)

## Level 5

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 2 branches.
- Branch 1: Player 2 node #1 has 2 actions:
    - action 1 -> terminal: chance { 1/2: (-17,-8), 1/2: (5,-16) }
    - action 2 -> terminal: chance { 1/2: (9,9), 1/2: (16,16) }
- Branch 2: Player 2 node #2 has 2 actions:
    - action 1 -> terminal: payoff (-8,-2)
    - action 2 -> terminal: payoff (-2,-9)

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#2 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (-6,-12) | (-6,-12) | (25/2,25/2) | (25/2,25/2) ; (-8,-2) | (-2,-9) | (-8,-2) | (-2,-9)

In an extensive-form game, a pure strategy for a player chooses one action at every one of that player's decision nodes. A strategy profile fixes a terminal node; a chance node contributes its probability-weighted (expected) payoff. The induced normal-form (bimatrix) payoff table lists, for every pair of pure strategies (one per player), the (payoff to Player 1, payoff to Player 2) expected payoff pair.

Consider this perfect-information extensive-form game where Player 1 chooses first at the root, then Player 2.

Game tree:
- Player 1 (root) has 2 branches.
- Branch 1: Player 2 node #1 has 3 actions:
    - action 1 -> terminal: chance { 1/2: (-13,-8), 1/2: (12,12) }
    - action 2 -> terminal: payoff (12,16)
    - action 3 -> terminal: payoff (-6,-15)
- Branch 2: Player 2 node #2 has 3 actions:
    - action 1 -> terminal: chance { 1/2: (15,-14), 1/2: (5,10) }
    - action 2 -> terminal: chance { 1/2: (-4,15), 1/2: (-17,9) }
    - action 3 -> terminal: chance { 1/2: (9,10), 1/2: (-8,3) }

Strategy order: rows are Player 1's pure strategies in order of the root branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure strategies, each written as the tuple of actions chosen at Player 2's decision nodes #1..#2 from top to bottom, ordered lexicographically by these tuples.

Give the induced normal-form payoff bimatrix. Format: list the rows in order separated by " ; ", and within each row list the column payoff pairs left to right separated by " | ". Write each entry as (payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example 5/2) and integers as plain numbers.

Answer: (-1/2,2) | (-1/2,2) | (-1/2,2) | (12,16) | (12,16) | (12,16) | (-6,-15) | (-6,-15) | (-6,-15) ; (10,-2) | (-21/2,12) | (1/2,13/2) | (10,-2) | (-21/2,12) | (1/2,13/2) | (10,-2) | (-21/2,12) | (1/2,13/2)
