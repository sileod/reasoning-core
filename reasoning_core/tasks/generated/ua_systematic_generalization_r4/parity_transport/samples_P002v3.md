# Level 0

## Example 1

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['B', 'C', 'F', 'D'], meaning the substituent at slot 0 is B, at slot 1 is C, at slot 2 is F, at slot 3 is D (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['B', 'C', 'D', 'F']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. swap D C
  2. swap C B

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

S

## Example 2

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['A', 'B', 'F', 'D'], meaning the substituent at slot 0 is A, at slot 1 is B, at slot 2 is F, at slot 3 is D (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['A', 'B', 'D', 'F']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. swap A B
  2. rotate F B D

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

R

# Level 2

## Example 1

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['F', 'C', 'D', 'E'], meaning the substituent at slot 0 is F, at slot 1 is C, at slot 2 is D, at slot 3 is E (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['C', 'D', 'E', 'F']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. invert
  2. rotate E F C
  3. swap C F
  4. swap E F
  5. rotate F E D
  6. rotate D F C

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

R

## Example 2

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['E', 'D', 'H', 'C'], meaning the substituent at slot 0 is E, at slot 1 is D, at slot 2 is H, at slot 3 is C (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['C', 'D', 'E', 'H']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. rotate E D H
  2. rotate C H E
  3. swap E H
  4. swap C D
  5. invert
  6. swap C D

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

R

# Level 5

## Example 1

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['E', 'A', 'H', 'G'], meaning the substituent at slot 0 is E, at slot 1 is A, at slot 2 is H, at slot 3 is G (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['A', 'E', 'G', 'H']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. invert
  2. rotate G A E
  3. invert
  4. rotate G H E
  5. rotate G H E
  6. rotate H A E
  7. invert
  8. rotate E G A
  9. invert
  10. swap E A
  11. invert
  12. invert

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

S

## Example 2

Prompt:

A tetrahedral chiral center bears four distinct substituents. Its current spatial arrangement is given as the ordered neighbor list ['D', 'H', 'G', 'B'], meaning the substituent at slot 0 is D, at slot 1 is H, at slot 2 is G, at slot 3 is B (slots in clockwise order viewed from above). Taking the reference order as the alphabetical order of the four substituents (['B', 'D', 'G', 'H']), the center's chirality is R when its neighbor list is an even permutation of that reference order and S when it is an odd one.

The following operations are then applied to the center in order:
  1. swap B G
  2. invert
  3. swap B H
  4. rotate D H B
  5. rotate B D H
  6. rotate D H B
  7. rotate D H G
  8. swap H B
  9. rotate B D G
  10. rotate G D B
  11. invert
  12. invert

Here swap X Y exchanges the two listed neighboring substituents (this flips handedness), rotate X Y Z cyclically moves X to Y's slot, Y to Z's slot, and Z to X's slot (this preserves handedness), and invert reflects the center in a mirror plane (this flips handedness).

Give the chirality of the center after all operations as a single letter.

Answer:

R
