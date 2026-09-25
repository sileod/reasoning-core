## Level 0

### Example 1

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 10 outcomes o1..o10 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 10 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 2 24 20 12 12
Outcome o2: 32 48 36 24 24
Outcome o3: 16 24 18 12 12
Outcome o4: 11 8 4 12 2
Outcome o5: 33 24 12 36 6
Outcome o6: 5 60 50 30 30
Outcome o7: 11 8 4 12 2
Outcome o8: 2 24 20 12 12
Outcome o9: 48 72 54 36 36
Outcome o10: 48 72 54 36 36

**Answer:**

0,1,1,2,2,0,2,0,1,1


### Example 2

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 10 outcomes o1..o10 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 10 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 4 4 2 12 24
Outcome o2: 12 12 6 36 72
Outcome o3: 6 6 3 18 36
Outcome o4: 10 11 1 2 5
Outcome o5: 20 22 2 4 10
Outcome o6: 4 4 2 12 24
Outcome o7: 6 6 3 18 36
Outcome o8: 2 2 1 6 12
Outcome o9: 30 33 3 6 15
Outcome o10: 30 33 3 6 15

**Answer:**

0,0,0,1,1,0,0,0,1,1


## Level 2

### Example 1

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 14 outcomes o1..o14 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 14 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 36 8 28 4 28
Outcome o2: 45 10 35 5 35
Outcome o3: 36 8 28 4 28
Outcome o4: 9 11 5 7 9
Outcome o5: 9 11 5 7 9
Outcome o6: 44 16 32 24 36
Outcome o7: 54 12 42 6 42
Outcome o8: 33 12 24 18 27
Outcome o9: 27 6 21 3 21
Outcome o10: 54 66 30 42 54
Outcome o11: 66 24 48 36 54
Outcome o12: 44 16 32 24 36
Outcome o13: 44 16 32 24 36
Outcome o14: 54 66 30 42 54

**Answer:**

0,0,0,1,1,2,0,2,0,1,2,2,2,1


### Example 2

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 14 outcomes o1..o14 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 14 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 54 30 6 66 60
Outcome o2: 40 55 25 60 20
Outcome o3: 4 6 12 14 24
Outcome o4: 18 10 2 22 20
Outcome o5: 32 28 20 48 40
Outcome o6: 45 25 5 55 50
Outcome o7: 18 36 24 42 6
Outcome o8: 24 33 15 36 12
Outcome o9: 32 28 20 48 40
Outcome o10: 36 20 4 44 40
Outcome o11: 30 20 20 60 55
Outcome o12: 48 42 30 72 60
Outcome o13: 4 6 12 14 24
Outcome o14: 16 22 10 24 8

**Answer:**

0,1,2,0,3,0,4,1,3,0,5,3,2,1


## Level 5

### Example 1

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 20 outcomes o1..o20 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 20 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 18 66 24 42 72
Outcome o2: 45 15 40 60 5
Outcome o3: 15 21 27 9 36
Outcome o4: 10 14 18 6 24
Outcome o5: 27 9 24 36 3
Outcome o6: 10 14 18 6 24
Outcome o7: 9 33 12 21 36
Outcome o8: 27 9 24 36 3
Outcome o9: 30 42 54 18 72
Outcome o10: 25 35 45 15 60
Outcome o11: 54 18 48 72 6
Outcome o12: 10 14 18 6 24
Outcome o13: 15 55 20 35 60
Outcome o14: 12 44 16 28 48
Outcome o15: 12 44 16 28 48
Outcome o16: 3 11 4 7 12
Outcome o17: 15 21 27 9 36
Outcome o18: 36 12 32 48 4
Outcome o19: 5 7 9 3 12
Outcome o20: 15 21 27 9 36

**Answer:**

0,1,2,2,1,2,0,1,2,2,1,2,0,0,0,0,2,1,2,2


### Example 2

**Prompt:**

There are 5 hypotheses h1..h5. Each of the 20 outcomes o1..o20 has a likelihood vector of positive integers, one entry per hypothesis (relative unnormalized likelihoods). Two outcomes are in the same minimal sufficient class when their likelihood vectors are scalar multiples of each other (proportional), so that grouping them loses no posterior information. Output the minimal partition as a comma-separated list of 20 class labels, one per outcome, labelling classes by first occurrence (o1's class is label 0, then each new class gets the next integer in order of first appearance).

Outcome o1: 36 15 21 36 6
Outcome o2: 36 33 24 18 12
Outcome o3: 4 4 1 4 4
Outcome o4: 24 10 14 24 4
Outcome o5: 8 2 12 12 5
Outcome o6: 8 2 12 12 5
Outcome o7: 16 4 24 24 10
Outcome o8: 36 15 21 36 6
Outcome o9: 4 4 1 4 4
Outcome o10: 32 8 48 48 20
Outcome o11: 12 11 8 6 4
Outcome o12: 72 30 42 72 12
Outcome o13: 16 4 24 24 10
Outcome o14: 8 8 2 8 8
Outcome o15: 72 66 48 36 24
Outcome o16: 36 33 24 18 12
Outcome o17: 16 4 24 24 10
Outcome o18: 40 10 60 60 25
Outcome o19: 12 5 7 12 2
Outcome o20: 24 24 6 24 24

**Answer:**

0,1,2,0,3,3,3,0,2,3,1,0,3,2,1,1,3,3,0,2

