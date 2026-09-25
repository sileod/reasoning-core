# rigidity_brace_design samples

## Level 0

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(0,0), 1:(2,2), 2:(1,2), 3:(1,0).
Joints 0, 3 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 1-0, 2-0, 2-3.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 0-3(cost=1), 1-3(cost=5).
The completed truss must be infinitesimally rigid: the only infinitesimal motion of its free joints is the zero motion (no remaining freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

1-3

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(0,0), 1:(0,3), 2:(3,0), 3:(2,1).
Joints 0, 2 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 3-2.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 0-3(cost=5), 1-0(cost=9), 1-2(cost=18), 3-0(cost=5).
The completed truss must be infinitesimally rigid: the only infinitesimal motion of its free joints is the zero motion (no remaining freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

0-3,1-0,1-2

## Level 2

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(2,1), 1:(2,0), 2:(1,2), 3:(0,3), 4:(0,0), 5:(0,2).
Joints 2, 4 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 0-4, 1-2, 1-4, 3-2, 5-4.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 0-2(cost=2), 1-5(cost=8), 2-5(cost=1), 3-4(cost=9), 5-2(cost=1).
The completed truss must be infinitesimally rigid: the only infinitesimal motion of its free joints is the zero motion (no remaining freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

0-2,2-5,3-4

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(0,1), 1:(2,2), 2:(1,1), 3:(2,1), 4:(1,2), 5:(0,0).
Joints 1, 3 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 0-1, 2-1, 2-3, 4-1, 4-3, 5-1, 5-3.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 0-3(cost=4), 3-5(cost=5), 4-5(cost=5).
The completed truss must be infinitesimally rigid: the only infinitesimal motion of its free joints is the zero motion (no remaining freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

0-3

## Level 5

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(1,2), 1:(0,0), 2:(2,1), 3:(2,0), 4:(2,2), 5:(0,3), 6:(1,1), 7:(0,2), 8:(1,0).
Joints 2, 8 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 0-2, 0-8, 1-2, 1-8, 3-2, 3-8, 4-2, 4-8, 6-2, 6-8, 7-2, 7-8.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 0-5(cost=2), 1-3(cost=4), 1-7(cost=4), 2-5(cost=8), 5-8(cost=10).
The completed truss must have exactly one infinitesimal freedom: joint 5 may rotate about fixed joint 8, and no other joint may move (no other freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

5-8

**Prompt:**

A pin-jointed truss in the plane has joints (index: x,y):
0:(0,2), 1:(2,0), 2:(2,2), 3:(0,1), 4:(3,0), 5:(1,1), 6:(1,0), 7:(2,1), 8:(1,2).
Joints 0, 3 are anchored to the ground (their velocity is fixed to zero).
The bars already present are: 1-0, 1-3, 2-0, 2-3, 5-0, 5-3, 6-0, 6-3, 7-0, 7-3, 8-0, 8-3.
You may add any of these permitted bars (cost = squared bar length, given in parentheses): 2-8(cost=1), 3-8(cost=2).
The completed truss must have exactly one infinitesimal freedom: joint 4 may rotate about fixed joint 3, and no other joint may move (no other freedom).
With the smallest possible total cost, give the bar(s) to add so the completed truss has precisely that motion space. If it is impossible, answer 'impossible'. If the current truss already realizes it, answer 'none'. Otherwise answer the added bars as a comma-separated list of 'i-j' pairs sorted increasingly (fewest bars first on cost ties, then lexicographic), e.g. '1-4,2-5'.

**Answer:**

impossible

