## Level 0

### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 8 unit(s), mass 1, sitting on the ground.
Block 2: width 10 unit(s), mass 3, center shifted +2 unit(s) from the center of the block directly below it.
Block 3: width 6 unit(s), mass 2, center shifted -1 unit(s) from the center of the block directly below it.
Block 4: width 10 unit(s), mass 1, center shifted -1 unit(s) from the center of the block directly below it.
Block 5: width 8 unit(s), mass 2, center shifted -1 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Remove block 2 entirely. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** none 4


### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 6 unit(s), mass 3, sitting on the ground.
Block 2: width 10 unit(s), mass 2, center shifted +0 unit(s) from the center of the block directly below it.
Block 3: width 10 unit(s), mass 3, center shifted -2 unit(s) from the center of the block directly below it.
Block 4: width 6 unit(s), mass 1, center shifted +2 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Nudge block 2: shift its center by +1 unit(s) horizontally. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** none 4


## Level 2

### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 8 unit(s), mass 3, sitting on the ground.
Block 2: width 8 unit(s), mass 2, center shifted -1 unit(s) from the center of the block directly below it.
Block 3: width 8 unit(s), mass 1, center shifted +0 unit(s) from the center of the block directly below it.
Block 4: width 6 unit(s), mass 5, center shifted +0 unit(s) from the center of the block directly below it.
Block 5: width 10 unit(s), mass 4, center shifted +1 unit(s) from the center of the block directly below it.
Block 6: width 12 unit(s), mass 3, center shifted +0 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Nudge block 1: shift its center by +4 unit(s) horizontally. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** 2,3,4,5,6 1


### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 12 unit(s), mass 1, sitting on the ground.
Block 2: width 10 unit(s), mass 2, center shifted +1 unit(s) from the center of the block directly below it.
Block 3: width 6 unit(s), mass 4, center shifted -3 unit(s) from the center of the block directly below it.
Block 4: width 12 unit(s), mass 4, center shifted +1 unit(s) from the center of the block directly below it.
Block 5: width 10 unit(s), mass 2, center shifted +4 unit(s) from the center of the block directly below it.
Block 6: width 6 unit(s), mass 1, center shifted +0 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Remove block 1 entirely. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** none 5


## Level 5

### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 14 unit(s), mass 6, sitting on the ground.
Block 2: width 14 unit(s), mass 3, center shifted +3 unit(s) from the center of the block directly below it.
Block 3: width 14 unit(s), mass 6, center shifted -5 unit(s) from the center of the block directly below it.
Block 4: width 12 unit(s), mass 6, center shifted +4 unit(s) from the center of the block directly below it.
Block 5: width 12 unit(s), mass 2, center shifted +4 unit(s) from the center of the block directly below it.
Block 6: width 10 unit(s), mass 6, center shifted -2 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Remove block 6 entirely. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** none 5


### Prompt

A tower of axis-aligned blocks rests on a flat, infinitely wide ground. A block occupies the horizontal interval centered on its center with half-width equal to half its width, and the ground supports the lowest block unconditionally.
Block 1: width 10 unit(s), mass 6, sitting on the ground.
Block 2: width 14 unit(s), mass 1, center shifted -6 unit(s) from the center of the block directly below it.
Block 3: width 14 unit(s), mass 5, center shifted +2 unit(s) from the center of the block directly below it.
Block 4: width 10 unit(s), mass 8, center shifted +0 unit(s) from the center of the block directly below it.
Block 5: width 12 unit(s), mass 7, center shifted -2 unit(s) from the center of the block directly below it.
Block 6: width 14 unit(s), mass 4, center shifted +0 unit(s) from the center of the block directly below it.
Block 7: width 14 unit(s), mass 3, center shifted +1 unit(s) from the center of the block directly below it.
The middle/upper blocks must each support the center of mass of every block above them: the mass-weighted average center of the blocks strictly above a block must lie strictly inside that block's footprint. Nudge block 4: shift its center by +7 unit(s) horizontally. After the change, recompute the support at every interface below and above the change, from the bottom up; the lowest interface whose supported center of mass falls outside its footprint causes that block and every block above it to topple off the tower. Blocks that topple are removed; the others stay.
Answer which block IDs (numbered 1 for the lowest block) topple, as a sorted comma-separated list with no spaces, or the single word 'none' if no block topples, followed by a space and the height (number of blocks) of the surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 topple and 3 blocks remain standing.


**Answer:** 5,6,7 4


