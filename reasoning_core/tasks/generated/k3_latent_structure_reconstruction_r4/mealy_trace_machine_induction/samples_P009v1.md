# Level 0

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b
eps        1    1

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q0/1 ; q0 --b--> q0/1
```

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b
eps        1    1

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q0/1 ; q0 --b--> q0/1
```

# Level 2

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b
eps        0    1
b          1    0
ba         0    0

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q0/0 ; q0 --b--> q1/1 ; q1 --a--> q2/1 ; q1 --b--> q0/0 ; q2 --a--> q1/0 ; q2 --b--> q0/0
```

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b
eps        1    1

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q0/1 ; q0 --b--> q0/1
```

# Level 5

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b   aa   ab  aab
eps        1    0    0    1    0
a          0    1    1    0    1
b          1    0    1    0    1
aa         1    0    1    1    0
bb         1    1    0    1    0
aaa        1    1    1    0    1
aab        1    0    1    0    0

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q1/1 ; q0 --b--> q2/0 ; q1 --a--> q3/0 ; q1 --b--> q2/1 ; q2 --a--> q3/1 ; q2 --b--> q4/0 ; q3 --a--> q5/1 ; q3 --b--> q6/0 ; q4 --a--> q1/1 ; q4 --b--> q5/1 ; q5 --a--> q3/1 ; q5 --b--> q0/1 ; q6 --a--> q2/1 ; q6 --b--> q5/0
```

**Prompt:**
```
A hidden Mealy machine has input alphabet {a, b} and output alphabet {0, 1}. It starts from its initial state and we record its input/output behavior in the observation table below. Each row is a history string (the inputs fed so far from the start); each column is a distinguishing suffix string; the cell at (history, suffix) is the output bit the machine emits as its last step when the suffix is fed immediately after that history.

Observation table (rows: histories, columns: suffixes):
history    a    b   ab   aa
eps        1    1    0    1
a          1    0    1    1
b          1    1    1    1
ab         1    0    1    0
bb         0    1    1    1
abb        1    1    1    0

Two histories lead to the same state iff their rows agree in every column (their futures agree). Merge equal rows: the minimized machine has one state per equivalence class. For a merged state v with representative history h, on input x it emits cell T[h][x] and moves to the state whose class contains the row indexed by h+x (propagate: look up h+x's row and merge by it too). The table distinguishes every pair of states and stays closed under appending one input, so this yields a well-defined minimized machine.

Name states canonically: within each equivalence class take the lexicographically smallest history (shorter strings first, equal-length strings in a<b order); order the representatives the same way and call them q0, q1, ... in that order.

Give the completed minimized machine as an explicit transition table covering every state and every input, in the exact format `q0 --a--> q1/0 ; q0 --b--> q2/1 ; q1 --a--> ...`, states in order q0, q1, ..., and within each state input a then b; each entry is `qk --i--> qm/o` with qk the current state, i the input, qm the next state, o the output bit. Output only the table, nothing else.
```

**Answer:**
```
q0 --a--> q1/1 ; q0 --b--> q2/1 ; q1 --a--> q0/1 ; q1 --b--> q3/0 ; q2 --a--> q0/1 ; q2 --b--> q4/1 ; q3 --a--> q4/1 ; q3 --b--> q5/0 ; q4 --a--> q0/0 ; q4 --b--> q0/1 ; q5 --a--> q4/1 ; q5 --b--> q0/1
```
