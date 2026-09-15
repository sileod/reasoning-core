# Level 0

### Example 1
**Prompt:**
```
Consider a synchronous Boolean network on n = 4 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [2, 3] -> 1110
  node 1: deps [3, 2] -> 1011
  node 2: deps [0, 1] -> 0101
  node 3: deps [1, 3] -> 0011
The network runs synchronously from the initial state 0001 until it enters its attractor cycle.
Now node 1 is clamped to the fixed value 0: its value remains 0 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
0001-1001-1011-0011 3
```

### Example 2
**Prompt:**
```
Consider a synchronous Boolean network on n = 4 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [0, 1] -> 1010
  node 1: deps [0, 2] -> 1101
  node 2: deps [2, 0] -> 1000
  node 3: deps [1, 2] -> 1011
The network runs synchronously from the initial state 1110 until it enters its attractor cycle.
Now node 3 is clamped to the fixed value 0: its value remains 0 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
0100-1110 1
```


# Level 2

### Example 1
**Prompt:**
```
Consider a synchronous Boolean network on n = 6 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [3, 4] -> 0110
  node 1: deps [3, 0] -> 1010
  node 2: deps [0, 5] -> 1011
  node 3: deps [1, 5] -> 1000
  node 4: deps [2, 3] -> 1101
  node 5: deps [1, 2] -> 0001
The network runs synchronously from the initial state 010010 until it enters its attractor cycle.
Now node 5 is clamped to the fixed value 0: its value remains 0 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
110010 2
```

### Example 2
**Prompt:**
```
Consider a synchronous Boolean network on n = 6 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [5, 3] -> 0101
  node 1: deps [2, 0] -> 1001
  node 2: deps [4, 1] -> 0000
  node 3: deps [2, 3] -> 1000
  node 4: deps [0, 1] -> 1110
  node 5: deps [4, 1] -> 1111
The network runs synchronously from the initial state 100010 until it enters its attractor cycle.
Now node 0 is clamped to the fixed value 0: its value remains 0 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
010011-010111 2
```


# Level 5

### Example 1
**Prompt:**
```
Consider a synchronous Boolean network on n = 9 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [3, 5, 0] -> 10110110
  node 1: deps [6, 0, 2] -> 01111111
  node 2: deps [8, 1, 2] -> 01011110
  node 3: deps [0, 6, 3] -> 00000110
  node 4: deps [5, 4, 1] -> 00111001
  node 5: deps [3, 6, 0] -> 00010100
  node 6: deps [5, 6, 0] -> 11111110
  node 7: deps [4, 0, 5] -> 11011010
  node 8: deps [2, 1, 8] -> 10000010
The network runs synchronously from the initial state 110110010 until it enters its attractor cycle.
Now node 5 is clamped to the fixed value 0: its value remains 0 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
010000110-110010110 1
```

### Example 2
**Prompt:**
```
Consider a synchronous Boolean network on n = 9 nodes.
Each node updates to a deterministic Boolean function of k other nodes, given as truth tables (dependency list, then the 2^k outputs in binary order of the dependency bits, bit j encoding dependency deps[j] = 1).
Update tables:
  node 0: deps [8, 4, 1] -> 10101111
  node 1: deps [2, 0, 3] -> 00101010
  node 2: deps [3, 8, 1] -> 01100111
  node 3: deps [0, 4, 2] -> 10100110
  node 4: deps [8, 3, 4] -> 10001110
  node 5: deps [0, 7, 4] -> 00110000
  node 6: deps [6, 0, 4] -> 00010010
  node 7: deps [7, 8, 1] -> 10110011
  node 8: deps [2, 0, 4] -> 10110010
The network runs synchronously from the initial state 111110110 until it enters its attractor cycle.
Now node 8 is clamped to the fixed value 1: its value remains 1 forever, all other nodes update normally, and the network runs synchronously from the same initial state until it enters a NEW attractor cycle.
Answer with two items separated by a single space: (1) the new attractor cycle, written in the rotation that is lexicographically smallest, its states listed in order joined by '-' where each state is an n-bit string, and (2) the first synchronization step (0-indexed, initial state is step 0) at which the clamped network's state differs from the original network's state.
```
**Answer:**
```
000101011-010101011-111101011-101101011 1
```


