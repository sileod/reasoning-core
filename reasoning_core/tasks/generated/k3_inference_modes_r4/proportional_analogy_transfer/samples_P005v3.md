# samples_P005v3 - proportional_analogy_transfer

## Level 0

### Example 1

**Prompt:**

My tuple source A = 0 2 1 -1 0 became B = -1 1 0 -2 -1 after applying exactly one of the operations [absolute, decrement, increment, negate, reverse, rotl, rotr, square]. Which operation was applied to A to produce B? Answer with that operation's name from the list.

**Answer:**

decrement

### Example 2

**Prompt:**

My grid source A = 2 2 1 2 | 1 0 2 1 | 2 2 2 1 | 2 0 2 0 became B = 2 0 2 0 | 2 2 2 1 | 1 0 2 1 | 2 2 1 2 after applying exactly one of the operations [hflip, rot180, rot270, rot90, transpose, vflip]. Which operation was applied to A to produce B? Answer with that operation's name from the list.

**Answer:**

vflip

## Level 2

### Example 1

**Prompt:**

My tuple source A = -2 0 2 -2 -2 -1 1 became B = -3 -1 1 -3 -3 -2 0 after applying exactly one of the operations [absolute, decrement, increment, negate, reverse, rotl, rotr, square]. Which operation was applied to A to produce B? Answer with that operation's name from the list.

**Answer:**

decrement

### Example 2

**Prompt:**

Complete this proportional analogy. The transformation mapping A = 'afejmkj' to B = 'jafejmk' is exactly one of the operations [double, drop_first, reverse, rotl, rotr, sort, swap_ends, upper]. Apply that same operation to C = 'klhjble'. What is the missing term C transformed so that A:B :: C:? ? Give the result as a lowercase or uppercase alphabetic string.

**Answer:**

eklhjbl

## Level 5

### Example 1

**Prompt:**

Complete this proportional analogy. The transformation mapping A = 2 -2 -1 0 2 2 1 2 2 1 to B = 2 2 1 0 2 2 1 2 2 1 is exactly one of the operations [absolute, decrement, increment, negate, reverse, rotl, rotr, square]. Apply that same operation to C = 1 2 0 -2 1 2 -2 -2 -1 1. What is the missing term C transformed so that A:B :: C:? ? Give the result as a space-separated list of integers.

**Answer:**

1   2   0   2   1   2   2   2   1   1

### Example 2

**Prompt:**

Complete this proportional analogy. The transformation mapping A = 'gkhdfdhhmmm' to B = 'khdfdhhmmmg' is exactly one of the operations [double, drop_first, reverse, rotl, rotr, sort, swap_ends, upper]. Apply that same operation to C = 'fejeijkhmfg'. What is the missing term C transformed so that A:B :: C:? ? Give the result as a lowercase or uppercase alphabetic string.

**Answer:**

ejeijkhmfgf
