# Pooled test status decoding - samples

Assignment: P004v1. Random seed 3536382515.

## Level 0

**Prompt**

We have 3 items, exactly 1 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [0, 1]
Pool 1: items [0, 1, 2]
Determine each item's status. Output a single string of length 3 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

??C

**Prompt**

We have 3 items, exactly 1 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [1, 2]
Pool 1: items [0, 1, 2]
Determine each item's status. Output a single string of length 3 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

C??

## Level 2

**Prompt**

We have 5 items, exactly 2 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [0, 1, 2, 3, 4]
Pool 1: items [0, 2, 4]
Pool 2: items [0, 1, 3, 4]
Pool 3: items [0, 3]
Determine each item's status. Output a single string of length 5 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

C??C?

**Prompt**

We have 5 items, exactly 2 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [2, 3, 4]
Pool 1: items [2]
Pool 2: items [1, 4]
Pool 3: items [0, 2, 4]
Determine each item's status. Output a single string of length 5 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

??C?T

## Level 5

**Prompt**

We have 8 items, exactly 3 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [0, 1, 2, 3, 5, 6, 7]
Pool 1: items [3, 4, 5, 6, 7]
Pool 2: items [0, 1, 3, 4, 5, 7]
Pool 3: items [1, 2, 3, 4, 6, 7]
Pool 4: items [0, 1, 2, 3, 4, 5, 6, 7]
Pool 5: items [2, 3, 5, 7]
Pool 6: items [2]
Determine each item's status. Output a single string of length 8 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

??CC?C?C

**Prompt**

We have 8 items, exactly 3 of which are tainted (the rest clean). The following pooled tests were run; each test reports TAINTED if its pool contains at least one tainted item, otherwise CLEAN.
Pool 0: items [0, 1, 2, 3, 4, 5, 6, 7]
Pool 1: items [2]
Pool 2: items [2]
Pool 3: items [3, 5]
Pool 4: items [1, 4]
Pool 5: items [0, 6]
Pool 6: items [2, 3, 4, 5]
Determine each item's status. Output a single string of length 8 in item index order using C for clean, T for tainted, and ? for undetermined. Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC.

**Answer**

C?T???CC
