## Level 0
### Example 1
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c}. Machine A has states 0..1 and machine B has states 0..1.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(0,a), (0,b)->(1,b), (0,c)->(1,c), (1,a)->(1,b), (1,b)->(1,a), (1,c)->(0,b)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(0,c), (0,b)->(1,b), (0,c)->(0,b), (1,a)->(0,c), (1,b)->(1,b), (1,c)->(0,a)
Both machines start in state 0.
Feed the input word 'aac' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
ccb;1;0
```
### Example 2
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c}. Machine A has states 0..1 and machine B has states 0..1.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(1,a), (0,b)->(1,a), (0,c)->(0,b), (1,a)->(0,a), (1,b)->(0,a), (1,c)->(0,a)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(1,c), (0,b)->(0,a), (0,c)->(1,a), (1,a)->(1,b), (1,b)->(0,b), (1,c)->(0,a)
Both machines start in state 0.
Feed the input word 'abb' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
cbb;1;1
```
## Level 2
### Example 1
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c}. Machine A has states 0..2 and machine B has states 0..2.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(1,c), (0,b)->(2,b), (0,c)->(2,a), (1,a)->(2,b), (1,b)->(0,c), (1,c)->(1,a), (2,a)->(0,a), (2,b)->(1,a), (2,c)->(1,b)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(0,c), (0,b)->(0,b), (0,c)->(0,b), (1,a)->(2,c), (1,b)->(1,b), (1,c)->(2,c), (2,a)->(0,b), (2,b)->(1,c), (2,c)->(2,b)
Both machines start in state 0.
Feed the input word 'cabac' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
ccbcc;2;0
```
### Example 2
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c}. Machine A has states 0..2 and machine B has states 0..2.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(0,b), (0,b)->(0,c), (0,c)->(0,a), (1,a)->(0,a), (1,b)->(1,c), (1,c)->(0,b), (2,a)->(0,c), (2,b)->(2,b), (2,c)->(1,c)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(2,a), (0,b)->(1,c), (0,c)->(1,a), (1,a)->(0,b), (1,b)->(2,b), (1,c)->(1,c), (2,a)->(2,b), (2,b)->(1,c), (2,c)->(2,b)
Both machines start in state 0.
Feed the input word 'cbcab' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
abbcc;0;1
```
## Level 5
### Example 1
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c, d}. Machine A has states 0..3 and machine B has states 0..3.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(3,c), (0,b)->(2,a), (0,c)->(0,b), (0,d)->(2,d), (1,a)->(1,c), (1,b)->(1,d), (1,c)->(0,c), (1,d)->(1,b), (2,a)->(0,d), (2,b)->(3,d), (2,c)->(3,b), (2,d)->(3,b), (3,a)->(2,b), (3,b)->(3,d), (3,c)->(0,a), (3,d)->(1,b)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(3,c), (0,b)->(3,d), (0,c)->(1,b), (0,d)->(0,c), (1,a)->(3,b), (1,b)->(1,d), (1,c)->(0,b), (1,d)->(1,d), (2,a)->(0,b), (2,b)->(0,c), (2,c)->(3,d), (2,d)->(3,c), (3,a)->(2,d), (3,b)->(3,a), (3,c)->(0,d), (3,d)->(2,c)
Both machines start in state 0.
Feed the input word 'bdacaddd' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
caaaaaaa;1;3
```
### Example 2
**Prompt:**
```
Two Mealy machines A and B share the input/output alphabet {a, b, c, d}. Machine A has states 0..3 and machine B has states 0..3.
Machine A transitions (state,symbol)->(next state, output symbol):
(0,a)->(3,b), (0,b)->(2,c), (0,c)->(1,b), (0,d)->(2,b), (1,a)->(2,b), (1,b)->(2,c), (1,c)->(1,d), (1,d)->(3,a), (2,a)->(2,d), (2,b)->(0,c), (2,c)->(1,c), (2,d)->(3,a), (3,a)->(3,a), (3,b)->(2,d), (3,c)->(3,a), (3,d)->(3,d)
Machine B transitions (state,symbol)->(next state, output symbol):
(0,a)->(3,c), (0,b)->(1,b), (0,c)->(1,c), (0,d)->(1,d), (1,a)->(1,c), (1,b)->(1,b), (1,c)->(0,d), (1,d)->(0,c), (2,a)->(3,a), (2,b)->(2,d), (2,c)->(2,b), (2,d)->(1,a), (3,a)->(1,a), (3,b)->(0,b), (3,c)->(3,b), (3,d)->(1,a)
Both machines start in state 0.
Feed the input word 'accabaab' into machine A, reading one symbol per step and emitting its output symbol each step. Then feed machine A's emitted word into machine B, again starting in state 0. Track each machine's state after processing every symbol of its consumed word.
Answer as the final output word produced by machine B, a semicolon, machine A's final state, a semicolon, then machine B's final state. For example 'abc;1;0' means machine B emitted 'abc', machine A ended in state 1, and machine B ended in state 0.
```
**Answer:**
```
bccccdcc;0;1
```
