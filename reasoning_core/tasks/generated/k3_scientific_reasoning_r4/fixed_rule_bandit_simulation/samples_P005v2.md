# P005v2 samples: fixed_rule_bandit_simulation

# Level 0

Prompt:
You are simulating a multi-armed bandit with 3 arms labeled 0 through 2, over 12 rounds (rounds 1..12). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 1,1,1,0,1,1,1,1,0,1,1,0
arm 1: 1,1,1,1,0,0,0,1,1,1,0,1
arm 2: 1,0,1,0,1,0,1,0,1,1,0,1
Allocation rule: Epsilon-greedy on a fixed schedule: the exploration rate is 1/2, so on every round r that is a multiple of 2 (r % 2 == 0) you EXPLORE by pulling the arm that has been pulled the fewest times so far; on all other rounds you EXPLOIT by pulling the arm with the highest empirical success rate (successes / pulls before that round); an arm never pulled before is treated as having rate -infinity.
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 12? Answer with a single integer.

Answer: 4

Prompt:
You are simulating a multi-armed bandit with 3 arms labeled 0 through 2, over 17 rounds (rounds 1..17). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1
arm 1: 0,0,1,0,0,1,0,0,0,1,0,0,0,0,0,1,1
arm 2: 0,0,0,1,1,1,0,1,0,0,0,1,0,0,0,1,0
Allocation rule: Epsilon-greedy on a fixed schedule: the exploration rate is 1/2, so on every round r that is a multiple of 2 (r % 2 == 0) you EXPLORE by pulling the arm that has been pulled the fewest times so far; on all other rounds you EXPLOIT by pulling the arm with the highest empirical success rate (successes / pulls before that round); an arm never pulled before is treated as having rate -infinity.
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 17? Answer with a single integer.

Answer: 4

# Level 2

Prompt:
You are simulating a multi-armed bandit with 4 arms labeled 0 through 3, over 28 rounds (rounds 1..28). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 1,1,0,1,1,1,1,1,0,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1
arm 1: 0,0,1,0,0,0,0,0,1,1,1,0,1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,0
arm 2: 0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
arm 3: 0,1,1,1,1,0,1,0,0,1,1,1,0,0,0,1,0,0,1,1,1,0,1,1,1,1,0,0
Allocation rule: Thompson sampling over tabulated Beta posteriors: each arm starts with a Beta(1,1) prior; after s successes and f failures its posterior is Beta(1+s, 1+f). At round r draw one sample for every arm from its current posterior, where the sample is the inverse-CDF of the posterior Beta evaluated at the tabulated grid value below whose slot is assigned deterministically by slot = (arm_index*7 + r*13) mod 64. Pull the arm whose drawn sample is largest.
Tabulated grid (index -> value): 0:0.953,1:0.883,2:0.844,3:0.863,4:0.917,5:0.849,6:0.784,7:0.514,8:0.933,9:0.528,10:0.623,11:0.629,12:0.818,13:0.537,14:0.723,15:0.665,16:0.605,17:0.648,18:0.875,19:0.581,20:0.977,21:0.662,22:0.973,23:0.868,24:0.601,25:0.836,26:0.696,27:0.707,28:0.964,29:0.741,30:0.858,31:0.535,32:0.844,33:0.842,34:0.659,35:0.804,36:0.938,37:0.641,38:0.834,39:0.751,40:0.748,41:0.723,42:0.763,43:0.662,44:0.639,45:0.75,46:0.736,47:0.536,48:0.645,49:0.582,50:0.629,51:0.87,52:0.515,53:0.774,54:0.711,55:0.717,56:0.536,57:0.59,58:0.966,59:0.667,60:0.964,61:0.646,62:0.607,63:0.877
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 28? Answer with a single integer.

Answer: 1

Prompt:
You are simulating a multi-armed bandit with 4 arms labeled 0 through 3, over 24 rounds (rounds 1..24). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 1,0,1,0,0,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,1,0
arm 1: 1,0,1,1,1,1,0,1,1,1,0,1,1,1,1,0,1,1,1,1,1,1,0,1
arm 2: 1,0,1,0,1,1,0,1,1,0,1,0,0,1,0,1,1,1,0,1,1,0,0,1
arm 3: 1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,0,0,1,1,0
Allocation rule: Epsilon-greedy on a fixed schedule: the exploration rate is 1/4, so on every round r that is a multiple of 4 (r % 4 == 0) you EXPLORE by pulling the arm that has been pulled the fewest times so far; on all other rounds you EXPLOIT by pulling the arm with the highest empirical success rate (successes / pulls before that round); an arm never pulled before is treated as having rate -infinity.
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 24? Answer with a single integer.

Answer: 4

# Level 5

