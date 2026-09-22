# Level 0

```
A Post tag system has a deletion number m=2 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['c', 'f'], productions: c -> 'c'; f -> 'ff'. Start word: cf.

Using the standard simulation of a tag system, answer how many production steps are applied before the word shrinks below 2 symbols and the system halts.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: 1

```
A Post tag system has a deletion number m=2 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['b', 'e'], productions: b -> 'e'; e -> 'e'. Start word: eb.

Using the standard simulation of a tag system, answer how many production steps are applied before the word shrinks below 2 symbols and the system halts.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: 1

# Level 2

```
A Post tag system has a deletion number m=3 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['b', 'd', 'e', 'f'], productions: b -> 'db'; d -> 'eb'; e -> 'db'; f -> 'f'. Start word: bddf.

Using the standard simulation of a tag system, answer what the word is after exactly 2 steps; if the system halts earlier the word stays at its halting word.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: f

```
A Post tag system has a deletion number m=3 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['b', 'd', 'e', 'f'], productions: b -> 'e'; d -> 'd'; e -> 'e'; f -> 'e'. Start word: dbbbbf.

Using the standard simulation of a tag system, answer what the word is after exactly 2 steps; if the system halts earlier the word stays at its halting word.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: de

# Level 5

```
A Post tag system has a deletion number m=2 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['a', 'b', 'c', 'd', 'e'], productions: a -> 'b'; b -> 'e'; c -> 'a'; d -> 'e'; e -> 'b'. Start word: eaacbbcbebde.

Using the standard simulation of a tag system, answer how many production steps are applied before the word shrinks below 2 symbols and the system halts.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: 11

```
A Post tag system has a deletion number m=2 and a production for each alphabet symbol. At every step it reads the first (head) symbol, deletes the first m symbols, and appends the production of the head symbol. It halts exactly when the word has fewer than m symbols. Alphabet = ['a', 'b', 'd', 'e', 'f'], productions: a -> 'f'; b -> 'e'; d -> 'b'; e -> 'd'; f -> 'a'. Start word: adedadeadbbb.

Using the standard simulation of a tag system, answer what the final (halting) word is; if it becomes empty answer exactly: empty.
Give only the answer: an exact string of letters (type "empty" for the empty word) when the answer is a word, or the integer step count when asked for steps.
```
Answer: d

