# Level 0
PROMPT:
Points (index 0 first): (8,7) (7,4) (5,6) (9,1) (8,3) (2,2). Coordinate directions, in order: min max, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. Strip the iterated Pareto fronts, numbered outwards from 1. Report the indices of the points in layer 1, in increasing index order, space-separated.
Answer: 0 3

PROMPT:
Points (index 0 first): (0,3) (3,8) (2,4) (4,2) (0,0) (0,2). Coordinate directions, in order: min min, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. For each queried pair (i,j), write 'D' if point i dominates or is strictly better than point j, 'E' if the two points are equal, otherwise 'N'. Queries: query (1,0); query (2,3); query (5,5); query (0,1). Give one symbol per query in order, space-separated.
Answer: N N E D

# Level 2
PROMPT:
Points (index 0 first): (0,2) (7,6) (2,8) (9,2) (7,4) (5,9) (0,3) (4,4) (2,1) (1,3). Coordinate directions, in order: min min, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. For each point in index order, report how many OTHER points dominate it, space-separated.
Answer: 8 0 1 0 1 0 6 3 6 5

PROMPT:
Points (index 0 first): (5,7) (6,9) (6,1) (9,4) (4,7) (7,3) (8,8) (3,1) (1,3) (1,0). Coordinate directions, in order: min max, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. For each point in index order, report how many OTHER points dominate it, space-separated.
Answer: 2 0 4 0 3 2 0 7 6 9

# Level 5
PROMPT:
Points (index 0 first): (4,6,0,2) (7,8,6,9) (7,9,7,5) (8,1,4,8) (7,7,1,5) (6,3,2,4) (4,0,2,5) (4,2,0,2) (5,0,4,0) (8,1,8,7) (8,1,3,4) (8,6,6,1) (6,9,1,2) (0,9,9,9) (0,3,6,9) (3,3,6,5). Coordinate directions, in order: min max min max, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. For each queried pair (i,j), write 'D' if point i dominates or is strictly better than point j, 'E' if the two points are equal, otherwise 'N'. Queries: query (6,7); query (8,11); query (11,0); query (13,8). Give one symbol per query in order, space-separated.
Answer: N N N N

PROMPT:
Points (index 0 first): (4,0,8,2) (4,7,9,0) (9,5,9,3) (4,0,1,4) (2,8,3,9) (5,7,9,6) (9,0,2,2) (9,2,3,8) (0,5,9,2) (5,9,0,2) (4,4,5,7) (1,1,0,3) (7,6,6,9) (3,6,6,7) (3,4,1,7) (0,9,9,4). Coordinate directions, in order: min min min min, where 'max' means larger is better and 'min' means smaller is better. Under Pareto dominance, a point dominates another when it is at least as good in every coordinate and strictly better in at least one. Strip the iterated Pareto fronts: the set of points not dominated by anything else is the first (outermost) front, layer 1; removing it reveals layer 2, and so on. Give, for each point in index order, its layer number, space-separated (e.g., '1 2 1 3').
Answer: 2 2 1 3 1 1 2 1 2 1 2 4 1 2 3 1