Prompt:
You are simulating a multi-armed bandit with 5 arms labeled 0 through 4, over 65 rounds (rounds 1..65). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,0,1,0,0,1,1,0,0,1,0,1,0,1,1,1,1,1,1,1
arm 1: 1,1,0,0,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,1,1,1,1,0,1,1,0,0,1,0,1,1,1,1,1,1,0,1,0,0,1,1,0,0,1,1,1,1,1,1,0,1,0,1,1,0,0,1,0,1,0,1,1,1
arm 2: 1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,0,1,1,0,0,1,1,1,1,1,0,1,1,1,1,1,0,1
arm 3: 0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0
arm 4: 0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0
Allocation rule: Thompson sampling over tabulated Beta posteriors: each arm starts with a Beta(1,1) prior; after s successes and f failures its posterior is Beta(1+s, 1+f). At round r draw one sample for every arm from its current posterior, where the sample is the inverse-CDF of the posterior Beta evaluated at the tabulated grid value below whose slot is assigned deterministically by slot = (arm_index*7 + r*13) mod 64. Pull the arm whose drawn sample is largest.
Tabulated grid (index -> value): 0:0.953,1:0.883,2:0.844,3:0.863,4:0.917,5:0.849,6:0.784,7:0.514,8:0.933,9:0.528,10:0.623,11:0.629,12:0.818,13:0.537,14:0.723,15:0.665,16:0.605,17:0.648,18:0.875,19:0.581,20:0.977,21:0.662,22:0.973,23:0.868,24:0.601,25:0.836,26:0.696,27:0.707,28:0.964,29:0.741,30:0.858,31:0.535,32:0.844,33:0.842,34:0.659,35:0.804,36:0.938,37:0.641,38:0.834,39:0.751,40:0.748,41:0.723,42:0.763,43:0.662,44:0.639,45:0.75,46:0.736,47:0.536,48:0.645,49:0.582,50:0.629,51:0.87,52:0.515,53:0.774,54:0.711,55:0.717,56:0.536,57:0.59,58:0.966,59:0.667,60:0.964,61:0.646,62:0.607,63:0.877
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 65? Answer with a single integer.

Answer: 1

Prompt:
You are simulating a multi-armed bandit with 5 arms labeled 0 through 4, over 66 rounds (rounds 1..66). Each arm i has a tabulated reward stream; on its j-th pull it returns stream_i[j] (1 = success, 0 = failure).
Reward streams:
arm 0: 0,0,0,1,1,1,1,1,0,0,0,0,1,0,1,0,1,0,1,1,1,0,1,1,0,0,0,1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,0,0,1,0,1,0,1,0,0,0,1,0,0,1,1,0,0,1,1,0,0,1,0,0
arm 1: 0,0,1,1,1,1,0,0,1,1,0,1,1,0,1,0,0,0,0,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1
arm 2: 1,0,1,0,1,1,1,1,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,1,0,0,1,1,0,0,1,0,1,0,1,1,0,0,0,0,0,1,1,0,1,1,0,1,1,0,1,1,1,1,0,0,1,1,1,1,1,0,1,0,1
arm 3: 0,0,0,1,1,0,0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,1,0
arm 4: 1,0,1,1,0,0,1,1,1,1,1,0,1,0,1,0,1,1,0,0,0,1,1,1,1,1,0,1,1,0,0,0,1,0,0,1,1,0,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,1,1,1,1,0,0,0,1,1,0,0,0
Allocation rule: Thompson sampling over tabulated Beta posteriors: each arm starts with a Beta(1,1) prior; after s successes and f failures its posterior is Beta(1+s, 1+f). At round r draw one sample for every arm from its current posterior, where the sample is the inverse-CDF of the posterior Beta evaluated at the tabulated grid value below whose slot is assigned deterministically by slot = (arm_index*7 + r*13) mod 64. Pull the arm whose drawn sample is largest.
Tabulated grid (index -> value): 0:0.953,1:0.883,2:0.844,3:0.863,4:0.917,5:0.849,6:0.784,7:0.514,8:0.933,9:0.528,10:0.623,11:0.629,12:0.818,13:0.537,14:0.723,15:0.665,16:0.605,17:0.648,18:0.875,19:0.581,20:0.977,21:0.662,22:0.973,23:0.868,24:0.601,25:0.836,26:0.696,27:0.707,28:0.964,29:0.741,30:0.858,31:0.535,32:0.844,33:0.842,34:0.659,35:0.804,36:0.938,37:0.641,38:0.834,39:0.751,40:0.748,41:0.723,42:0.763,43:0.662,44:0.639,45:0.75,46:0.736,47:0.536,48:0.645,49:0.582,50:0.629,51:0.87,52:0.515,53:0.774,54:0.711,55:0.717,56:0.536,57:0.59,58:0.966,59:0.667,60:0.964,61:0.646,62:0.607,63:0.877
Tie-break: whenever two or more arms tie for the arm the rule would choose, always pick the arm with the smallest index.
What is the total number of pulls received by the least-pulled arm at the end of round 66? Answer with a single integer.

Answer: 2
