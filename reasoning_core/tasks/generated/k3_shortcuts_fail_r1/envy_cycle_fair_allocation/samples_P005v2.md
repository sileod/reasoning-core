## Level 0

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5
A0:    0 0 0 5 5 4
A1:    6 6 6 2 0 1
A2:    5 4 6 6 4 3

Pick order is A0,A1,A2 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A0 I1:A0 I2:A1 I3:A1 I4:A2 I5:A2

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A1 I1:A1 I2:A2 I3:A2 I4:A0 I5:A0

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5
A0:    6 4 1 3 5 6
A1:    5 5 0 6 5 4
A2:    1 6 4 6 0 0

Pick order is A0,A1,A2 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A0 I1:A1 I2:A1 I3:A2 I4:A0 I5:A2

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A0 I1:A2 I2:A2 I3:A1 I4:A0 I5:A1

## Level 2

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5 I6 I7 I8 I9
A0:    1 3 8 6 5 3 1 3 7 2
A1:    0 2 6 6 0 8 2 8 0 8
A2:    2 5 8 6 1 5 5 4 3 7
A3:    6 8 2 7 8 4 8 2 6 6
A4:    5 2 0 2 4 4 3 6 7 8

Pick order is A0,A1,A2,A3,A4 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A3 I1:A1 I2:A0 I3:A4 I4:A2 I5:A4 I6:A2 I7:A3 I8:A0 I9:A1

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A4 I1:A2 I2:A0 I3:A1 I4:A3 I5:A1 I6:A3 I7:A4 I8:A0 I9:A2

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5 I6 I7 I8 I9
A0:    1 4 2 1 8 1 8 2 5 5
A1:    1 0 7 6 2 4 8 5 0 0
A2:    6 3 0 0 0 1 7 1 6 1
A3:    6 8 4 4 0 8 6 3 3 5
A4:    8 8 8 4 5 1 0 0 3 3

Pick order is A0,A1,A2,A3,A4 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A4 I1:A0 I2:A1 I3:A1 I4:A3 I5:A4 I6:A2 I7:A0 I8:A2 I9:A3

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A4 I1:A3 I2:A1 I3:A1 I4:A0 I5:A4 I6:A2 I7:A3 I8:A2 I9:A0

## Level 5

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5 I6 I7 I8 I9 I10 I11 I12 I13 I14 I15
A0:    8 11 9 6 9 9 1 2 6 3 11 7 10 0 2 10
A1:    5 11 9 0 9 4 3 7 11 11 8 3 7 0 6 6
A2:    1 9 9 7 2 1 10 4 2 5 4 3 6 7 1 5
A3:    11 7 6 8 10 6 7 9 9 4 11 0 2 11 3 0
A4:    8 2 0 4 5 7 0 8 11 3 5 7 10 4 3 11
A5:    11 9 7 3 1 10 11 9 3 1 9 10 3 6 7 2
A6:    1 8 0 5 9 2 11 11 11 4 0 3 6 8 4 9
A7:    8 8 11 7 5 1 6 0 0 7 0 4 2 11 9 7

Pick order is A0,A1,A2,A3,A4,A5,A6,A7 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A4 I1:A2 I2:A7 I3:A7 I4:A2 I5:A4 I6:A5 I7:A3 I8:A5 I9:A0 I10:A0 I11:A3 I12:A6 I13:A6 I14:A1 I15:A1

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A4 I1:A0 I2:A7 I3:A7 I4:A0 I5:A4 I6:A6 I7:A5 I8:A6 I9:A3 I10:A3 I11:A5 I12:A2 I13:A2 I14:A1 I15:A1

### Example

**Prompt:**

```
Agents choose items in round-robin order. On each turn, an agent takes one of the remaining items (the choice is arbitrary).

Valuations (rows are agents, columns are items):
items:  I0 I1 I2 I3 I4 I5 I6 I7 I8 I9 I10 I11 I12 I13 I14 I15
A0:    2 11 3 10 9 10 10 1 7 9 9 4 7 7 8 2
A1:    7 7 1 9 1 7 7 1 4 5 6 5 4 7 4 9
A2:    3 5 8 9 4 3 0 7 3 6 6 10 5 0 10 6
A3:    7 6 3 4 6 3 11 9 8 4 4 0 0 3 9 10
A4:    6 6 9 4 11 1 1 9 10 4 8 0 5 0 9 4
A5:    6 11 3 9 6 9 5 5 2 3 1 9 10 6 6 6
A6:    6 6 2 6 5 4 4 5 2 7 7 1 1 4 6 7
A7:    1 7 3 1 9 3 6 9 6 9 6 8 6 9 11 2

Pick order is A0,A1,A2,A3,A4,A5,A6,A7 (first round), repeating until every item is taken.
This produces the initial item-to-agent allocation (item label: owning agent): I0:A2 I1:A6 I2:A3 I3:A2 I4:A1 I5:A4 I6:A4 I7:A0 I8:A5 I9:A7 I10:A3 I11:A5 I12:A1 I13:A0 I14:A7 I15:A6

Now resolve envy: recompute which agent envies which (an agent envies you if it values your bundle strictly more than its own), then apply the envy-cycle elimination algorithm -- repeatedly find a directed cycle in the envy graph and rotate every item along the cycle one step (the cycle owner passes its items to the next agent). Repeat until no envy cycle remains.

Give the final envy-free-up-to-one-item allocation as item-to-agent pairs in increasing item-index order, each of the form I{item}:A{agent}, joined by spaces.
```

**Answer:**

I0:A1 I1:A6 I2:A2 I3:A1 I4:A4 I5:A0 I6:A0 I7:A3 I8:A5 I9:A7 I10:A2 I11:A5 I12:A4 I13:A3 I14:A7 I15:A6
