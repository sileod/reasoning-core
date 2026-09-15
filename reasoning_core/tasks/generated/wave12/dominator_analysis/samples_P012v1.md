## Level 0

### Example

Consider the directed control-flow graph on nodes 0..5 with entry node 0 and edges (0->3), (1->4), (2->0), (3->1), (5->2). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 0 dominate node 4? Answer exactly 'yes' or 'no'.

Answer: yes

### Example

Consider the directed control-flow graph on nodes 0..5 with entry node 0 and edges (0->3), (1->0), (1->4), (2->0), (3->5), (4->2). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 5 dominate node 3? Answer exactly 'yes' or 'no'.

Answer: no


## Level 2

### Example

Consider the directed control-flow graph on nodes 0..9 with entry node 0 and edges (0->1), (0->4), (1->0), (2->9), (4->6), (5->0), (5->8), (6->7), (6->8), (7->3), (8->1), (9->5). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 8 dominate node 8? Answer exactly 'yes' or 'no'.

Answer: yes

### Example

Consider the directed control-flow graph on nodes 0..9 with entry node 0 and edges (0->6), (1->0), (1->7), (2->0), (2->8), (3->0), (4->2), (6->1), (7->4), (8->5), (9->3), (9->4). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 1 dominate node 8? Answer exactly 'yes' or 'no'.

Answer: no


## Level 5

### Example

Consider the directed control-flow graph on nodes 0..15 with entry node 0 and edges (0->7), (0->13), (1->14), (2->13), (3->2), (4->9), (4->10), (5->4), (5->6), (6->3), (7->9), (8->3), (9->8), (9->13), (10->8), (10->15), (11->0), (12->1), (13->5), (14->6), (15->11). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 1 dominate node 1? Answer exactly 'yes' or 'no'.

Answer: yes

### Example

Consider the directed control-flow graph on nodes 0..15 with entry node 0 and edges (0->9), (1->14), (2->10), (3->11), (5->7), (6->5), (7->1), (7->10), (8->15), (9->12), (9->13), (10->7), (10->12), (11->4), (12->3), (13->0), (13->8), (14->2), (14->9), (15->6). A node X dominates node Y if every path from the entry to Y passes through X (X dominates itself). Does node 14 dominate node 6? Answer exactly 'yes' or 'no'.

Answer: no

