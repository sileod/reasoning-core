# Samples for P004v2: tree_subset_counting_dp

### Level 0

**Prompt:**
We count vertex covers in a rooted tree with 6 nodes labeled 0, 1, 2, 3, 4, 5, root 0. A vertex cover is a set of vertices that touches every edge (every edge has at least one endpoint in the set). The tree's parent links are (1->0, 2->1, 3->1, 4->2, 5->3). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the exact number (a non-negative integer). The answer is a single integer with no extra text.

**Answer:**
22

### Level 0

**Prompt:**
We count matchings in a rooted tree with 6 nodes labeled 0, 1, 2, 3, 4, 5, root 0. A matching is a set of edges no two of which share a vertex. The tree's parent links are (1->0, 2->0, 3->2, 4->1, 5->0). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the exact number (a non-negative integer). The answer is a single integer with no extra text.

**Answer:**
12

### Level 2

**Prompt:**
We count independent sets in a rooted tree with 14 nodes labeled 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, root 0. A independent set is a set of vertices no two of which are joined by an edge. The tree's parent links are (1->0, 2->0, 3->1, 4->0, 5->0, 6->5, 7->2, 8->2, 9->1, 10->6, 11->4, 12->2, 13->2). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the number modulo 999999937, giving one integer in {0, 1, ..., 999999936}. The answer is a single integer with no extra text.

**Answer:**
1659

### Level 2

**Prompt:**
We count matchings in a rooted tree with 6 nodes labeled 0, 1, 2, 3, 4, 5, root 0. A matching is a set of edges no two of which share a vertex. The tree's parent links are (1->0, 2->0, 3->0, 4->2, 5->4). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the exact number (a non-negative integer). The answer is a single integer with no extra text.

**Answer:**
11

### Level 5

**Prompt:**
We count vertex covers in a rooted tree with 12 nodes labeled 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, root 0. A vertex cover is a set of vertices that touches every edge (every edge has at least one endpoint in the set). The tree's parent links are (1->0, 2->1, 3->2, 4->0, 5->4, 6->5, 7->4, 8->3, 9->4, 10->8, 11->8). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the exact number (a non-negative integer). The answer is a single integer with no extra text.

**Answer:**
490

### Level 5

**Prompt:**
We count vertex covers in a rooted tree with 25 nodes labeled 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, root 0. A vertex cover is a set of vertices that touches every edge (every edge has at least one endpoint in the set). The tree's parent links are (1->0, 2->0, 3->2, 4->2, 5->2, 6->5, 7->2, 8->1, 9->4, 10->5, 11->10, 12->4, 13->5, 14->0, 15->11, 16->1, 17->6, 18->16, 19->4, 20->1, 21->1, 22->14, 23->20, 24->4). Compute the count by bottom-up dynamic programming at each node, combining child subtrees into one count per node. Report the number modulo 999999937, giving one integer in {0, 1, ..., 999999936}. The answer is a single integer with no extra text.

**Answer:**
527616

