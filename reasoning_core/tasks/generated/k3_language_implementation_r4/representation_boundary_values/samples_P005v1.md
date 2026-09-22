## Level 0
### Prompt
An 8-bit value starts as the byte 19. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: divide by 8 as an unsigned byte (division by zero traps).
2: use the byte as an enum tag; valid tags are [54, 235] (others trap).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
2u, trap

### Prompt
An 8-bit value starts as the byte 223. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: add -1 as a signed byte (wrap within -128..127).
2: use the byte as an index into an array of size 156 (out of range traps).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
-34s, trap

## Level 2
### Prompt
An 8-bit value starts as the byte 11. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: add 49 as an unsigned byte (wrap mod 256).
2: divide by 4 as an unsigned byte (division by zero traps).
3: treat the byte as a tagged union: the top 6 bits are the tag, the remaining bits are the payload. Valid variants are {0: 'signed', 1: 'unsigned', 2: 'signed', 3: 'unsigned', 4: 'unsigned'} (invalid tag traps, payload read as the variant's type).
4: divide by 0 as an unsigned byte (division by zero traps).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
60u, 15u, 3u, trap

### Prompt
An 8-bit value starts as the byte 10. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: multiply by 225 as an unsigned byte (wrap mod 256).
2: reinterpret the byte as signed.
3: multiply by 13 as an unsigned byte (wrap mod 256).
4: multiply by 22 as an unsigned byte (wrap mod 256).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
202u, -54s, 66u, 172u

## Level 5
### Prompt
An 8-bit value starts as the byte 98. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: reinterpret the byte as signed.
2: use the byte as an index into an array of size 45 (out of range traps).
3: add 179 as an unsigned byte (wrap mod 256).
4: treat the byte as a tagged union: the top 4 bits are the tag, the remaining bits are the payload. Valid variants are {0: 'unsigned', 1: 'unsigned', 2: 'unsigned', 3: 'signed', 4: 'signed', 5: 'unsigned'} (invalid tag traps, payload read as the variant's type).
5: multiply by 144 as an unsigned byte (wrap mod 256).
6: add -29 as a signed byte (wrap within -128..127).
7: treat the byte as a tagged union: the top 5 bits are the tag, the remaining bits are the payload. Valid variants are {0: 'signed', 1: 'signed', 2: 'signed', 3: 'unsigned'} (invalid tag traps, payload read as the variant's type).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
98s, trap

### Prompt
An 8-bit value starts as the byte 71. A sequence of checkpoints processes it left to right; unsigned arithmetic wraps mod 256 and signed arithmetic wraps within -128..127. A checkpoint traps if it divides by zero, indexes out of range, uses an invalid enum tag, or selects an invalid tagged-union variant; a trap ends the sequence at that checkpoint.
Checkpoints:
1: add 23 as a signed byte (wrap within -128..127).
2: multiply by 8 as an unsigned byte (wrap mod 256).
3: add 28 as a signed byte (wrap within -128..127).
4: add 9 as an unsigned byte (wrap mod 256).
5: reinterpret the byte as signed.
6: reinterpret the byte as unsigned.
7: divide by 0 as an unsigned byte (division by zero traps).

List each checkpoint's result in order as a comma-separated list: unsigned values as an integer followed by 'u', signed values as an integer followed by 's', and a trapped checkpoint as the word 'trap'. Example format: '42u, -5s, trap'. Output only the list.
### Answer
94s, 240u, 12s, 21u, 21s, 21u, trap

