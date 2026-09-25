# Samples P008v1

## Level 0

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 2, state 2 has weight 4, state 3 has weight 2.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3
    | ---|---|---|---
    | A1 | 8 | 5 | 12
    | A2 | 6 | 0 | 1
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Fern costs 2: outcome 1 (prior weight 4) contains states st2; outcome 2 (prior weight 4) contains states st1, st3.
    Experiment Dune costs 8: outcome 1 (prior weight 6) contains states st2, st3; outcome 2 (prior weight 2) contains states st1.
    Experiment Amber costs 3: outcome 1 (prior weight 2) contains states st1; outcome 2 (prior weight 6) contains states st2, st3.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Fern

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 5, state 2 has weight 2, state 3 has weight 3.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3
    | ---|---|---|---
    | A1 | -1 | -4 | -8
    | A2 | -9 | -8 | -5
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Echo costs 4: outcome 1 (prior weight 7) contains states st1, st2; outcome 2 (prior weight 3) contains states st3.
    Experiment Amber costs 2: outcome 1 (prior weight 2) contains states st2; outcome 2 (prior weight 8) contains states st1, st3.
    Experiment Beryl costs 8: outcome 1 (prior weight 2) contains states st2; outcome 2 (prior weight 8) contains states st1, st3.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Amber

## Level 2

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 5, state 2 has weight 2, state 3 has weight 4, state 4 has weight 3, state 5 has weight 3.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3 | st4 | st5
    | ---|---|---|---|---|---
    | A1 | 9 | -9 | -2 | 0 | -1
    | A2 | -5 | -6 | -6 | 12 | -2
    | A3 | 7 | 0 | 0 | -2 | 1
    | A4 | 12 | 6 | 3 | 10 | 3
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Amber costs 1: outcome 1 (prior weight 10) contains states st1, st2, st5; outcome 2 (prior weight 3) contains states st4; outcome 3 (prior weight 4) contains states st3.
    Experiment Echo costs 5: outcome 1 (prior weight 9) contains states st2, st3, st4; outcome 2 (prior weight 5) contains states st1; outcome 3 (prior weight 3) contains states st5.
    Experiment Cobalt costs 0: outcome 1 (prior weight 6) contains states st4, st5; outcome 2 (prior weight 9) contains states st1, st3; outcome 3 (prior weight 2) contains states st2.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Cobalt

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 2, state 2 has weight 4, state 3 has weight 5, state 4 has weight 4, state 5 has weight 5.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3 | st4 | st5
    | ---|---|---|---|---|---
    | A1 | 6 | 9 | 6 | 1 | 11
    | A2 | 12 | 7 | -6 | 0 | 8
    | A3 | 12 | 6 | 11 | 12 | 6
    | A4 | -6 | 2 | 3 | -3 | -5
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Cobalt costs 5: outcome 1 (prior weight 4) contains states st4; outcome 2 (prior weight 2) contains states st1; outcome 3 (prior weight 14) contains states st2, st3, st5.
    Experiment Fern costs 8: outcome 1 (prior weight 11) contains states st1, st2, st3; outcome 2 (prior weight 5) contains states st5; outcome 3 (prior weight 4) contains states st4.
    Experiment Amber costs 6: outcome 1 (prior weight 8) contains states st2, st4; outcome 2 (prior weight 5) contains states st5; outcome 3 (prior weight 7) contains states st1, st3.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Cobalt

