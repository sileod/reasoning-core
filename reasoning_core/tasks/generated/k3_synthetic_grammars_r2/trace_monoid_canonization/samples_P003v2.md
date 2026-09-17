# P003v2 samples

## Level 0

### canonical

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ab, ac, bd. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d. Recorded word: ddcbba.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use lexicographic Kahn topological sorting: repeatedly take the smallest available label. Give the lexicographically least word in the class. Answer with only the word, for example abac.
```

**Answer:**
```
ddacbb
```

### size

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ac, cd. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d. Recorded word: bcadad.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Count distinct words, not swap sequences. You may use dynamic programming over completed occurrence sets in the dependency DAG. Give the class size. Answer with only an integer, for example 12.
```

**Answer:**
```
5
```

### layers

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ad, bd. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d. Recorded word: bdabac.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use Foata layering: repeatedly remove ALL currently predecessor-free occurrences simultaneously as the next layer. Sort labels alphabetically inside each layer. Give the layers in removal order, joined by dots; for example ab.c.ab. Answer with only that string.
```

**Answer:**
```
bd.a.b.a.c
```

## Level 2

### size

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ac, ad, bc, be, ce, de. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e. Recorded word: edbbdadc.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Count distinct words, not swap sequences. You may use dynamic programming over completed occurrence sets in the dependency DAG. Give the class size. Answer with only an integer, for example 12.
```

**Answer:**
```
22
```

### canonical

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ac, ad, cd, de. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e. Recorded word: cbdddcae.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use lexicographic Kahn topological sorting: repeatedly take the smallest available label. Give the lexicographically least word in the class. Answer with only the word, for example abac.
```

**Answer:**
```
cbacddde
```

### layers

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ab, ac, ad, bd. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e. Recorded word: cdbbeacc.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use Foata layering: repeatedly remove ALL currently predecessor-free occurrences simultaneously as the next layer. Sort labels alphabetically inside each layer. Give the layers in removal order, joined by dots; for example ab.c.ab. Answer with only that string.
```

**Answer:**
```
c.bd.b.e.ac.c
```

## Level 5

### canonical

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ab, ac, ad, af, bd, be, bf, cd, ce, de, ef. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e < f. Recorded word: dfaedfecabf.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use lexicographic Kahn topological sorting: repeatedly take the smallest available label. Give the lexicographically least word in the class. Answer with only the word, for example abac.
```

**Answer:**
```
adeeafdfcbf
```

### layers

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ab, ac, ad, ae, bc, bd, be, bf, de, ef. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e < f. Recorded word: fbbdfaaceed.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Use Foata layering: repeatedly remove ALL currently predecessor-free occurrences simultaneously as the next layer. Sort labels alphabetically inside each layer. Give the layers in removal order, joined by dots; for example ab.c.ab. Answer with only that string.
```

**Answer:**
```
bf.bd.f.ac.ade.e
```

### size

**Prompt:**
```
A scheduler records a word of operation labels. Adjacent occurrences may be swapped exactly when their labels form one of these unordered commuting pairs: ab, ac, ad, ae, bd, be, de, ef. No other pairs commute; equal labels are dependent. The equivalence class contains all distinct words reachable by any number of these swaps. Alphabetical order is a < b < c < d < e < f. Recorded word: eedfabfbacd.
To reason about this trace, order each occurrence after every earlier occurrence with a dependent label (the dependency DAG). Count distinct words, not swap sequences. You may use dynamic programming over completed occurrence sets in the dependency DAG. Give the class size. Answer with only an integer, for example 12.
```

**Answer:**
```
256
```
