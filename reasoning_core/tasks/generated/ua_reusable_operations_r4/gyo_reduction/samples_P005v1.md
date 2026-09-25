## Level 0
A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={0,1} e1={1,2}
Answer:

Answer: v0 v2 BLOCKED

A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={0,2} e1={0,1,2}
Answer:

Answer: v1 BLOCKED

## Level 2
A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={0,1,3} e1={0,1,2,3} e2={2,3} e3={1,3}
Answer:

Answer: e0 v0 e2 v2 BLOCKED

A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={0,1,2,3} e1={1,3} e2={0,3}
Answer:

Answer: v2 e1 v1 BLOCKED

## Level 5
A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={2,3} e1={0,1}
Answer:

Answer: v0 v1 v2 v3 EMPTY

A hypergraph's vertices are the integers appearing in its edges, listed as e0,e1,... Reduce it to emptiness with repeated GYO steps:
1. If a vertex appears in exactly one edge, delete that vertex from that edge (step 'v<vertex>').
2. Otherwise, if one edge is a proper subset of another edge, delete the contained edge (step 'e<edge-index>').
Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies (final word BLOCKED).
Answer with the steps in order followed by the final word, space-separated. Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.
Edges: e0={2,3} e1={0,1,2,3} e2={1,2} e3={0,1,2} e4={1,2,3}
Answer:

Answer: e0 e2 e3 v0 BLOCKED
