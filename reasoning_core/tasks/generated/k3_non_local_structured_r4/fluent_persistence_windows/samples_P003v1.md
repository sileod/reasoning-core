## Level 0

### Example 1

**Prompt:**

Fluents: F0..F1. Initially none hold. Events toggle a fluent (on if off, off if on): at 1: toggle F0,F1; at 2: toggle F0,F1; at 5: toggle F0,F1; at 6: toggle F0. Fluents persist their truth between events. What is the last instant at which F1 holds? Answer a single integer timestamp, or -1 if it never holds.

**Answer:**

6

### Example 2

**Prompt:**

Fluents: F0..F1. Initially none hold. Events toggle a fluent (on if off, off if on): at 2: toggle F0,F1; at 3: toggle F0,F1; at 4: toggle F1; at 6: toggle F1. Fluents persist their truth between events. What is the first instant at which F0 holds? Answer a single integer timestamp, or 7 if it never holds.

**Answer:**

2

## Level 2

### Example 1

**Prompt:**

Fluents: F0..F3. Initially none hold. Events toggle a fluent (on if off, off if on): at 1: toggle F2; at 4: toggle F0,F3; at 6: toggle F0,F2; at 7: toggle F1; at 8: toggle F1; at 10: toggle F2,F3; at 11: toggle F0,F2; at 12: toggle F2. Fluents persist their truth between events. Does F0 hold at time 0? Answer exactly yes or no.

**Answer:**

no

### Example 2

**Prompt:**

Fluents: F0..F3. Initially none hold. Events toggle a fluent (on if off, off if on): at 1: toggle F2,F3; at 2: toggle F0,F2; at 3: toggle F2; at 4: toggle F0,F1; at 5: toggle F0,F3; at 6: toggle F1,F2; at 9: toggle F2; at 10: toggle F3. Fluents persist their truth between events. Which fluents hold at time 12? Answer a comma-separated sorted list of fluent names (e.g. F0,F2), or the word none if no fluent holds.

**Answer:**

F0,F2,F3

## Level 5

### Example 1

**Prompt:**

Fluents: F0..F6. Initially none hold. Events toggle a fluent (on if off, off if on): at 2: toggle F0,F5; at 3: toggle F0; at 4: toggle F6; at 6: toggle F0,F5; at 7: toggle F4; at 9: toggle F1,F6; at 10: toggle F2,F5; at 13: toggle F2; at 14: toggle F3,F4; at 15: toggle F0; at 17: toggle F2; at 18: toggle F0,F4; at 19: toggle F3,F4; at 21: toggle F0. Fluents persist their truth between events. Does F4 hold at time 6? Answer exactly yes or no.

**Answer:**

no

### Example 2

**Prompt:**

Fluents: F0..F6. Initially none hold. Events toggle a fluent (on if off, off if on): at 1: toggle F0,F5; at 2: toggle F5; at 4: toggle F3; at 5: toggle F0,F5; at 6: toggle F2; at 7: toggle F5; at 9: toggle F3; at 12: toggle F3; at 14: toggle F5; at 15: toggle F5,F6; at 16: toggle F0,F4; at 17: toggle F0,F2; at 18: toggle F5; at 21: toggle F3,F6. Fluents persist their truth between events. Which fluents hold at time 0? Answer a comma-separated sorted list of fluent names (e.g. F0,F2), or the word none if no fluent holds.

**Answer:**

none

