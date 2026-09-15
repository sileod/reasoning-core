# samples_P004v1

## Level 0

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: ld r3 = mem[r0]
i1: sub r1 = r0 r3
i2: mul r1 = r2 r3
i3: mul r2 = r1 r1
i4: and r2 = r0 r0

Answer with a single integer: the total stall cycles.
```

**Answer**

`3`

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: or r2 = r0 r2
i1: ld r1 = mem[r2]
i2: ld r1 = mem[r1]
i3: or r0 = r1 r2
i4: div r0 = r2 r1

Answer with a single integer: the total stall cycles.
```

**Answer**

`2`


## Level 2

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: div r0 = r3 r0
i1: mul r3 = r0 r0
i2: ld r1 = mem[r1]
i3: ld r0 = mem[r3]
i4: ld r0 = mem[r1]
i5: sub r2 = r1 r2
i6: sub r2 = r3 r3
i7: div r0 = r0 r1
i8: ld r3 = mem[r3]

Answer with a single integer: the total stall cycles.
```

**Answer**

`3`

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: or r1 = r1 r1
i1: ld r0 = mem[r1]
i2: and r3 = r2 r0
i3: sub r2 = r1 r0
i4: mul r0 = r1 r0
i5: add r2 = r1 r0
i6: sub r1 = r3 r3
i7: div r3 = r2 r2
i8: or r2 = r3 r2

Answer with a single integer: the total stall cycles.
```

**Answer**

`5`


## Level 5

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: and r2 = r4 r4
i1: ld r1 = mem[r3]
i2: add r4 = r0 r4
i3: or r2 = r1 r3
i4: div r3 = r3 r4
i5: add r3 = r4 r3
i6: ld r1 = mem[r4]
i7: mul r0 = r2 r3
i8: ld r2 = mem[r0]
i9: ld r0 = mem[r1]
i10: div r3 = r3 r2
i11: div r0 = r0 r2
i12: sub r0 = r2 r0
i13: div r4 = r0 r2
i14: div r0 = r1 r1

Answer with a single integer: the total stall cycles.
```

**Answer**

`6`

**Example prompt**

```
An in-order single-issue pipelined processor with five stages (Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. Instructions issue in program order, one per cycle, unless a dependency forces a stall. Each instruction reads its source registers when it enters Execute. A result becomes usable for a dependent instruction's Execute stage according to its producing class:
- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;
- ld: usable one cycle after the producer's Memory stage (load-use);
- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).
When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, inserting one stall cycle per extra cycle of waiting, and this delays every later instruction. Compute the total number of stall cycles inserted (the total bubbles; answer 0 if none).
Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.

i0: ld r0 = mem[r2]
i1: and r3 = r3 r1
i2: mul r2 = r1 r1
i3: add r2 = r0 r0
i4: ld r2 = mem[r2]
i5: ld r4 = mem[r2]
i6: sub r0 = r1 r0
i7: div r4 = r1 r3
i8: add r1 = r4 r4
i9: and r0 = r3 r0
i10: and r2 = r2 r4
i11: add r2 = r1 r0
i12: mul r0 = r2 r1
i13: or r2 = r4 r4
i14: mul r2 = r3 r0

Answer with a single integer: the total stall cycles.
```

**Answer**

`4`

