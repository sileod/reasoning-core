## Level 0, Example 1

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 3, 1
f1(B) = 1, 2
f2(C) = 3, 1
f3(D) = 2, 4
f4(C,A,B) = 5, 1, 5, 3, 3, 4, 3, 5
f5(D,B) = 1, 5, 1, 4
Evidence: none.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of C. Use variable elimination: first substitute evidence, then sum out D, A, B in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
324/563, 239/563
```

## Level 0, Example 2

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 3, 2
f1(B) = 3, 2
f2(C) = 2, 1
f3(D) = 1, 3
f4(A,B,C) = 2, 4, 3, 5, 4, 2, 1, 1
f5(D,A) = 2, 2, 3, 5
Evidence: none.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of C. Use variable elimination: first substitute evidence, then sum out B, A, D in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
872/1371, 499/1371
```

## Level 2, Example 1

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..1; E=0..1; F=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 1, 1
f1(B) = 2, 5
f2(C) = 1, 5
f3(D) = 2, 2
f4(E) = 5, 2
f5(F) = 5, 1
f6(D,E) = 4, 2, 5, 1
f7(E,B) = 1, 5, 3, 1
f8(A,D) = 5, 1, 3, 1
f9(F,E) = 4, 4, 4, 5
f10(D,C) = 2, 1, 2, 5
Evidence: none.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of F. Use variable elimination: first substitute evidence, then sum out B, D, E, A, C in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
70342/84593, 14251/84593
```

## Level 2, Example 2

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..1; E=0..1; F=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 4, 1
f1(B) = 4, 5
f2(C) = 2, 4
f3(D) = 5, 3
f4(E) = 1, 1
f5(F) = 2, 3
f6(D,B) = 4, 1, 2, 4
f7(C,D) = 5, 3, 2, 2
f8(C,A,E) = 2, 3, 5, 4, 1, 1, 2, 2
f9(F,C) = 4, 5, 2, 5
Evidence: A=1, F=0.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of D. Use variable elimination: first substitute evidence, then sum out C, E, B in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
325/513, 188/513
```

## Level 5, Example 1

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..1; E=0..1; F=0..1; G=0..2; H=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 1, 1
f1(B) = 1, 1
f2(C) = 2, 3
f3(D) = 1, 1
f4(E) = 4, 1
f5(F) = 2, 3
f6(G) = 4, 1, 2
f7(H) = 4, 2
f8(D,E,H) = 2, 3, 2, 1, 2, 2, 2, 5
f9(C,B,H) = 4, 5, 3, 1, 2, 2, 5, 5
f10(F,E,A) = 1, 5, 3, 2, 2, 5, 2, 4
f11(G,H) = 5, 1, 4, 2, 2, 2
f12(H,A) = 1, 2, 5, 1
f13(G,H,D) = 3, 4, 5, 2, 1, 3, 3, 3, 5, 1, 1, 4
f14(C,H,F) = 2, 4, 2, 5, 1, 4, 4, 5
Evidence: D=1, H=1.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of B. Use variable elimination: first substitute evidence, then sum out E, G, C, A, F in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
668/1441, 773/1441
```

## Level 5, Example 2

### Prompt

```text
Infer the distribution of one hidden variable in this discrete factor graph.
Domains: A=0..1; B=0..1; C=0..1; D=0..2; E=0..1; F=0..1; G=0..1; H=0..1.
Each factor lists nonnegative unnormalized weights in lexicographic order of its displayed arguments' value tuples (last argument changes fastest). For binary (A,B), the order is (0,0),(0,1),(1,0),(1,1).
f0(A) = 2, 4
f1(B) = 1, 1
f2(C) = 1, 2
f3(D) = 5, 2, 4
f4(E) = 2, 1
f5(F) = 4, 4
f6(G) = 5, 4
f7(H) = 1, 3
f8(A,E,H) = 4, 3, 5, 1, 3, 2, 1, 3
f9(H,G) = 2, 5, 5, 3
f10(A,F) = 1, 2, 5, 3
f11(A,B) = 3, 4, 3, 1
f12(D,E) = 4, 5, 2, 1, 4, 3
f13(D,C) = 3, 2, 3, 2, 4, 3
f14(A,G) = 1, 1, 4, 2
f15(B,D) = 1, 3, 2, 3, 2, 4
f16(A,D) = 3, 3, 3, 3, 4, 1
Evidence: none.
An assignment's weight is the product of all listed factors. Condition on the evidence by discarding inconsistent assignments, then normalize the remaining weights.
Compute the exact marginal of A. Use variable elimination: first substitute evidence, then sum out E, F, B, G, C, H, D in that order; retain the query variable and normalize.
Return only its probabilities for values 0,1,... in increasing value order, as reduced fractions (integers when integral) separated by commas. Format example: 1/3, 2/3.
```

### Answer

```text
62633331/326186483, 263553152/326186483
```
