# Samples: question_partition_equivalence

## Level 0

### Example 1

**Prompt:**

There are 4 possible worlds, numbered: 1, 2, 4, 6.

Question one: Is the world (at most 0 or even)?

Question two: Is the world (at least 5 or greater than 0)?

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

no

### Example 2

**Prompt:**

There are 4 possible worlds, numbered: 0, 1, 3, 4.

Question one: What number is the world? (Give its exact value.)

Question two: Is the world (even or congruent to 0 modulo 4)?

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

no

## Level 2

### Example 1

**Prompt:**

There are 6 possible worlds, numbered: 1, 3, 6, 13, 15, 16.

Question one: Which one of the following groups is the world in: {13}, {15}? (If it is in none, the answer is 'none of the above'.)

Question two: Which one of the following groups is the world in: {15}, {13}? (If it is in none, the answer is 'none of the above'.)

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

yes

### Example 2

**Prompt:**

There are 6 possible worlds, numbered: 0, 1, 8, 12, 14, 15.

Question one: Is the world less than 12?

Question two: Is the world not (not (less than 12))?

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

yes

## Level 5

### Example 1

**Prompt:**

There are 9 possible worlds, numbered: 4, 8, 9, 14, 19, 20, 22, 24, 26.

Question one: Is the world not (((even and equal to 26) or (less than 9 or at least 23)))?

Question two: Is the world not (not ((at least 15 or even)))?

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

no

### Example 2

**Prompt:**

There are 9 possible worlds, numbered: 3, 4, 5, 13, 17, 20, 22, 26, 27.

Question one: Is the world not ((not (between 27 and 27 inclusive) and (equal to 16 and between 16 and 19 inclusive)))?

Question two: Is the world not ((not (between 27 and 27 inclusive) and not ((not (equal to 16) or not (between 16 and 19 inclusive)))))?

Do these two questions induce the same partition of the possible worlds -- that is, do they ask the same thing? Answer exactly "yes" or "no".

**Answer:**

yes
