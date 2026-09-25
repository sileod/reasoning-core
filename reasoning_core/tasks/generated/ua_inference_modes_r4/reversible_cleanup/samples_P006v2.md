## Level 0

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 4 (size 3): combine value 0 and value 3
value 3 (size 1): combine value 1 and value 2
value 2 (size 5): base material
value 1 (size 2): base material
value 0 (size 4): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
7
```

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 4 (size 2): combine value 0 and value 3
value 3 (size 4): combine value 1 and value 2
value 2 (size 3): base material
value 1 (size 5): base material
value 0 (size 4): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
8
```

## Level 2

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 12 (size 13): combine value 4 and value 11
value 11 (size 3): combine value 9 and value 10
value 10 (size 4): base material
value 9 (size 9): combine value 5 and value 8
value 8 (size 10): combine value 6 and value 7
value 7 (size 8): base material
value 6 (size 10): base material
value 5 (size 5): base material
value 4 (size 10): combine value 0 and value 3
value 3 (size 8): combine value 1 and value 2
value 2 (size 9): base material
value 1 (size 7): base material
value 0 (size 8): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
19
```

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 12 (size 1): combine value 6 and value 11
value 11 (size 12): combine value 7 and value 10
value 10 (size 10): combine value 8 and value 9
value 9 (size 10): base material
value 8 (size 11): base material
value 7 (size 6): base material
value 6 (size 3): combine value 2 and value 5
value 5 (size 11): combine value 3 and value 4
value 4 (size 5): base material
value 3 (size 8): base material
value 2 (size 6): combine value 0 and value 1
value 1 (size 6): base material
value 0 (size 8): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
24
```

## Level 5

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 24 (size 12): combine value 2 and value 23
value 23 (size 24): combine value 9 and value 22
value 22 (size 7): combine value 16 and value 21
value 21 (size 9): combine value 19 and value 20
value 20 (size 13): base material
value 19 (size 15): combine value 17 and value 18
value 18 (size 5): base material
value 17 (size 11): base material
value 16 (size 15): combine value 12 and value 15
value 15 (size 4): combine value 13 and value 14
value 14 (size 16): base material
value 13 (size 5): base material
value 12 (size 7): combine value 10 and value 11
value 11 (size 9): base material
value 10 (size 2): base material
value 9 (size 1): combine value 3 and value 8
value 8 (size 11): combine value 4 and value 7
value 7 (size 22): combine value 5 and value 6
value 6 (size 7): base material
value 5 (size 16): base material
value 4 (size 14): base material
value 3 (size 7): base material
value 2 (size 22): combine value 0 and value 1
value 1 (size 16): base material
value 0 (size 17): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
57
```

### Prompt
```
We maintain a workspace holding intermediate results. Every value that is present consumes workspace equal to its size in resource tokens. Base materials are provided directly: loading one makes it resident and consumes its size. Combining two values replaces both of their tokens with the combined value's tokens, and you may drop a resident value when it is no longer needed. Using the Sethi-Ullman / tree register allocation order, compute the minimal peak number of resource tokens that are resident at any one moment needed to produce the root value.
value 24 (size 28): combine value 6 and value 23
value 23 (size 31): combine value 7 and value 22
value 22 (size 1): combine value 12 and value 21
value 21 (size 30): combine value 17 and value 20
value 20 (size 1): combine value 18 and value 19
value 19 (size 14): base material
value 18 (size 8): base material
value 17 (size 26): combine value 13 and value 16
value 16 (size 26): combine value 14 and value 15
value 15 (size 13): base material
value 14 (size 15): base material
value 13 (size 14): base material
value 12 (size 1): combine value 10 and value 11
value 11 (size 10): base material
value 10 (size 27): combine value 8 and value 9
value 9 (size 17): base material
value 8 (size 19): base material
value 7 (size 18): base material
value 6 (size 8): combine value 0 and value 5
value 5 (size 16): combine value 1 and value 4
value 4 (size 2): combine value 2 and value 3
value 3 (size 20): base material
value 2 (size 12): base material
value 1 (size 4): base material
value 0 (size 1): base material
The answer is one integer: the minimal peak token count.
```

### Answer
```
50
```

