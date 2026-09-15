## Level 0
**Example 1**
We have an undirected graph on vertices 0..3 with edges {(0, 1), (0, 2), (1, 2), (2, 3)}. The vertices 0..3 hold chips [2, 1, 0, 0]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..3, as a list of integers like [a, b, c].

Answer: [1, 0, 2, 0]

**Example 2**
We have an undirected graph on vertices 0..3 with edges {(0, 1), (1, 2), (2, 3)}. The vertices 0..3 hold chips [1, 0, 0, 0]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..3, as a list of integers like [a, b, c].

Answer: [0, 1, 0, 0]

## Level 2
**Example 1**
We have an undirected graph on vertices 0..5 with edges {(0, 1), (0, 2), (0, 3), (1, 3), (1, 5), (2, 3), (2, 5), (3, 5), (4, 5)}. The vertices 0..5 hold chips [2, 0, 1, 0, 4, 1]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..5, as a list of integers like [a, b, c].

Answer: [2, 1, 2, 1, 0, 2]

**Example 2**
We have an undirected graph on vertices 0..5 with edges {(0, 2), (1, 3), (2, 4), (2, 5), (3, 5)}. The vertices 0..5 hold chips [0, 0, 0, 1, 0, 2]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..5, as a list of integers like [a, b, c].

Answer: [0, 0, 1, 1, 0, 1]

## Level 5
**Example 1**
We have an undirected graph on vertices 0..8 with edges {(0, 5), (0, 8), (1, 2), (1, 3), (1, 6), (1, 7), (2, 3), (2, 4), (2, 5), (2, 6), (3, 4), (3, 5), (3, 7), (3, 8), (4, 6), (5, 7), (5, 8)}. The vertices 0..8 hold chips [1, 1, 2, 1, 3, 5, 2, 0, 0]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..8, as a list of integers like [a, b, c].

Answer: [0, 3, 0, 4, 2, 2, 1, 1, 2]

**Example 2**
We have an undirected graph on vertices 0..8 with edges {(0, 2), (0, 4), (0, 6), (0, 7), (0, 8), (1, 2), (1, 6), (1, 7), (2, 4), (3, 6), (4, 5), (4, 8), (5, 7)}. The vertices 0..8 hold chips [3, 1, 2, 0, 2, 2, 2, 2, 1]. Repeatedly fire any vertex that has at least as many chips as its degree: firing removes degree-many chips from it and adds one chip to each of its neighbors. Continue until no vertex is overloaded. Return the final stable chip vector for vertices 0..8, as a list of integers like [a, b, c].

Answer: [4, 2, 2, 0, 3, 1, 2, 0, 1]
