## Level 0

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {ab}:
S -> Bb | SB
A -> bb | S
B -> bb | Ab

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 3) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 3). Example format: 'yes abab' or 'no'.

Answer:

no

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {ab}:
S -> b
A -> Ba | aA
B -> B | a

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 3) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 3). Example format: 'yes abab' or 'no'.

Answer:

no

## Level 2

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {bc}:
S -> bb | A
A -> A
B -> b

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 5) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 5). Example format: 'yes abab' or 'no'.

Answer:

no

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {ac}:
S -> S | S
A -> aS
B -> cc

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 5) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 5). Example format: 'yes abab' or 'no'.

Answer:

no

## Level 5

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {ac}:
S -> A
A -> X | Y
X -> a
Y -> a

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 8) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 8). Example format: 'yes abab' or 'no'.

Answer:

yes a

### Example

Prompt:

Consider the context-free grammar with start symbol S over the terminal alphabet {bc}:
S -> A
A -> X | Y
X -> c
Y -> c

Search the grammar's derivations for ambiguity. A word is unambiguous if every derivation of it gives the same parse tree; the grammar is ambiguous if some word has two distinct parse trees. Enumerate sentential forms by length to find the shortest word (of length at most 8) with two distinct parse trees. If the grammar is ambiguous, answer with 'yes <word>' giving that shortest word; otherwise answer 'no' (no ambiguous word up to length 8). Example format: 'yes abab' or 'no'.

Answer:

yes c
