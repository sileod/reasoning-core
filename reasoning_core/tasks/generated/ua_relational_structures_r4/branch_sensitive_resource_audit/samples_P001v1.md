## Level 0
### Example 1
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 3.
Capacities: cpu=4, disk=6, gpu=3.

Program:
either/or:
  seq:
    uses gpu 2*n
  seq:
    uses gpu 5
    uses gpu 3
    uses disk n

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
[gpu]
```

### Example 2
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 2.
Capacities: cpu=0, disk=2, net=9.

Program:
either/or:
  seq:
    uses net 6
    uses net 4
    uses disk n
  seq:
    uses disk 3
  seq:
    uses disk 2

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
[disk] [net]
```

## Level 2
### Example 1
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 3.
Capacities: net=24, io=6, cpu=7, gpu=11, mem=0.

Program:
seq:
  uses net 10
  uses gpu 2*n+1
  uses net 10

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
none
```

### Example 2
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 4.
Capacities: mem=20, tpu=21, cpu=77, net=1, io=0.

Program:
par:
  seq:
    uses cpu 2
    uses cpu 3*n+1
  par:
    seq:
      uses tpu 10
      uses cpu 1*n+5
      uses cpu 3*n+4
    either/or:
      seq:
        uses cpu 3*n+4
        uses mem 5
      seq:
        uses mem 3*n+1
      seq:
        uses tpu 5
  seq:
    uses cpu 2*n+4
    uses cpu 1
    uses io 5

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
[io]
```

## Level 5
### Example 1
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 4.
Capacities: io=0, mem=4, net=11, tpu=12, disk=6, gpu=7, cpu=6.

Program:
seq:
  uses cpu 8

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
[cpu]
```

### Example 2
**Prompt:**
```
A resource-audit problem. A program is a tree of blocks. In a 'seq' (sequential) block every child runs and uses of a resource add across children. In a 'par' (parallel) block every branch runs concurrently so uses of a resource also add across branches. In an 'either/or' (choice) block only one branch runs, so a resource's use is the maximum across the branches. Each statement 'uses <res> <expr>' obligates that resource by <expr>; an expression A*n+B is evaluated at the given value of n (plain numbers are constants). A resource violates the discipline if its total use across the whole program exceeds its capacity.

Variable n = 3.
Capacities: io=0, mem=4, gpu=0, net=7, disk=14, cpu=14, tpu=12.

Program:
seq:
  uses net 13
  uses gpu 10

List every resource whose use exceeds its capacity, in lexicographic (alphabetical) order, each as a bracketed token separated by spaces, e.g. [cpu] [mem]. If no resource violates, answer: none.
```
**Answer:**
```
[gpu] [net]
```
