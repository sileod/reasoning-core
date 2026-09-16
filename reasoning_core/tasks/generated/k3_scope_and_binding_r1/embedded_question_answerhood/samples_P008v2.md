# Samples: embedded_question_answerhood (P008v2)

Each example lists one or more sentences embedding a wh-question under know, tell or wonder. The gold answer is the ordered sequence of readings (exhaustive, mention-some, or pair-list), one per sentence.

## Level 0

### Level 0 - Example 1

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Sara knows which cafe is still open after nine.
```

Answer:

```
mention-some
```

### Level 0 - Example 2

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Nora knows which colleague is available to cover the shift.
```

Answer:

```
mention-some
```

## Level 2

### Level 2 - Example 1

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Mina knows which colleague is available to cover the shift.
2) Mina wonders who should present first.
```

Answer:

```
mention-some exhaustive
```

### Level 2 - Example 2

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Omar wonders which route the bus takes.
2) Omar knows who can fix the broken tap.
```

Answer:

```
exhaustive mention-some
```

## Level 5

### Level 5 - Example 1

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Lia wonders which guest reserved which room.
2) Mina knows which nearby shop still has the medicine in stock.
3) Kay wonders which route the bus takes.
4) Omar knows where she can buy a newspaper at night.
```

Answer:

```
pair-list mention-some exhaustive mention-some
```

### Level 5 - Example 2

Prompt:

```
For each numbered sentence, an embedded wh-question appears under the verbs know, tell, or wonder. Decide which reading that complement receives and reply with exactly that many verdict words, one per sentence in the same order, separated by single spaces.

Convention: a clause with two wh-phrases is pair-list; a wonder-complement is exhaustive; a know or tell clause carrying a possibility marker (can, able, available, in stock, open, free) is mention-some; every other know or tell clause is exhaustive.

1) Kay knows who was hired for the project.
2) Mina told Ina who submitted the proposal.
3) Kay knows who can fix the broken tap.
4) Mina wonders which book Pia chose.
```

Answer:

```
exhaustive exhaustive mention-some exhaustive
```
