# Samples for P005v1: leaky_evidence_commitment

## Assigned design choice

Present evidence as a stream of +1/-1 signs with leakage rate and time-varying thresholds; answer the final choice and step count when bounds are first hit.

## Summary

Accumulate signed evidence with stated leakage, starting bias, and absorbing decision bounds; vary interruptions, changing bounds, and opposing evidence bursts; answer the committed choice and stopping time.

# Level 0

## Example 1

A signed-evidence accumulator starts at 1. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -3 (lower) and 3 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
-1 -1 +1 -1 -1 +1 +1 -1 -1 +1 -1 -1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `lower 12`

## Example 2

A signed-evidence accumulator starts at 1. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -3 (lower) and 3 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
-1 -1 -1 +1 +1 +1 -1 +1 -1 +1 +1 -1 -1 +1 +1 +1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `upper 16`

# Level 2

## Example 1

A signed-evidence accumulator starts at 3. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -5 (lower) and 5 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
-1 -1 -1 +1 -1 +1 -1 +1 -1 +1 +1 +1 -1 +1 -1 +1 +1 -1 -1 -1 +1 -1 +1 -1 -1 +1 +1 -1 -1 -1 -1 -1 -1 -1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `lower 34`

## Example 2

A signed-evidence accumulator starts at 3. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -5 (lower) and 5 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
-1 +1 -1 +1 -1 -1 +1 +1 +1 +1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `upper 10`

# Level 5

## Example 1

A signed-evidence accumulator starts at 3. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -8 (lower) and 8 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
At step 9 the upper bound widens further up by 2 (becomes 10).
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
-1 +1 +1 -1 +1 -1 -1 -1 -1 -1 +1 -1 -1 +1 -1 -1 -1 -1 -1 -1 +1 +1 +1 +1 +1 +1 -1 -1 +1 +1 +1 -1 +1 +1 -1 -1 +1 -1 +1 +1 -1 -1 +1 -1 +1 -1 +1 -1 -1 +1 +1 +1 +1 +1 -1 +1 -1 -1 -1 -1 +1 -1 -1 -1 +1 -1 -1 +1 +1 +1 +1 +1 -1 +1 +1 -1 +1 -1 -1 -1 +1 -1 -1 -1 -1 -1 -1 +1 +1 -1 -1 -1 -1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `lower 93`

## Example 2

A signed-evidence accumulator starts at 3. It reads signs one at a time, each +1 or -1. Before every sign, the value shrinks by 4% of its distance from zero toward zero (rounded to the nearest integer), then the sign is added. The initial decision bounds are -8 (lower) and 8 (upper): the moment the value becomes at or below the lower bound it commits 'lower', and at or above the upper bound it commits 'upper', and reading stops immediately.
At step 7 the upper bound widens further up by 1 (becomes 9).
The stated leak, starting value, and (possibly widened) decision bounds apply while reading this sign stream:
+1 -1 +1 +1 -1 -1 +1 -1 -1 +1 -1 -1 -1 +1 +1 +1 +1 -1 -1 -1 -1 -1 +1 -1 +1 +1 +1 -1 +1 -1 +1 -1 +1 +1 -1 -1 -1 -1 -1 +1 +1 -1 -1 -1 -1 -1 +1 -1 -1 -1 -1
What is the committed bound ('upper' or 'lower') and the step number at which it committed? Answer with the bound word and the step count, space-separated, e.g. 'upper 7'.


Answer: `lower 51`
