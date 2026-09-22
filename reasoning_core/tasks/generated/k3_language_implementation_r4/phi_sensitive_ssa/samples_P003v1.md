
## Level 0

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = 1 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 3 then bB else bE
bB: [ x = (x + c); c = c + 2; t0 = 1 ] -> bH
bE: [ ] -> halt

Execute the program until it halts. What is the final value of variable x? Answer one integer.
```

### Answer

```
3
```

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = 2 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 3 then bB else bE
bB: [ x = (x * c); c = c + 1; t0 = -2 ] -> bH
bE: [ ] -> halt

Execute the program until it halts. What is the final value of variable x? Answer one integer.
```

### Answer

```
0
```


## Level 2

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = 2 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 3 then bB else bE
bB: [ x = (c - x); c = c + 2; t0 = 0 ] -> bH
bE: [ ] -> halt

Execute the program until it halts. What is the final value of variable t0? Answer one integer.
```

### Answer

```
0
```

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = 3 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 2 then bB else bE
bB: [ x = (x + x); c = c + 1; t0 = (x - x) ] -> bH
bE: [ ] -> halt

Execute the program until it halts. On the 2nd execution of the phi node in block bH, which predecessor block's edge is selected? Answer with the block identifier ('b0' or 'bB').
```

### Answer

```
bB
```


## Level 5

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = 2 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 3 then bB else bE
bB: [ x = (x - c); c = c + 1; t0 = 1; t1 = 1 ] -> bH
bE: [ ] -> halt

Execute the program until it halts. What is the final value of variable t1? Answer one integer.
```

### Answer

```
1
```

### Prompt

```
This is an arithmetic SSA program (single static assignment) with a loop and a predecessor-selected phi node. 'v = expr' assigns a variable using earlier variables; 'phi x [ b0, bB ]' makes x take the value that the predecessor block actually taken beforehand produced. A block 'bN: [ ... ] -> if cond then A else B' branches, '-> T' jumps, '-> halt' stops.

b0: [ c = 0; x = -2 ] -> bH
bH: [ phi x [ b0, bB ] ] -> if c < 7 then bB else bE
bB: [ x = (c - x); c = c + 2; t0 = (c + c); t1 = -2 ] -> bH
bE: [ ] -> halt

Execute the program until it halts. What is the final value of variable x? Answer one integer.
```

### Answer

```
2
```

