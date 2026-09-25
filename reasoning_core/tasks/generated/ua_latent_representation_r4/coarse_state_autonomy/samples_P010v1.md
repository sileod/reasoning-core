## Level 0
### Example 1
**Prompt**
```
There are 4 fine states 0..3 and 2 aggregate states 0..1. The aggregation map (fine state -> aggregate state) is: [0:0, 1:1, 2:0, 3:0].
The fine-state transition map is (fine state -> next fine state): [0:1, 1:0, 2:3, 3:1].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
2,0
```

### Example 2
**Prompt**
```
There are 4 fine states 0..3 and 2 aggregate states 0..1. The aggregation map (fine state -> aggregate state) is: [0:1, 1:0, 2:1, 3:1].
The fine-state transition map is (fine state -> next fine state): [0:1, 1:2, 2:2, 3:1].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
3,0
```

## Level 2
### Example 1
**Prompt**
```
There are 8 fine states 0..7 and 3 aggregate states 0..2. The aggregation map (fine state -> aggregate state) is: [0:1, 1:1, 2:1, 3:0, 4:1, 5:1, 6:2, 7:0].
The fine-state transition map is (fine state -> next fine state): [0:6, 1:6, 2:6, 3:2, 4:6, 5:6, 6:7, 7:0].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
closed
```

### Example 2
**Prompt**
```
There are 8 fine states 0..7 and 3 aggregate states 0..2. The aggregation map (fine state -> aggregate state) is: [0:0, 1:1, 2:0, 3:2, 4:2, 5:0, 6:1, 7:0].
The fine-state transition map is (fine state -> next fine state): [0:7, 1:1, 2:7, 3:1, 4:1, 5:0, 6:3, 7:0].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
1,1
```

## Level 5
### Example 1
**Prompt**
```
There are 14 fine states 0..13 and 5 aggregate states 0..4. The aggregation map (fine state -> aggregate state) is: [0:1, 1:2, 2:1, 3:3, 4:1, 5:0, 6:3, 7:0, 8:1, 9:4, 10:1, 11:3, 12:4, 13:3].
The fine-state transition map is (fine state -> next fine state): [0:13, 1:6, 2:5, 3:0, 4:7, 5:8, 6:8, 7:8, 8:7, 9:1, 10:5, 11:10, 12:1, 13:10].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
0,3
```

### Example 2
**Prompt**
```
There are 14 fine states 0..13 and 5 aggregate states 0..4. The aggregation map (fine state -> aggregate state) is: [0:0, 1:0, 2:4, 3:4, 4:3, 5:4, 6:2, 7:3, 8:4, 9:3, 10:1, 11:3, 12:1, 13:4].
The fine-state transition map is (fine state -> next fine state): [0:0, 1:9, 2:10, 3:12, 4:6, 5:10, 6:10, 7:6, 8:12, 9:6, 10:12, 11:6, 12:12, 13:10].
An abstraction has no hidden detail ('closed') if, within every aggregate state, all fine states map to the same aggregate state under the transition. Determine whether this aggregation is closed.
Answer exactly 'closed', or if not closed give one witness pair 'f,c' where f is a fine state and c its resulting aggregate state, such that another fine state in the same aggregate maps to a different aggregate state.
```
**Answer**
```
0,0
```
