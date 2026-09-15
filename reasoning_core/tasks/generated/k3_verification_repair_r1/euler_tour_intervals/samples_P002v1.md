# Level 0
A rooted tree has nodes numbered 0 (the root) through 5. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 1, 1, 1, 2]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 0 an ancestor of node 5? Answer only 'yes' or 'no'.
Answer: yes

A rooted tree has nodes numbered 0 (the root) through 5. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 0, 0, 0, 0]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 0 an ancestor of node 1? Answer only 'yes' or 'no'.
Answer: yes

# Level 2
A rooted tree has nodes numbered 0 (the root) through 11. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 1, 0, 1, 4, 0, 6, 4, 4, 6, 0]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 6 an ancestor of node 7? Answer only 'yes' or 'no'.
Answer: yes

A rooted tree has nodes numbered 0 (the root) through 11. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 0, 1, 2, 2, 4, 1, 5, 1, 3, 5]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 3 an ancestor of node 2? Answer only 'yes' or 'no'.
Answer: no

# Level 5
A rooted tree has nodes numbered 0 (the root) through 20. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 1, 1, 2, 3, 0, 5, 6, 8, 8, 0, 1, 5, 10, 3, 9, 16, 4, 5, 7]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 5 an ancestor of node 7? Answer only 'yes' or 'no'.
Answer: yes

A rooted tree has nodes numbered 0 (the root) through 20. The parent of each node k is parent[k], where parent[0] is None: [None, 0, 0, 2, 1, 3, 4, 3, 2, 0, 2, 7, 10, 1, 6, 13, 2, 12, 13, 16, 19]. Run a depth-first search from the root and stamp each node u with an entry time tin[u] and exit time tout[u] such that the subtree rooted at u occupies the contiguous interval [tin[u], tout[u]]. Using only these stamps and the subtree-interval property (u is an ancestor of v exactly when tin[u] <= tin[v] <= tout[u]), decide: is node 4 an ancestor of node 14? Answer only 'yes' or 'no'.
Answer: yes
