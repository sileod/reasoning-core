# Samples: instruction_priority (P001v1)

## Level 0

### Example 1

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [medium (3)] power down the generator.
    [lowest (1)] do not power down the generator.
    [medium (3)] do not raise the flag.
    Is the operator required to power down the generator?

Answer: yes

### Example 2

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [medium (3)] power down the generator.
    [lowest (1)] do not power down the generator.
    [low (2)] do not open the doors.
    Must the operator power down the generator?

Answer: yes

## Level 2

### Example 1

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [lowest (1)] release the valves.
    [high (4)] do not release the valves.
    [low (2)] do not open the doors.
    [low (2)] do not open the doors.
    [lowest (1)] do not open the doors.
    Should the operator release the valves?

Answer: no

### Example 2

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [high (4)] move the crate to the north.
    [medium (3)] do not move the crate to the north.
    [lowest (1)] open the doors.
    [low (2)] return to base.
    [lowest (1)] open the doors.
    Must the operator move the crate to the north?

Answer: yes

## Level 5

### Example 1

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [highest (5)] power down the generator.
    [medium (3)] do not power down the generator.
    [low (2)] do not raise the flag.
    [high (4)] raise the flag.
    [medium (3)] do not raise the flag.
    [medium (3)] raise the flag.
    [medium (3)] do not raise the flag.
    [highest (5)] raise the flag.
    Should the operator power down the generator?

Answer: yes

### Example 2

Prompt:

    Answer this question with exactly yes or no.
    Each instruction carries a numeric rank 1 (lowest) to 5 (highest). Obey every instruction, except that when two instructions directly contradict, follow only the higher-ranked one. A lower-ranked instruction still applies everywhere it does not directly contradict a higher one.
    [highest (5)] raise the flag.
    [high (4)] do not raise the flag.
    [high (4)] do not move the crate to the north.
    [low (2)] do not move the crate to the north.
    [lowest (1)] return to base.
    [low (2)] do not move the crate to the north.
    [high (4)] move the crate to the north.
    [lowest (1)] move the crate to the north.
    Must the operator raise the flag?

Answer: yes
