# Level 0

## Example 1

### Prompt

```
Compare the two ground terms A = c0 and B = f1(c0) under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c0 > c1, c0 > f0. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the multiset extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {greater, less, incomparable or equivalent}.
```

### Answer

```
less
```

## Example 2

### Prompt

```
Compare the two ground terms A = c1 and B = f0(f1(c0,f0)) under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c1 > c0, f0 > c1. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the lexicographic extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {equivalent, greater, incomparable or less}.
```

### Answer

```
less
```

# Level 2

## Example 1

### Prompt

```
Compare the two ground terms A = f1(c1,f2(c1,f1(f1,f0))) and B = c0 under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c0 > c1, c1 > f1, f0 > f2, f1 > f0. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the lexicographic extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {greater, less, equivalent or incomparable}.
```

### Answer

```
less
```

## Example 2

### Prompt

```
Compare the two ground terms A = f3(f3(f2(f1,f3),f3(f0,c1))) and B = f1(f2(f2(f2,f1),c1),f2(c0,c1)) under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c1 > c0, f0 > c1, f1 > f0, f2 > f0. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the lexicographic extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {greater, less, incomparable or equivalent}.
```

### Answer

```
incomparable
```

# Level 5

## Example 1

### Prompt

```
Compare the two ground terms A = f5(f2(f1(f4(c2)))) and B = c1 under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c0 > c1, c0 > f2, c1 > f0, c2 > f3, f0 > c2, f1 > f0, f2 > f1, f3 > f4. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the lexicographic extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {equivalent, greater, incomparable or less}.
```

### Answer

```
incomparable
```

## Example 2

### Prompt

```
Compare the two ground terms A = f0(f4(c1,f4(f4,c2))) and B = f1(f4(c1,f4(f4,c2))) under the recursive path ordering, where the (strict) symbol precedence > is the transitive closure of: c1 > f0, c2 > c1, f0 > f3, f1 > f0, f2 > c2, f2 > f1, f3 > c0, f4 > c2, f4 > f1. Subterms may dominate as in the standard recursive path ordering, and terms sharing a root symbol are compared by the lexicographic extension of the ordering over their argument lists. Is term A greater than, less than, equivalent to, or incomparable with term B (adjective describing A relative to B)? Answer with exactly one word from {incomparable, greater, less or equivalent}.
```

### Answer

```
greater
```
