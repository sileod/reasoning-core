## Level 0

### Example 1

We run a grow-only counter CRDT across replicas; a replica only counts upward and merges by taking the max contribution for every replica.
Initial counts: r0=3, r1=3.
r0 increments by 3.
After all operations, which value does replica r1 hold?
Answer as counter:N (N is the counted value).

**Answer**: `counter:3`

### Example 2

We run a last-writer-wins register CRDT; each replica holds (timestamp, value) and the highest timestamp wins.
Initial state: r0=(ts1,v1), r1=(ts3,v4).
r0 sets value to 0.
After all operations, which value does replica r0 hold?
Answer as reg:val.

**Answer**: `reg:0`

## Level 2

### Example 1

We run a grow-only counter CRDT across replicas; a replica only counts upward and merges by taking the max contribution for every replica.
Initial counts: r0=1, r1=1.
r1 increments by 1.
r0 merges with another replica whose state is r0=2; r1=2.
r0 increments by 3.
r1 increments by 2.
After all operations, which value does replica r0 hold?
Answer as counter:N (N is the counted value).

**Answer**: `counter:5`

### Example 2

We run a PN counter CRDT; each replica tracks a positive and negative count and the net is positive minus negative.
Initial counts: r0={3,1}, r1={2,1}.
r1 increments by -2.
r0 merges with another replica whose state is r0={1,3}; r1={3,2}.
r0 increments by -2.
r0 increments by 2.
After all operations, which value does replica r0 hold?
Answer as pn:N (N is the net value).

**Answer**: `pn:0`

## Level 5

### Example 1

We run a last-writer-wins register CRDT; each replica holds (timestamp, value) and the highest timestamp wins.
Initial state: r0=(ts3,v3), r1=(ts3,v4), r2=(ts3,v8).
r2 sets value to 2.
r0 sets value to 3.
r1 sets value to 2.
r2 merges with another replica whose state is r0=(ts8,v7); r1=(ts5,v0); r2=(ts10,v2).
r0 sets value to 6.
r2 sets value to 1.
r2 sets value to 3.
r2 merges with another replica whose state is r0=(ts8,v7); r1=(ts5,v0); r2=(ts10,v2).
After all operations, which value does replica r2 hold?
Answer as reg:val.

**Answer**: `reg:2`

### Example 2

We run an add-wins set CRDT; each replica holds a set and removes only tombstone the element.
Initial sets: r0={}, r1={}, r2={d}.
r1 removes b.
r0 removes b.
r0 adds c.
r1 merges with another replica whose state is r0={a,d}; r1={}; r2={c,d}.
r0 adds c.
r0 adds a.
r1 merges with another replica whose state is r0={}; r1={}; r2={b}.
r1 removes a.
After all operations, which value does replica r1 hold?
Answer as set:[a,b] (the surviving elements).

**Answer**: `set:[]`
