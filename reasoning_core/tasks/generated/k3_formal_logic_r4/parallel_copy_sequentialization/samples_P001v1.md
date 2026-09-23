# Parallel copy sequentialization samples

## Level 0

### Example 1

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r4 (exactly 5 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r3:=r4
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
r3=r4
```

### Example 2

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r4 (exactly 5 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r1:=r2
r4:=r3
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
r1=r2;r4=r3
```

## Level 2

### Example 1

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r6 (exactly 7 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r0:=r6
r1:=r2
r2:=r0
r3:=r4
r6:=r1
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
t=r0;r0=r6;r6=r1;r1=r2;r2=t;r3=r4
```

### Example 2

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r6 (exactly 7 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r3:=r2
r4:=r6
r5:=r1
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
r3=r2;r4=r6;r5=r1
```

## Level 5

### Example 1

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r9 (exactly 10 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r0:=r6
r1:=r5
r2:=r4
r3:=r9
r4:=r1
r5:=r2
r6:=r8
r7:=r0
r8:=r7
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
t=r0;r0=r6;r6=r8;r8=r7;r7=t;t=r1;r1=r5;r5=r2;r2=r4;r4=t;r3=r9
```

### Example 2

**Prompt:**

```
Parallel copy problem. Registers are numbered r0 through r9 (exactly 10 registers).
Simultaneously, as one parallel step, the following transfers must happen; each 'dst:=src' means the value currently in src is to end up in dst:
r1:=r0
r8:=r4
Sequentialize these into ordinary single-register move instructions (each move writes exactly one register, 'a=b' copies b's current value into a). You may use one scratch register t, initially holding garbage; a value is only safe to overwrite once every copy that still needs it has read it. Use a swap for any two-cycle and t for any longer permutation cycle.
Answer with ONLY the ordered move list as one canonical string, register numbers as in the input, scratch written as 't', each move semicolon-terminated with no spaces, e.g. 'r1=r2;r3=r1;'. No prose.
```

**Answer:**

```
r8=r4;r1=r0
```

