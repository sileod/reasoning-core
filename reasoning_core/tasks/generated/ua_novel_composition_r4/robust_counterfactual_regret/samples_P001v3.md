## Level 0

Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 3 interventions and 2 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [4, 0]
  intervention 1: [2, 2]
  intervention 2: [1, 3]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

1 1


Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 3 interventions and 2 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [0, 1]
  intervention 1: [1, 0]
  intervention 2: [3, 1]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

0 1


## Level 2

Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 5 interventions and 4 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [4, 9, 3, 0]
  intervention 1: [3, 6, 10, 9]
  intervention 2: [1, 1, 1, 2]
  intervention 3: [4, 5, 6, 6]
  intervention 4: [5, 9, 6, 7]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

2 3


Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 5 interventions and 4 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [9, 1, 2, 0]
  intervention 1: [1, 4, 6, 6]
  intervention 2: [10, 4, 9, 3]
  intervention 3: [9, 1, 0, 5]
  intervention 4: [9, 9, 3, 8]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

1 2


## Level 5

Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 8 interventions and 7 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [9, 6, 13, 7, 12, 11, 16]
  intervention 1: [18, 9, 1, 1, 9, 11, 16]
  intervention 2: [3, 19, 3, 14, 16, 0, 13]
  intervention 3: [19, 9, 17, 4, 8, 14, 5]
  intervention 4: [8, 10, 2, 14, 0, 19, 6]
  intervention 5: [11, 7, 11, 12, 19, 19, 3]
  intervention 6: [1, 5, 15, 15, 15, 3, 17]
  intervention 7: [10, 5, 13, 9, 12, 8, 9]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

7 2


Prompt:

An agent must pick one intervention to use in all scenarios, hedging against unknown future conditions. There are 8 interventions and 7 coupled scenarios, where entry cost[i][s] is the loss of intervention i under scenario s:
  intervention 0: [2, 12, 16, 17, 18, 18, 16]
  intervention 1: [18, 2, 12, 11, 4, 14, 17]
  intervention 2: [17, 3, 13, 11, 18, 19, 1]
  intervention 3: [13, 18, 0, 9, 0, 1, 0]
  intervention 4: [3, 12, 6, 12, 12, 16, 4]
  intervention 5: [18, 4, 15, 17, 16, 3, 1]
  intervention 6: [16, 14, 9, 7, 19, 8, 5]
  intervention 7: [7, 2, 3, 5, 10, 7, 7]
Use Savage minimax regret. For each scenario, an intervention's regret is its loss minus the best (minimum) loss among all interventions in that same scenario; an intervention's worst-case regret is the maximum of its regrets over scenarios. The robust intervention is the one with the smallest worst-case regret (ties: smallest index). Its adversarial witness is the scenario that gives it its worst-case regret (ties: smallest scenario index). Answer as "<robust intervention index> <witness scenario index>".

Answer:

7 4

