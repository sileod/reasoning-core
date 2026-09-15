## Level 0
### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 2 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 170
Round keys (in order): [43, 197]
S-box (index 0..15): [1, 11, 9, 12, 3, 7, 13, 2, 15, 6, 10, 0, 4, 5, 14, 8]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [2, 7, 1, 6, 0, 3, 4, 5]
What is the ciphertext after all 2 rounds? Answer one integer.
### Answer
98

### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 2 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 57
Round keys (in order): [6, 64]
S-box (index 0..15): [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [3, 1, 2, 4, 6, 5, 0, 7]
What is the ciphertext after all 2 rounds? Answer one integer.
### Answer
147

## Level 2
### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 4 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 221
Round keys (in order): [142, 30, 217, 101]
S-box (index 0..15): [1, 11, 9, 12, 3, 7, 13, 2, 15, 6, 10, 0, 4, 5, 14, 8]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [0, 2, 1, 4, 7, 5, 3, 6]
What is the ciphertext after all 4 rounds? Answer one integer.
### Answer
9

### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 4 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 26
Round keys (in order): [235, 137, 103, 203]
S-box (index 0..15): [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [1, 7, 5, 2, 6, 0, 4, 3]
What is the ciphertext after all 4 rounds? Answer one integer.
### Answer
45

## Level 5
### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 7 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 110
Round keys (in order): [211, 249, 8, 1, 172, 227, 136]
S-box (index 0..15): [1, 11, 9, 12, 3, 7, 13, 2, 15, 6, 10, 0, 4, 5, 14, 8]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [7, 0, 1, 2, 5, 4, 6, 3]
What is the ciphertext after all 7 rounds? Answer one integer.
### Answer
42

### Prompt
We encrypt an 8-bit block with a toy subset-permutation network for 7 rounds. Each round: XOR the block with the round key, then split into high and low 4-bit nibbles, pass each through the s-box, reassemble, then permute the 8 bit positions by the permutation.
Plaintext: 134
Round keys (in order): [166, 120, 120, 51, 77, 36, 89]
S-box (index 0..15): [1, 11, 9, 12, 3, 7, 13, 2, 15, 6, 10, 0, 4, 5, 14, 8]
Permutation (destination position i receives source bit perm[i]); list perm where outbit[i] = inbit[perm[i]]: [0, 1, 2, 5, 4, 7, 3, 6]
What is the ciphertext after all 7 rounds? Answer one integer.
### Answer
85

