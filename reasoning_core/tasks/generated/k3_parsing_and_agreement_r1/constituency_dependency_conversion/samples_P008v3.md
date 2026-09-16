## Level 0
### Example 1
**Prompt:**
```
Constituency parse tree:
(S (NP (Det few) (N bridge)) (VP (V lifted) (NP (Det every) (N window))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
List every labeled dependency arc. Answer format: each arc as 'governor -> dependent : label', arcs sorted by governor, then dependent, then label, joined with ' ; '.
```
**Answer:**
```
bridge -> few : det ; lifted -> bridge : subj ; lifted -> window : obj ; window -> every : det
```

### Example 2
**Prompt:**
```
Constituency parse tree:
(S (NP (Det these) (Adj deep) (N village)) (VP (V hired) (NP (Det many) (Adj fresh) (N brook))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
List every labeled dependency arc. Answer format: each arc as 'governor -> dependent : label', arcs sorted by governor, then dependent, then label, joined with ' ; '.
```
**Answer:**
```
brook -> fresh : mod ; brook -> many : det ; hired -> brook : obj ; hired -> village : subj ; village -> deep : mod ; village -> these : det
```

## Level 2
### Example 1
**Prompt:**
```
Constituency parse tree:
(S (NP (Det this) (Adj dull) (Adj cool) (N teacher)) (VP (V held) (NP (Det both) (N bog)) (NP (Det that) (Adj fresh) (Adj rapid) (N brook))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
Consider the word 'brook' in the dependency tree. What is its governor and its dependents with their labels? The root token has governor ROOT. Answer format: 'GOV=<governor or ROOT> ; DEPS=<word:label, ...>' with dependents sorted by word then label, or 'NONE' if it has none.
```
**Answer:**
```
GOV=held ; DEPS=fresh:mod, rapid:mod, that:det
```

### Example 2
**Prompt:**
```
Constituency parse tree:
(S (NP (Det an) (Adj deep) (Adj happy) (N hollow)) (VP (V made) (NP (Det those) (N shore)) (NP (Det a) (Adj clear) (N house))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
List every labeled dependency arc. Answer format: each arc as 'governor -> dependent : label', arcs sorted by governor, then dependent, then label, joined with ' ; '.
```
**Answer:**
```
hollow -> an : det ; hollow -> deep : mod ; hollow -> happy : mod ; house -> a : det ; house -> clear : mod ; made -> hollow : subj ; made -> house : obj ; made -> shore : obj ; shore -> those : det
```

## Level 5
### Example 1
**Prompt:**
```
Constituency parse tree:
(S (NP (Det these) (Adj bright) (Adj dim) (Adj ham) (N cliff)) (VP (V painted) (PP (P of) (NP (Det that) (N howl))) (NP (Det a) (N temple))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
Consider the word 'howl' in the dependency tree. What is its governor and its dependents with their labels? The root token has governor ROOT. Answer format: 'GOV=<governor or ROOT> ; DEPS=<word:label, ...>' with dependents sorted by word then label, or 'NONE' if it has none.
```
**Answer:**
```
GOV=of ; DEPS=that:det
```

### Example 2
**Prompt:**
```
Constituency parse tree:
(S (NP (Det each) (Adj bare) (Adj old) (Adj rapid) (N frith)) (VP (V bought) (NP (Det an) (Adj bright) (N cat)) (NP (Det these) (N bird))))

Head-percolation rules:
- The head of S is its VP child.
- The head of VP is its V child.
- The head of NP is its N child.
- The head of PP is its P child.
- A preterminal's head is its word.
For every non-head child, draw an arc from the parent's head word to that child's head word, labeled by grammatical function: S's NP child is 'subj'; VP's NP child is 'obj' and VP's PP child is 'arg'; NP's Det and Adj children are 'det' and 'mod', and NP's PP child is 'mod'; PP's NP child is 'comp'.
Consider the word 'frith' in the dependency tree. What is its governor and its dependents with their labels? The root token has governor ROOT. Answer format: 'GOV=<governor or ROOT> ; DEPS=<word:label, ...>' with dependents sorted by word then label, or 'NONE' if it has none.
```
**Answer:**
```
GOV=bought ; DEPS=bare:mod, each:det, old:mod, rapid:mod
```

