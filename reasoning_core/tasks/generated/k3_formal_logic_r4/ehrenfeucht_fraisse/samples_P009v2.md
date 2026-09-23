# Ehrenfeucht-Fraisse game v2 - samples

Assigned semantics: answer the winning player and, when Spoiler wins, the
lexicographically smallest vertex pair (A-vertex, B-vertex) that guarantees
Spoiler a win.

## Level 0

### Example 1

**Prompt:**

Two players play the 2-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {e, c} and edges e-c.
Graph B has vertices {q, p} and edges none.
Who wins the 2-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Spoiler; c,p

### Example 2

**Prompt:**

Two players play the 2-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {c, d} and edges none.
Graph B has vertices {q, t} and edges none.
Who wins the 2-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Duplicator

## Level 2

### Example 1

**Prompt:**

Two players play the 3-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {d, a, e} and edges d-e.
Graph B has vertices {q, s, p} and edges q-p, q-s, s-p.
Who wins the 3-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Spoiler; a,p

### Example 2

**Prompt:**

Two players play the 3-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {e, a, c} and edges a-c.
Graph B has vertices {s, q, t} and edges q-t.
Who wins the 3-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Duplicator

## Level 5

### Example 1

**Prompt:**

Two players play the 4-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {b, c, e, d} and edges b-d, c-e.
Graph B has vertices {s, r, p, t} and edges s-t.
Who wins the 4-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Spoiler; b,p

### Example 2

**Prompt:**

Two players play the 4-round Ehrenfeucht-Fraisse game on two undirected graphs A and B. In each round Spoiler picks a vertex in either graph, then Duplicator picks a vertex in the other graph. After all rounds, if the chosen vertices of A and B form an isomorphism of the induced subgraphs, Duplicator wins; otherwise Spoiler wins.
Graph A has vertices {d, e, c, a} and edges c-a, d-e.
Graph B has vertices {t, p, s, q} and edges p-s, s-q, t-p, t-s.
Who wins the 4-round game? If Duplicator wins, answer exactly 'Duplicator'. If Spoiler wins, answer 'Spoiler; <a>,<b>' where <a>,<b> is the lexicographically smallest pair (A-vertex, B-vertex, compared by these vertex names) such that Spoiler can guarantee a win by opening on that pair.

**Answer:**

Spoiler; a,p

