# Level 0
## Example 1
Prompt:
Using the Misra-Gries majority algorithm with 2 counters, process the stream of symbols from alphabet [0, 1, 2, 3]: 0 3 2 2 3 3 3 1 2 1 3 1 0 2 3 1 2 2 2 1 3 2 2 0. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
2:3

## Example 2
Prompt:
Using the Misra-Gries majority algorithm with 2 counters, process the stream of symbols from alphabet [0, 1, 2, 3]: 3 0 3 1 0 0 0 3 1 0 0 0 0 2 3 3 0 2 2 1 1 1 0 1. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
0:5,1:4

# Level 2
## Example 1
Prompt:
Using the Misra-Gries majority algorithm with 2 counters, process the stream of symbols from alphabet [0, 1, 2, 3, 4, 5]: 3 2 4 3 2 0 5 1 2 5 5 0 0 0 0 1 1 0 5 1 1 5 4 3 2 4 4 2 2 0 5 0 5 2 3 1 0 5 3 3. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
3:1

## Example 2
Prompt:
Using the Misra-Gries majority algorithm with 2 counters, process the stream of symbols from alphabet [0, 1, 2, 3, 4, 5]: 1 3 2 3 4 1 2 1 5 3 5 5 3 3 4 3 0 4 3 4 5 4 2 3 1 4 1 3 4 0 4 2 3 5 0 0 0 0 2 5. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
0:3,5:1

# Level 5
## Example 1
Prompt:
Using the Misra-Gries majority algorithm with 3 counters, process the stream of symbols from alphabet [0, 1, 2, 3, 4, 5, 6, 7, 8]: 1 3 8 5 2 5 5 0 4 7 6 3 0 1 5 7 8 1 8 5 7 8 1 1 1 3 8 8 3 1 4 2 8 7 4 1 5 0 8 1 5 0 3 3 7 6 1 0 4 0 1 6 1 6 0 5 4 0 8 4 4 1 0 7. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
0:1,4:2,7:1

## Example 2
Prompt:
Using the Misra-Gries majority algorithm with 3 counters, process the stream of symbols from alphabet [0, 1, 2, 3, 4, 5, 6, 7, 8]: 6 8 7 0 3 8 5 4 4 1 3 7 5 2 4 3 2 4 7 5 5 1 5 8 3 8 6 1 6 1 4 0 7 2 5 2 7 6 5 3 6 7 3 4 8 8 6 6 7 3 5 4 6 7 5 3 0 1 6 2 8 7 7 3. On a hit increment the counter; if the symbol has no counter and a slot is free, occupy it with count 1; otherwise decrement every counter by 1 and drop any that reach 0. Write the final counter map in sorted-symbol order as comma-separated key:value pairs (for example '0:2,3:1'); if every counter is empty write 'none'.
Answer:
3:1,7:2,8:1

