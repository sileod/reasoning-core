# samples_P003v1

## Level 0

### Example 1

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag1', 'tag3', 'tag4']
New adds (delivered in order, before removes): ['tag4']
Causal removes (delivered immediately after adds): ['tag3']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag6']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag3', 'tag5']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag1
tag4
tag6
```

### Example 2

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag0', 'tag1', 'tag6']
New adds (delivered in order, before removes): ['tag5', 'tag6']
Causal removes (delivered immediately after adds): ['tag1', 'tag5']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag4']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag2', 'tag5']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag0
tag4
tag6
```

## Level 2

### Example 1

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag0', 'tag3', 'tag5', 'tag8', 'tag9']
New adds (delivered in order, before removes): ['tag1', 'tag3', 'tag7']
Causal removes (delivered immediately after adds): ['tag0', 'tag8', 'tag9']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag6', 'tag7']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag3', 'tag9']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag1
tag3
tag5
tag6
tag7
```

### Example 2

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag0', 'tag1', 'tag2', 'tag4', 'tag8']
New adds (delivered in order, before removes): ['tag1', 'tag5', 'tag6']
Causal removes (delivered immediately after adds): ['tag1', 'tag2', 'tag5', 'tag6']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag5']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag1', 'tag3', 'tag6']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag0
tag4
tag5
tag8
```

## Level 5

### Example 1

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag0', 'tag3', 'tag5', 'tag6', 'tag7', 'tag8', 'tag10', 'tag11']
New adds (delivered in order, before removes): ['tag0', 'tag1', 'tag2', 'tag3']
Causal removes (delivered immediately after adds): ['tag2', 'tag6', 'tag7', 'tag10', 'tag11']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag1', 'tag4']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag1', 'tag10', 'tag11', 'tag12']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag0
tag1
tag3
tag4
tag5
tag8
```

### Example 2

Prompt:

```
You are merging partial CRDT updates for a set whose membership follows observed-remove semantics: a tag is permanently gone once a causal remove of it has been observed, and a later replayed (duplicate/stale) add of an already-removed tag must NOT revive it.
Initial visible tags: ['tag1', 'tag3', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10', 'tag12']
New adds (delivered in order, before removes): ['tag2', 'tag3', 'tag5', 'tag7', 'tag8', 'tag11']
Causal removes (delivered immediately after adds): ['tag8', 'tag9', 'tag10', 'tag12']
Delayed adds (arrive late, must not be revoked unless already-removed tags being replayed): ['tag0', 'tag5', 'tag11']
Replayed duplicate adds (stale, must not revive any removed tag): ['tag8', 'tag9', 'tag11', 'tag12']
What is the final set of visible tag strings?
Answer as the list of visible tag strings, one per line, in lexicographic order, with no duplicates. If the set is empty, answer with an empty line.
```

Answer:

```
tag0
tag1
tag2
tag3
tag5
tag6
tag7
tag11
```
