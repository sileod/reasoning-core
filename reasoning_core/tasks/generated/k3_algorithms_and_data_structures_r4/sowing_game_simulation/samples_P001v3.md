## Level 0

Prompt:

There is a circular board of 4 pits numbered 0..3. Initial seeds per pit (index:count): 0:3, 1:0, 2:1, 3:1. Sowing moves clockwise (right). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 1, 3. Give the pit index of the first illegal move (the first attempted turn whose start pit is empty). The answer is one integer.

Answer:

1

Prompt:

There is a circular board of 4 pits numbered 0..3. Initial seeds per pit (index:count): 0:3, 1:3, 2:4, 3:4. Sowing moves clockwise (right). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 0, 1. Give the total number of seeds captured across the whole play. The answer is one integer.

Answer:

7

## Level 2

Prompt:

There is a circular board of 5 pits numbered 0..4. Initial seeds per pit (index:count): 0:4, 1:3, 2:5, 3:5, 4:3. Sowing moves clockwise (right). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 3, 2, 1. Give the total number of seeds captured across the whole play. The answer is one integer.

Answer:

10

Prompt:

There is a circular board of 5 pits numbered 0..4. Initial seeds per pit (index:count): 0:6, 1:4, 2:0, 3:3, 4:4. Sowing moves clockwise (right). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 2, 0, 1. Give the pit index of the first illegal move (the first attempted turn whose start pit is empty). The answer is one integer.

Answer:

2

## Level 5

Prompt:

There is a circular board of 6 pits numbered 0..5. Initial seeds per pit (index:count): 0:0, 1:3, 2:5, 3:3, 4:5, 5:6. Sowing moves counter-clockwise (left). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 0, 5, 4, 3. Give the pit index of the first illegal move (the first attempted turn whose start pit is empty). The answer is one integer.

Answer:

0

Prompt:

There is a circular board of 6 pits numbered 0..5. Initial seeds per pit (index:count): 0:6, 1:5, 2:0, 3:6, 4:0, 5:4. Sowing moves clockwise (right). On each turn: pick up all seeds from the start pit; if that pit has 0 seeds the move is illegal. Distribute them one seed per pit moving that direction, wrapping at the end. If the last seed lands in a pit that was empty before its drop, capture: remove the single landing seed plus all seeds in the mirror pit (index n-1-L), add them to a running captured total, and end the turn. Otherwise, if the landing pit is now non-empty and is not the turn's start pit, relay: continue sowing from it. Play turns in order starting from pits: 2, 3, 1, 4. Give the pit index of the first illegal move (the first attempted turn whose start pit is empty). The answer is one integer.

Answer:

2

