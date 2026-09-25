# Censoring Observation Equivalence V3 - samples (P003v3)

## Level 0
Config: n=4, maxval=4, blocks=2

### Example 1
**Prompt:**
A sensor logs one reading per time step from time 1 to time 4; every reading is an integer from 0 to 4. A hidden history is one assignment of those readings over time.

Report A:
- From time 1 to time 2 the reading stayed within 1 and 2.
- The minimum reading between time 3 and time 4 was 3.

Report B:
- From time 1 to time 2 the reading never fell below 0.
- From time 1 to time 2 the reading never exceeded 3.
- The minimum reading between time 3 and time 4 was 3.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** NO

### Example 2
**Prompt:**
A sensor logs one reading per time step from time 1 to time 4; every reading is an integer from 0 to 4. A hidden history is one assignment of those readings over time.

Report A:
- From time 1 to time 3 the reading stayed within 1 and 2.
- The maximum reading at time 4 was 2.

Report B:
- From time 1 to time 3 the reading never fell below 0.
- From time 1 to time 3 the reading never exceeded 3.
- The maximum reading at time 4 was 2.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** NO


## Level 2
Config: n=4, maxval=6, blocks=3

### Example 1
**Prompt:**
A sensor logs one reading per time step from time 1 to time 4; every reading is an integer from 0 to 6. A hidden history is one assignment of those readings over time.

Report A:
- At time 1 the reading was exactly 6.
- From time 2 to time 3 the reading never exceeded 6.
- At time 4 the reading was at least 1.

Report B:
- At time 1 the reading was between 1 and 6.
- From time 2 to time 3 the reading never exceeded 6.
- At time 4 the reading was at least 1.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** NO

### Example 2
**Prompt:**
A sensor logs one reading per time step from time 1 to time 4; every reading is an integer from 0 to 6. A hidden history is one assignment of those readings over time.

Report A:
- From time 1 to time 2 the reading stayed within 1 and 3.
- At time 3 the reading was between 2 and 2.
- At time 4 the reading was between 5 and 5.

Report B:
- From time 1 to time 2 the reading never fell below 1.
- From time 1 to time 2 the reading never exceeded 3.
- At time 3 the reading was between 2 and 2.
- At time 4 the reading was between 5 and 5.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** YES


## Level 5
Config: n=5, maxval=8, blocks=4

### Example 1
**Prompt:**
A sensor logs one reading per time step from time 1 to time 5; every reading is an integer from 0 to 8. A hidden history is one assignment of those readings over time.

Report A:
- At time 1 the reading was between 8 and 8.
- At time 2 the reading was at most 7.
- At time 3 the reading was at most 6.
- From time 4 to time 5 the reading stayed within 5 and 8.

Report B:
- At time 1 the reading was at least 7.
- At time 1 the reading was at most 8.
- At time 2 the reading was at most 7.
- At time 3 the reading was at most 6.
- From time 4 to time 5 the reading stayed within 5 and 8.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** NO

### Example 2
**Prompt:**
A sensor logs one reading per time step from time 1 to time 5; every reading is an integer from 0 to 8. A hidden history is one assignment of those readings over time.

Report A:
- At time 1 the reading was exactly 3.
- The maximum reading at time 2 was 6.
- The minimum reading at time 3 was 7.
- From time 4 to time 5 the reading stayed within 0 and 8.

Report B:
- At time 1 the reading was between 2 and 3.
- The maximum reading at time 2 was 6.
- The minimum reading at time 3 was 7.
- From time 4 to time 5 the reading stayed within 0 and 8.

Do reports A and B carry identical evidence -- do they permit exactly the same set of reading histories? Reply by writing only YES or NO as the answer.

**Answer:** NO
