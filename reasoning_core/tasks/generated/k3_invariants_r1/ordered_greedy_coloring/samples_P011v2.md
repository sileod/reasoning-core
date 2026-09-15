# Samples for ordered_greedy_coloring (P011v2)

## Level 0

### Prompt
```
A graph has vertices v0..v5 with edges: v0:{v1} v1:{v0,v2} v2:{v1,v3} v3:{v2,v4} v4:{v3,v5} v5:{v4}.
The greedy coloring processes them in order v2 -> v1 -> v4 -> v5 -> v3 -> v0.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
What color does v0 receive? Answer with one integer.
```

### Answer
```
1
```

### Prompt
```
A graph has vertices v0..v5 with edges: v0:{v1} v1:{v0,v2} v2:{v1,v3} v3:{v2,v4} v4:{v3,v5} v5:{v4}.
The greedy coloring processes them in order v4 -> v3 -> v1 -> v5 -> v0 -> v2.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
What color does v2 receive? Answer with one integer.
```

### Answer
```
3
```

## Level 2

### Prompt
```
A graph has vertices v0..v9 with edges: v0:{v1,v9} v1:{v0,v2} v2:{v1,v3} v3:{v2,v4} v4:{v3,v5} v5:{v4,v6} v6:{v5,v7} v7:{v6,v8} v8:{v7,v9} v9:{v0,v8}.
The greedy coloring processes them in order v0 -> v9 -> v8 -> v4 -> v1 -> v2 -> v3 -> v6 -> v5 -> v7.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
What color does v7 receive? Answer with one integer.
```

### Answer
```
2
```

### Prompt
```
A graph has vertices v0..v9 with edges: v0:{v1,v9} v1:{v0,v2} v2:{v1,v3} v3:{v2,v4} v4:{v3,v5} v5:{v4,v6} v6:{v5,v7} v7:{v6,v8} v8:{v7,v9} v9:{v0,v8}.
The greedy coloring processes them in order v7 -> v1 -> v5 -> v0 -> v8 -> v2 -> v6 -> v3 -> v9 -> v4.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
What color does v4 receive? Answer with one integer.
```

### Answer
```
2
```

## Level 5

### Prompt
```
A graph has vertices v0..v15 with edges: v0:{v1,v2} v1:{v0,v3} v2:{v0,v3,v4} v3:{v1,v2,v5} v4:{v2,v5,v6} v5:{v3,v4,v7} v6:{v4,v7,v8} v7:{v5,v6,v9} v8:{v6,v9,v10} v9:{v7,v8,v11} v10:{v8,v11,v12} v11:{v9,v10,v13} v12:{v10,v13,v14} v13:{v11,v12,v15} v14:{v12,v15} v15:{v13,v14}.
The greedy coloring processes them in order v4 -> v14 -> v15 -> v13 -> v12 -> v6 -> v9 -> v8 -> v3 -> v11 -> v0 -> v10 -> v7 -> v1 -> v2 -> v5.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
What color does v5 receive? Answer with one integer.
```

### Answer
```
2
```

### Prompt
```
A graph has vertices v0..v15 with edges: v0:{v1,v3} v1:{v0,v2,v4} v2:{v1,v5} v3:{v0,v4,v6} v4:{v1,v3,v5,v7} v5:{v2,v4,v8} v6:{v3,v7,v9} v7:{v4,v6,v8,v10} v8:{v5,v7,v11} v9:{v6,v10,v12} v10:{v7,v9,v11,v13} v11:{v8,v10,v14} v12:{v9,v13,v15} v13:{v10,v12,v14} v14:{v11,v13} v15:{v12}.
The greedy coloring processes them in order v12 -> v10 -> v8 -> v1 -> v15 -> v0 -> v3 -> v2 -> v6 -> v14 -> v4 -> v7 -> v5 -> v13 -> v11 -> v9.
Each vertex receives the smallest color 1,2,3,... not yet used by any of its already-colored neighbors.
List the full assignment as v0,v1,... colors separated by spaces.
```

### Answer
```
2 1 2 1 2 3 2 3 1 3 1 2 1 2 1 2
```
