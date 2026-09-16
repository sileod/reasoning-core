# Markov Algorithm Execution - samples P004v1

## Level 0

### Example 1

**Prompt:**

This is a Markov algorithm over the alphabet abc.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. c ->
2. b ->
3. bc ->
Start word: acabba
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

3

### Example 2

**Prompt:**

This is a Markov algorithm over the alphabet abc.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. ab ->
2. b ->
3. c ->
4. ca -> b
Start word: ccbabcacc
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

7

## Level 2

### Example 1

**Prompt:**

This is a Markov algorithm over the alphabet abc.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. bb ->
2. cb -> .
3. bb -> a
4. a ->
5. c ->
Start word: aaabccca
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

7

### Example 2

**Prompt:**

This is a Markov algorithm over the alphabet abc.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. a ->
2. aa ->
3. cbb -> bc
Start word: cbbabbacba
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

5

## Level 5

### Example 1

**Prompt:**

This is a Markov algorithm over the alphabet abcde.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. dbea -> .bb
2. c ->
3. cee -> .b
4. b ->
5. ebd ->
6. b -> .
7. d -> .
8. cce ->
Start word: cadabbedacacc
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

7

### Example 2

**Prompt:**

This is a Markov algorithm over the alphabet abcde.
It rewrites strings. Apply the rules below in order (rule 1 first). At each step, take the first rule whose left side occurs; replace its leftmost occurrence with the right side, then restart from rule 1. A rule written 'lhs -> .rhs' halts the algorithm when it is applied; the algorithm also halts when no rule's left side occurs.
Rules:
1. e ->
2. edc -> bc
3. aecc -> a
4. c ->
5. b ->
6. ce -> .
7. eabd -> ddd
8. aaa ->
Start word: bacbacbabdceecbcd
How many rule applications happen before the algorithm halts? Answer with a single integer (the step count).

**Answer:**

13
