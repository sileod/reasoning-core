# Samples for P011v1 (prediction_commitment_lineage)

## Level 0

### Example 1
Prompt:
A study evolved through 3 analysis versions (numbered 1..3) and 2 claims, each evaluated by one test. There are 12 data items (numbered 1..12); each was introduced by one version. Data item m was introduced by version 1:v1, 2:v3, 3:v2, 4:v3, 5:v2, 6:v1, 7:v3, 8:v3, 9:v2, 10:v3, 11:v2, 12:v1. Version 1 is the initial version with no ancestors. Version 2 is the initial version with no ancestors. Version 3 is the initial version with no ancestors. Claim 1 was evaluated by running test 3 at version 1; test 3 reads data { d12 }. Claim 2 was evaluated by running test 1 at version 3; test 1 reads data { d4 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
none

---

### Example 2
Prompt:
A study evolved through 3 analysis versions (numbered 1..3) and 2 claims, each evaluated by one test. There are 12 data items (numbered 1..12); each was introduced by one version. Data item m was introduced by version 1:v1, 2:v1, 3:v3, 4:v2, 5:v2, 6:v3, 7:v3, 8:v3, 9:v3, 10:v2, 11:v3, 12:v2. Version 1 is the initial version with no ancestors. Version 2 is the initial version with no ancestors. Version 3 is the initial version with no ancestors. Claim 1 was evaluated by running test 1 at version 2; test 1 reads data { d5 }. Claim 2 was evaluated by running test 2 at version 2; test 2 reads data { d9 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
2:2

---

## Level 2

### Example 1
Prompt:
A study evolved through 5 analysis versions (numbered 1..5) and 4 claims, each evaluated by one test. There are 18 data items (numbered 1..18); each was introduced by one version. Data item m was introduced by version 1:v5, 2:v3, 3:v2, 4:v4, 5:v4, 6:v5, 7:v3, 8:v4, 9:v3, 10:v4, 11:v1, 12:v4, 13:v2, 14:v4, 15:v2, 16:v5, 17:v4, 18:v4. Version 1 is the initial version with no ancestors. Version 2 is the initial version with no ancestors. Version 3 was derived by revising version(s) 2. Version 4 is the initial version with no ancestors. Version 5 was derived by revising version(s) 3 and 4. Claim 1 was evaluated by running test 2 at version 2; test 2 reads data { d3 d18 }. Claim 2 was evaluated by running test 1 at version 2; test 1 reads data { d3 d17 }. Claim 3 was evaluated by running test 4 at version 3; test 4 reads data { d13 d18 }. Claim 4 was evaluated by running test 3 at version 2; test 3 reads data { d8 d13 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
none

---

### Example 2
Prompt:
A study evolved through 5 analysis versions (numbered 1..5) and 4 claims, each evaluated by one test. There are 18 data items (numbered 1..18); each was introduced by one version. Data item m was introduced by version 1:v4, 2:v3, 3:v1, 4:v4, 5:v5, 6:v5, 7:v1, 8:v4, 9:v4, 10:v3, 11:v2, 12:v5, 13:v2, 14:v2, 15:v4, 16:v3, 17:v4, 18:v1. Version 1 is the initial version with no ancestors. Version 2 was derived by revising version(s) 1. Version 3 is the initial version with no ancestors. Version 4 is the initial version with no ancestors. Version 5 was derived by revising version(s) 1 and 2. Claim 1 was evaluated by running test 1 at version 3; test 1 reads data { d2 d14 }. Claim 2 was evaluated by running test 5 at version 4; test 5 reads data { d7 d12 }. Claim 3 was evaluated by running test 2 at version 1; test 2 reads data { d10 d12 }. Claim 4 was evaluated by running test 3 at version 4; test 3 reads data { d3 d17 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
2:5,3:2

---

## Level 5

### Example 1
Prompt:
A study evolved through 8 analysis versions (numbered 1..8) and 7 claims, each evaluated by one test. There are 27 data items (numbered 1..27); each was introduced by one version. Data item m was introduced by version 1:v4, 2:v8, 3:v4, 4:v6, 5:v4, 6:v5, 7:v7, 8:v8, 9:v7, 10:v7, 11:v1, 12:v8, 13:v6, 14:v4, 15:v8, 16:v4, 17:v5, 18:v4, 19:v6, 20:v7, 21:v5, 22:v3, 23:v8, 24:v5, 25:v7, 26:v7, 27:v5. Version 1 is the initial version with no ancestors. Version 2 was derived by revising version(s) 1. Version 3 is the initial version with no ancestors. Version 4 was derived by revising version(s) 2. Version 5 is the initial version with no ancestors. Version 6 was derived by revising version(s) 2 and 4 and 5. Version 7 was derived by revising version(s) 4 and 5. Version 8 is the initial version with no ancestors. Claim 1 was evaluated by running test 2 at version 7; test 2 reads data { d8 d12 d23 }. Claim 2 was evaluated by running test 8 at version 2; test 8 reads data { d6 d24 d25 }. Claim 3 was evaluated by running test 5 at version 4; test 5 reads data { d12 d21 d22 }. Claim 4 was evaluated by running test 1 at version 2; test 1 reads data { d3 d11 d16 }. Claim 5 was evaluated by running test 3 at version 3; test 3 reads data { d3 d22 d27 }. Claim 6 was evaluated by running test 4 at version 8; test 4 reads data { d3 d21 d24 }. Claim 7 was evaluated by running test 6 at version 3; test 6 reads data { d4 d9 d22 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
1:2,2:8,3:5,6:4

---

### Example 2
Prompt:
A study evolved through 8 analysis versions (numbered 1..8) and 7 claims, each evaluated by one test. There are 27 data items (numbered 1..27); each was introduced by one version. Data item m was introduced by version 1:v5, 2:v2, 3:v5, 4:v5, 5:v8, 6:v5, 7:v4, 8:v7, 9:v2, 10:v8, 11:v1, 12:v8, 13:v2, 14:v6, 15:v6, 16:v8, 17:v7, 18:v4, 19:v8, 20:v8, 21:v7, 22:v7, 23:v1, 24:v1, 25:v2, 26:v3, 27:v7. Version 1 is the initial version with no ancestors. Version 2 is the initial version with no ancestors. Version 3 is the initial version with no ancestors. Version 4 was derived by revising version(s) 2 and 3. Version 5 was derived by revising version(s) 4. Version 6 is the initial version with no ancestors. Version 7 was derived by revising version(s) 2 and 4. Version 8 was derived by revising version(s) 3 and 5. Claim 1 was evaluated by running test 3 at version 6; test 3 reads data { d18 d24 d26 }. Claim 2 was evaluated by running test 5 at version 6; test 5 reads data { d4 d16 d23 }. Claim 3 was evaluated by running test 2 at version 8; test 2 reads data { d4 d7 d23 }. Claim 4 was evaluated by running test 7 at version 3; test 7 reads data { d4 d16 d26 }. Claim 5 was evaluated by running test 4 at version 5; test 4 reads data { d7 d9 d19 }. Claim 6 was evaluated by running test 1 at version 2; test 1 reads data { d4 d17 d21 }. Claim 7 was evaluated by running test 8 at version 8; test 8 reads data { d5 d14 d19 }. A claim-test pair is contaminated by inherited data reuse when any data item the test reads was introduced by the version where the claim was evaluated or by any of that version's ancestor versions. It is genuinely held out (uncontaminated) when all of the data the test reads was introduced only by versions outside that whole lineage. List the claim:test pairs that are uncontaminated, in increasing claim order, comma-separated (e.g. '1:4,3:2'); write 'none' if there are none.

Answer:
1:3,2:5,6:1

---
