# Level 0
## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

L0: x = x + 8
L1: z = b
L2: z = z + 2

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L0, L1

## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

L0: z = z + 7
L1: x = b
L2: x = x + 1

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L0, L1

# Level 2
## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

while (c3):
  L0: x = x + 8
  L1: z = 5
L2: y = y + 9
if (c4):
  if (c4):
    L3: y = y + 4
  else:
    L4: x = x + 8
else:
  while (c4):
    L5: x = 0
L6: x = c
L7: y = 8

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L1, L2, L3, L6

## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

if (c4):
  L0: y = 7
else:
  L1: z = 7
L2: x = x + 3
L3: y = 6
L4: z = z + 6
L5: x = 6

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L2, L3, L4

# Level 5
## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

while (c2):
  L0: x = 6
L1: y = 6
L2: x = x + 7
if (c2):
  L3: z = z + 3
  if (c3):
    L4: x = x + 3
    L5: x = x + 2
  else:
    L6: y = y + 8
    L7: x = b
  L8: z = 9
else:
  if (c1):
    L9: y = y + 9
  else:
    L10: y = 4
  L11: y = b
L12: x = 0
if (c1):
  L13: y = c
  while (c4):
    L14: x = 0
    while (c3):
      L15: y = c
else:
  if (c4):
    L16: z = z + 6
  else:
    L17: x = x + 4
    L18: x = c
  L19: z = 7
  while (c1):
    L20: z = z + 6
    L21: z = 1
L22: y = 2
L23: y = y + 2

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L8, L12, L14, L18, L19, L21, L22

## Example
**Prompt:**

Below is a small imperative program. Each assignment statement carries a unique label (L0, L1, ...).

L0: z = z + 4
L1: x = 7
L2: x = x + 8
L3: x = x + 9
if (c2):
  L4: x = x + 9
else:
  L5: y = b
  while (c4):
    L6: z = z + 2
  L7: x = 5
L8: x = x + 4
while (c4):
  L9: x = x + 2
  L10: x = c
while (c1):
  L11: x = 0
  L12: x = x + 1
  L13: x = x + 9

A labeled assignment's definition reaches the end of the program if there is a path through the control flow (following branches and the body of while-loops, possibly zero or more times) from that assignment to the final point on which the assigned variable is not overwritten by another assignment. List every label whose definition reaches the end of the program.

Answer format: the labels in ascending order, comma-separated with no spaces, for example L0,L1,L4. If no assignment reaches the end, write exactly: none

**Answer:**

L0, L5, L6, L8, L10, L13
