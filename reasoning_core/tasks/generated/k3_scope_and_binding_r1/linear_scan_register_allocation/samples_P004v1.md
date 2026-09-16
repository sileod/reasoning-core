# Level 0
## Prompt
A single basic block defines and uses 4 variables at integer positions. Registers available: 1.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v0 def at 0
v1 def at 1
v3 def at 2
v2 def at 3
v1 use at 5
v1 use at 6
v0 use at 8
v2 use at 9
v2 use at 10
v3 use at 11
v1 use at 12
v0 use at 13
v2 use at 14
v3 use at 15
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
S_0_S_S

## Prompt
A single basic block defines and uses 4 variables at integer positions. Registers available: 1.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v2 def at 1
v2 use at 2
v3 def at 3
v1 def at 5
v0 def at 6
v0 use at 7
v3 use at 8
v1 use at 9
v2 use at 11
v1 use at 12
v3 use at 14
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
0_S_S_S

# Level 2
## Prompt
A single basic block defines and uses 5 variables at integer positions. Registers available: 1.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v2 def at 0
v0 def at 1
v4 def at 2
v4 use at 4
v1 def at 7
v2 use at 9
v0 use at 10
v3 def at 11
v4 use at 13
v2 use at 14
v1 use at 16
v0 use at 17
v2 use at 19
v1 use at 20
v3 use at 21
v3 use at 22
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
S_S_S_S_0

## Prompt
A single basic block defines and uses 5 variables at integer positions. Registers available: 1.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v0 def at 0
v4 def at 1
v4 use at 3
v3 def at 4
v4 use at 5
v1 def at 9
v1 use at 11
v0 use at 12
v3 use at 13
v2 def at 17
v0 use at 19
v2 use at 20
v1 use at 21
v2 use at 22
v3 use at 23
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
S_0_S_S_0

# Level 5
## Prompt
A single basic block defines and uses 6 variables at integer positions. Registers available: 2.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v0 def at 2
v5 def at 3
v1 def at 4
v5 use at 5
v4 def at 7
v1 use at 8
v2 def at 10
v4 use at 12
v0 use at 14
v5 use at 16
v3 def at 17
v3 use at 20
v1 use at 22
v4 use at 32
v3 use at 33
v2 use at 35
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
0_S_S_0_S_1

## Prompt
A single basic block defines and uses 6 variables at integer positions. Registers available: 2.
Lines list 'variable op position'. A def starts a variable's live interval; its live range ends at its last use.
v0 def at 0
v4 def at 2
v2 def at 4
v5 def at 5
v1 def at 7
v3 def at 8
v0 use at 10
v1 use at 11
v4 use at 13
v1 use at 16
v5 use at 18
v2 use at 19
v5 use at 21
v3 use at 23
v2 use at 24
v0 use at 29
v3 use at 34
Run linear-scan allocation: process positions in increasing order; on a variable's start first free the registers of intervals that already ended (their end < current position); if a register is free assign the variable's start to it, else evict the currently-live variable whose end is farthest and spill it (an interval evicted once stays spilled). A variable that would evict a variable with a farther end instead spills itself.
For each v0..vN-1 give the register it was assigned at its start, or 'S' for spilled, joined by underscores. Example: '0_S_1_0'.
## Answer
S_0_S_S_1_S

