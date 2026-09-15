# Samples for P010v2: tree_reroot_distances

Assigned design choice: Return only the rerooted total distance for a single queried node, with the query node chosen uniformly at random per instance, and the answer is that integer.

Each example shows the generated prompt verbatim and its gold answer.

## Level 0

**Example 1**

Prompt:

    A connected, undirected tree on 6 nodes labeled 0..5 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 3 to every other node, and return that total as a single integer.
    Edges:
      0-1
      1-2
      0-3
      0-4
      1-5
    Query node: 3
    Answer: one integer.

Answer: 11

**Example 2**

Prompt:

    A connected, undirected tree on 6 nodes labeled 0..5 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 1 to every other node, and return that total as a single integer.
    Edges:
      0-1
      1-2
      0-3
      2-4
      0-5
    Query node: 1
    Answer: one integer.

Answer: 8

## Level 2

**Example 1**

Prompt:

    A connected, undirected tree on 24 nodes labeled 0..23 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 11 to every other node, and return that total as a single integer.
    Edges:
      0-1
      1-2
      0-3
      1-4
      3-5
      0-6
      6-7
      6-8
      0-9
      0-10
      2-11
      3-12
      4-13
      8-14
      9-15
      14-16
      13-17
      11-18
      4-19
      17-20
      12-21
      14-22
      12-23
    Query node: 11
    Answer: one integer.

Answer: 102

**Example 2**

Prompt:

    A connected, undirected tree on 26 nodes labeled 0..25 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 6 to every other node, and return that total as a single integer.
    Edges:
      0-1
      1-2
      2-3
      2-4
      0-5
      3-6
      4-7
      1-8
      5-9
      3-10
      2-11
      9-12
      4-13
      12-14
      3-15
      7-16
      7-17
      7-18
      14-19
      3-20
      7-21
      20-22
      11-23
      16-24
      2-25
    Query node: 6
    Answer: one integer.

Answer: 105

## Level 5

**Example 1**

Prompt:

    A connected, undirected tree on 69 nodes labeled 0..68 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 30 to every other node, and return that total as a single integer.
    Edges:
      0-1
      0-2
      2-3
      2-4
      1-5
      5-6
      4-7
      3-8
      1-9
      7-10
      2-11
      5-12
      6-13
      13-14
      13-15
      15-16
      12-17
      11-18
      1-19
      11-20
      6-21
      4-22
      8-23
      2-24
      21-25
      5-26
      1-27
      5-28
      3-29
      27-30
      22-31
      9-32
      28-33
      10-34
      17-35
      20-36
      4-37
      13-38
      19-39
      31-40
      2-41
      6-42
      30-43
      36-44
      33-45
      27-46
      43-47
      15-48
      37-49
      36-50
      37-51
      26-52
      0-53
      11-54
      52-55
      32-56
      21-57
      45-58
      26-59
      12-60
      58-61
      19-62
      36-63
      24-64
      30-65
      51-66
      38-67
      49-68
    Query node: 30
    Answer: one integer.

Answer: 363

**Example 2**

Prompt:

    A connected, undirected tree on 57 nodes labeled 0..56 has edges of weight 1, so the distance between two nodes is the number of edges on the path connecting them. The tree is given below as its edges. Use the two-pass rerooting ('re-rooting') tree DP: a bottom-up pass that accumulates, for each node, the sum of the distances from it to all nodes in its own subtree, followed by a top-down pass that reroots across every edge with the shift (n - 2*subtree_size of the child). Compute the sum of the distances from node 50 to every other node, and return that total as a single integer.
    Edges:
      0-1
      0-2
      0-3
      3-4
      1-5
      1-6
      1-7
      2-8
      5-9
      6-10
      1-11
      6-12
      0-13
      11-14
      12-15
      11-16
      13-17
      9-18
      17-19
      16-20
      2-21
      0-22
      7-23
      9-24
      23-25
      11-26
      6-27
      26-28
      24-29
      10-30
      10-31
      24-32
      22-33
      6-34
      7-35
      17-36
      28-37
      6-38
      35-39
      16-40
      4-41
      31-42
      28-43
      22-44
      43-45
      39-46
      27-47
      12-48
      37-49
      13-50
      47-51
      46-52
      33-53
      7-54
      29-55
      55-56
    Query node: 50
    Answer: one integer.

Answer: 291