## Level 5

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 5, state 2 has weight 1, state 3 has weight 2, state 4 has weight 1, state 5 has weight 5, state 6 has weight 5, state 7 has weight 5, state 8 has weight 1.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3 | st4 | st5 | st6 | st7 | st8
    | ---|---|---|---|---|---|---|---|---
    | A1 | -3 | 3 | 9 | -2 | -2 | 4 | 1 | 10
    | A2 | -3 | -1 | 2 | 4 | 12 | -9 | -1 | 4
    | A3 | 5 | 9 | 1 | 0 | -9 | 7 | -4 | 0
    | A4 | 12 | 11 | 5 | 9 | -9 | 10 | 1 | 9
    | A5 | -2 | 0 | -9 | -7 | 0 | -4 | 7 | -3
    | A6 | 10 | 2 | 6 | 9 | 4 | 9 | -8 | -4
    | A7 | -5 | 10 | -5 | -3 | 7 | -9 | 2 | 10
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Fern costs 7: outcome 1 (prior weight 1) contains states st4; outcome 2 (prior weight 1) contains states st8; outcome 3 (prior weight 10) contains states st5, st7; outcome 4 (prior weight 13) contains states st1, st2, st3, st6.
    Experiment Beryl costs 1: outcome 1 (prior weight 9) contains states st3, st4, st7, st8; outcome 2 (prior weight 5) contains states st6; outcome 3 (prior weight 10) contains states st1, st5; outcome 4 (prior weight 1) contains states st2.
    Experiment Cobalt costs 8: outcome 1 (prior weight 11) contains states st1, st7, st8; outcome 2 (prior weight 7) contains states st3, st6; outcome 3 (prior weight 6) contains states st4, st5; outcome 4 (prior weight 1) contains states st2.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Beryl

**Prompt:**

    You must choose one action, but the reward each action yields depends on an unknown state of the world. The states are listed with their prior likelihood weights (relative to each other): state 1 has weight 6, state 2 has weight 4, state 3 has weight 3, state 4 has weight 2, state 5 has weight 6, state 6 has weight 1, state 7 has weight 3, state 8 has weight 5.
    
    The reward table below gives, for each action and each state, the reward of taking that action when that state is true (rows are actions, columns are states):
    
    | Action | st1 | st2 | st3 | st4 | st5 | st6 | st7 | st8
    | ---|---|---|---|---|---|---|---|---
    | A1 | 9 | 4 | -6 | 3 | -5 | 0 | 2 | 1
    | A2 | 2 | 6 | 4 | -9 | 3 | 10 | 0 | 10
    | A3 | 10 | -7 | 11 | 5 | -6 | 1 | -7 | 6
    | A4 | 8 | -3 | -9 | -5 | 4 | 4 | -8 | 7
    | A5 | 0 | 8 | 4 | 12 | -5 | -3 | -2 | -2
    | A6 | 10 | 10 | 10 | -7 | -8 | -8 | -5 | 1
    | A7 | 2 | 10 | 7 | -1 | -6 | -1 | 6 | -3
    
    Before choosing, you may run exactly one experiment at its listed cost. Each experiment reveals which of its outcomes holds; the outcomes of an experiment are a partition of the states (each state belongs to exactly one outcome), and each outcome lists the states in it and its prior likelihood weight. Given an outcome, the state is one of the states in that outcome with posterior proportional to the prior weights.
    
    Experiment Echo costs 5: outcome 1 (prior weight 18) contains states st1, st5, st6, st8; outcome 2 (prior weight 7) contains states st2, st3; outcome 3 (prior weight 2) contains states st4; outcome 4 (prior weight 3) contains states st7.
    Experiment Beryl costs 7: outcome 1 (prior weight 12) contains states st3, st6, st7, st8; outcome 2 (prior weight 2) contains states st4; outcome 3 (prior weight 12) contains states st1, st5; outcome 4 (prior weight 4) contains states st2.
    Experiment Amber costs 6: outcome 1 (prior weight 16) contains states st1, st5, st6, st7; outcome 2 (prior weight 7) contains states st4, st8; outcome 3 (prior weight 4) contains states st2; outcome 4 (prior weight 3) contains states st3.
    
    Compute the expected value of information for each experiment: for every outcome, take the best expected reward under that outcome's posterior distribution, then average those best rewards over the outcomes weighted by their prior, and subtract the best expected reward achievable with no test and the experiment's cost. Return the name of the experiment (Amber, Beryl, Cobalt, ...) with the highest expected net value; if two tie, the one whose name comes first alphabetically. Give only the experiment name as your answer.

**Answer:**

    Echo

