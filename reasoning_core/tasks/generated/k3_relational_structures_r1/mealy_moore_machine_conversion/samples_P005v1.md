## Level 0
**Prompt**

A Mealy machine has states and outputs on each transition (2 inputs, inputs labeled 0..1). Its transition/output table is:
[[(1, '0'), (0, '1')], [(1, '0'), (0, '1')]]
Convert it to an equivalent Moore machine by splitting states so every input-output trace is preserved. Give the resulting Moore table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states renamed S0,S1,... in the order you create them.

**Answer**

S0:0->S1,0;1->S2,1|S1:0->S1,0;1->S2,1|S2:0->S1,0;1->S2,1

---

**Prompt**

A Mealy machine has states and outputs on each transition (2 inputs, inputs labeled 0..1). Its transition/output table is:
[[(0, '0'), (0, '1')], [(1, '1'), (1, '0')]]
Convert it to an equivalent Moore machine by splitting states so every input-output trace is preserved. Give the resulting Moore table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states renamed S0,S1,... in the order you create them.

**Answer**

S0:0->S1,0;1->S2,1|S1:0->S1,0;1->S2,1|S2:0->S1,0;1->S2,1

---

## Level 2
**Prompt**

A Mealy machine has states and outputs on each transition (2 inputs, inputs labeled 0..1). Its transition/output table is:
[[(0, '0'), (1, '0')], [(3, '1'), (0, '0')], [(1, '1'), (2, '0')], [(0, '1'), (0, '1')]]
Convert it to an equivalent Moore machine by splitting states so every input-output trace is preserved. Give the resulting Moore table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states renamed S0,S1,... in the order you create them.

**Answer**

S0:0->S1,0;1->S2,0|S1:0->S1,0;1->S2,0|S2:0->S3,1;1->S1,0|S3:0->S4,1;1->S4,1|S4:0->S1,0;1->S2,0

---

**Prompt**

A Mealy machine has states and outputs on each transition (2 inputs, inputs labeled 0..1). Its transition/output table is:
[[(1, '0'), (2, '0')], [(1, '0'), (2, '1')], [(0, '1'), (1, '0')], [(3, '1'), (0, '1')]]
Convert it to an equivalent Moore machine by splitting states so every input-output trace is preserved. Give the resulting Moore table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states renamed S0,S1,... in the order you create them.

**Answer**

S0:0->S1,0;1->S2,0|S1:0->S1,0;1->S3,1|S2:0->S4,1;1->S1,0|S3:0->S4,1;1->S1,0|S4:0->S1,0;1->S2,0

---

## Level 5
**Prompt**

A Moore machine has an output attached to each state (3 inputs, inputs labeled 0..2). Its per-state outputs are: S0:1, S1:1, S2:1, S3:1, S4:1, S5:0, S6:1. Its transition table lists each state's successors by input:
[[1, 3, 3], [0, 2, 3], [6, 3, 4], [4, 2, 3], [6, 6, 2], [1, 2, 0], [0, 3, 1]]
Convert it to an equivalent Mealy machine (output on each transition). Give the resulting Mealy table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states named S0,S1,...

**Answer**

S0:0->S1,1;1->S3,1;2->S3,1|S1:0->S0,1;1->S2,1;2->S3,1|S2:0->S6,1;1->S3,1;2->S4,1|S3:0->S4,1;1->S2,1;2->S3,1|S4:0->S6,1;1->S6,1;2->S2,1|S5:0->S1,1;1->S2,1;2->S0,1|S6:0->S0,1;1->S3,1;2->S1,1

---

**Prompt**

A Mealy machine has states and outputs on each transition (3 inputs, inputs labeled 0..2). Its transition/output table is:
[[(5, '0'), (3, '1'), (2, '1')], [(2, '0'), (3, '1'), (1, '0')], [(2, '0'), (0, '1'), (2, '0')], [(1, '1'), (2, '1'), (0, '0')], [(3, '1'), (1, '1'), (1, '0')], [(4, '0'), (3, '1'), (1, '1')], [(0, '1'), (3, '1'), (2, '0')]]
Convert it to an equivalent Moore machine by splitting states so every input-output trace is preserved. Give the resulting Moore table, each row as 'state:input->next,output' (separate inputs with ';', rows with '|'), states renamed S0,S1,... in the order you create them.

**Answer**

S0:0->S1,0;1->S2,1;2->S3,1|S1:0->S4,0;1->S2,1;2->S5,1|S2:0->S5,1;1->S3,1;2->S6,0|S3:0->S7,0;1->S8,1;2->S7,0|S4:0->S2,1;1->S5,1;2->S9,0|S5:0->S7,0;1->S2,1;2->S9,0|S6:0->S1,0;1->S2,1;2->S3,1|S7:0->S7,0;1->S8,1;2->S7,0|S8:0->S1,0;1->S2,1;2->S3,1|S9:0->S7,0;1->S2,1;2->S9,0

---
