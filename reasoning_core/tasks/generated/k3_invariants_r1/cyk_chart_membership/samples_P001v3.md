## Level 0

### Example 1

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N2 N2
N1 -> a
N1 -> b
N2 -> N1 S
N2 -> a
S -> N1 N2
S -> N2 N2
S -> S N1
S -> a

The input terminal string is: aaab

Run CYK recognition on this string and count the total number of distinct derivation trees (parses) of the whole string rooted at the start symbol S. Answer with that count as a non-negative integer.
```

Answer:
```
10
```

### Example 2

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N1 N2
N1 -> S S
N1 -> b
N2 -> S N2
N2 -> a
N2 -> b
S -> N1 N1
S -> a
S -> b

The input terminal string is: bbab

Run CYK recognition on this string. A chart cell is indexed by an interval [a, b) of string positions. Write down the nonterminals in the cell for the interval [1, 2); an empty cell is recorded as the single word EMPTY. List the nonterminals in sorted lexicographic order.
```

Answer:
```
N1 N2 S
```

## Level 2

### Example 1

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N2 N1
N1 -> N2 N2
N1 -> N2 S
N1 -> a
N1 -> b
N2 -> N1 N3
N2 -> N2 N2
N2 -> a
N3 -> N3 S
N3 -> a
N3 -> b
S -> N1 N3
S -> N2 N1
S -> S N3
S -> b

The input terminal string is: aababb

Run CYK recognition on this string. A chart cell is indexed by an interval [a, b) of string positions. Write down the nonterminals in the cell for the interval [1, 2); an empty cell is recorded as the single word EMPTY. List the nonterminals in sorted lexicographic order.
```

Answer:
```
N1 N2 N3
```

### Example 2

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N1 N3
N1 -> N3 N3
N1 -> a
N2 -> N2 N2
N2 -> N3 S
N2 -> b
N3 -> N3 S
N3 -> b
S -> N1 N3
S -> N2 N3
S -> S N3
S -> S S
S -> a

The input terminal string is: babbba

Run CYK recognition on this string. A chart cell is indexed by an interval [a, b) of string positions. Write down the nonterminals in the cell for the interval [1, 2); an empty cell is recorded as the single word EMPTY. List the nonterminals in sorted lexicographic order.
```

Answer:
```
N1 S
```

## Level 5

### Example 1

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N1 N2
N1 -> N1 N3
N1 -> N2 S
N1 -> a
N1 -> b
N2 -> N1 N2
N2 -> N3 N3
N2 -> N3 N4
N2 -> N4 N4
N2 -> b
N3 -> N2 S
N3 -> N4 N4
N4 -> S N4
N4 -> b
S -> N1 N2
S -> S N4
S -> S S
S -> a

The input terminal string is: bbabababb

Run CYK recognition on this string. A chart cell is indexed by an interval [a, b) of string positions. Write down the nonterminals in the cell for the interval [7, 9); an empty cell is recorded as the single word EMPTY. List the nonterminals in sorted lexicographic order.
```

Answer:
```
N1 N2 N3 S
```

### Example 2

Prompt:
```
A small grammar in Chomsky normal form is given:
N1 -> N1 N4
N1 -> N4 N4
N1 -> a
N2 -> N4 N1
N2 -> a
N3 -> N2 N3
N3 -> N2 N4
N3 -> N3 N4
N3 -> S S
N3 -> a
N3 -> b
N4 -> N1 N1
N4 -> N3 N4
N4 -> a
N4 -> b
S -> N2 N1
S -> N4 N3
S -> S N4

The input terminal string is: bbaabaaaa

Run CYK recognition on this string and count the total number of distinct derivation trees (parses) of the whole string rooted at the start symbol S. Answer with that count as a non-negative integer.
```

Answer:
```
142771
```
