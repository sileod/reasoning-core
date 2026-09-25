## Level 0

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|(0,1)  =>  0|



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1|(0,1)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. Give the full sequence of graphs reached, including the start graph and the graph after every single application, joined with '->'. For example a valid answer format is  0,1,2|(0,1),(1,2)->0,1,2|(1,2) .

**Answer:**

0,1|(0,1)->2|

---

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|  =>  0|   (blocked whenever a copy of 0,1,2|(0,2),(1,2) also extends the match)



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1,2|(0,1),(0,2),(1,2)



Target subgraph: 0,1,2|(0,1),(0,2),(1,2)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. In the resulting graph, is the target subgraph present? Answer Yes or No.

**Answer:**

Yes

---

## Level 2

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|  =>  0|



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1,2|(0,2)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. Give the full sequence of graphs reached, including the start graph and the graph after every single application, joined with '->'. For example a valid answer format is  0,1,2|(0,1),(1,2)->0,1,2|(1,2) .

**Answer:**

0,1,2|(0,2)->2,3|->0|

---

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|(0,1)  =>  0|   (blocked whenever a copy of 0,1,2,3|(0,1),(0,3),(1,2),(1,3) also extends the match)



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1,2,3,4|(0,1),(0,2)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. Give the full sequence of graphs reached, including the start graph and the graph after every single application, joined with '->'. For example a valid answer format is  0,1,2|(0,1),(1,2)->0,1,2|(1,2) .

**Answer:**

0,1,2,3,4|(0,1),(0,2)->2,3,4,5|

---

## Level 5

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|(0,1)  =>  0|   (blocked whenever a copy of 0,1,2|(0,1),(0,2),(1,2) also extends the match)



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1,2|(0,1),(0,2)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. What is the total number of applications? Answer with a single integer.

**Answer:**

1

---

### Example

**Prompt:**

You are working with a graph rewriting system. A graph is written as <nodes>|<edges>, where <nodes> is a comma-separated list of node labels and <edges> a comma-separated list of unordered edges. For example the graph with nodes 0,1,2 and edges (0,1),(1,2) is written  0,1,2|(0,1),(1,2) , and a graph with two nodes and no edges is written  0,1| .



A rewrite rule  A => B  replaces an occurrence of subgraph A with subgraph B. When the rule is applied, the matched nodes of A are deleted together with every edge incident to them (any dangling edge), and the nodes of B are added with fresh labels together with their listed edges.



The rule is:

  0,1|  =>  0|



When applying the rule repeatedly, always pick the lexicographically smallest match: list the images of the left-side nodes in order of their labels and choose the lexicographically smallest such tuple.



Start graph: 0,1,2,3,4,5,6|(1,5),(1,6),(2,4),(2,5),(2,6),(3,6),(5,6)



Starting from the start graph, repeatedly apply the rule at the lexicographically smallest match until the rule can no longer be applied. What is the total number of applications? Answer with a single integer.

**Answer:**

6

---

