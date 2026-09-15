## Level 0
Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0] and sinks (net absorbers) are nodes [3].
Edges with their (capacity, flow) values:
  0 -> 1   (capacity 3, flow 1)
  0 -> 3   (capacity 3, flow 1)
  1 -> 3   (capacity 1, flow 1)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>1>3:1; 0>3:1

Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0] and sinks (net absorbers) are nodes [3].
Edges with their (capacity, flow) values:
  0 -> 3   (capacity 2, flow 2)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>3:2


## Level 2
Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0, 1] and sinks (net absorbers) are nodes [4, 5].
Edges with their (capacity, flow) values:
  0 -> 2   (capacity 1, flow 1)
  1 -> 4   (capacity 4, flow 2)
  1 -> 5   (capacity 2, flow 1)
  2 -> 3   (capacity 2, flow 1)
  3 -> 4   (capacity 1, flow 1)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>2>3>4:1; 1>4:2; 1>5:1

Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0, 1] and sinks (net absorbers) are nodes [4, 5].
Edges with their (capacity, flow) values:
  0 -> 2   (capacity 3, flow 1)
  1 -> 2   (capacity 2, flow 1)
  1 -> 4   (capacity 2, flow 2)
  2 -> 3   (capacity 3, flow 1)
  2 -> 5   (capacity 2, flow 1)
  3 -> 5   (capacity 2, flow 1)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>2>3>5:1; 1>2>5:1; 1>4:2


## Level 5
Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0, 1, 2] and sinks (net absorbers) are nodes [6, 7, 8].
Edges with their (capacity, flow) values:
  0 -> 3   (capacity 1, flow 1)
  0 -> 5   (capacity 2, flow 1)
  1 -> 3   (capacity 3, flow 1)
  1 -> 8   (capacity 3, flow 1)
  2 -> 3   (capacity 3, flow 2)
  2 -> 8   (capacity 1, flow 1)
  3 -> 4   (capacity 3, flow 2)
  3 -> 5   (capacity 1, flow 1)
  3 -> 8   (capacity 3, flow 1)
  4 -> 5   (capacity 2, flow 2)
  5 -> 6   (capacity 3, flow 3)
  5 -> 7   (capacity 2, flow 1)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>3>4>5>6:1; 0>5>6:1; 1>3>4>5>6:1; 1>8:1; 2>3>5>7:1; 2>3>8:1; 2>8:1

Prompt:
We are given a feasible integer edge flow on a directed acyclic graph together with its edge capacities. Nodes are numbered so that every edge points from a smaller to a larger number. Sources (net producers) are nodes [0, 1, 2] and sinks (net absorbers) are nodes [6, 7, 8].
Edges with their (capacity, flow) values:
  0 -> 3   (capacity 1, flow 1)
  0 -> 7   (capacity 2, flow 2)
  1 -> 3   (capacity 2, flow 1)
  1 -> 6   (capacity 2, flow 1)
  2 -> 3   (capacity 1, flow 1)
  2 -> 7   (capacity 3, flow 1)
  3 -> 4   (capacity 4, flow 3)
  4 -> 5   (capacity 2, flow 2)
  4 -> 6   (capacity 3, flow 1)
  5 -> 7   (capacity 3, flow 1)
  5 -> 8   (capacity 2, flow 1)
Decompose this flow into simple paths running from a source to a sink using the canonical greedy: repeatedly start at the smallest source still carrying flow, then at each node follow the smallest-labeled outgoing edge that still has remaining flow, stop when a sink is reached, and send one unit along that whole path. Cycle flows are excluded because the graph is acyclic. Report the resulting multiset of paths: for each distinct path write 'a>b>...>z:value' with its total flow value, list the paths sorted lexicographically, and separate them by '; '.
Answer:
0>3>4>5>7:1; 0>7:2; 1>3>4>5>8:1; 1>6:1; 2>3>4>6:1; 2>7:1

