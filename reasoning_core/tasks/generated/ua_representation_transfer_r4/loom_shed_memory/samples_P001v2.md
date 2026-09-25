## Level 0

### Prompt

A loom has 5 warp threads. warp 1 -> shaft 1, warp 2 -> shaft 0, warp 3 -> shaft 2, warp 4 -> shaft 2, warp 5 -> shaft 1. There are 3 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 1,2,3; pedal B lifts shafts 1,2,3; pedal C lifts shafts 2. The weaver starts with no shaft lifted. pick 1: no change (shed holds); pick 2: no change (shed holds); pick 3: no change (shed holds); pick 4: no change (shed holds); pick 5: press pedal B; pick 6: release shafts 3. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses every pick in the order listed, from pick 1 through pick 6. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 2. Give the answer as a single integer.


### Answer

5


### Prompt

A loom has 5 warp threads. warp 1 -> shaft 0, warp 2 -> shaft 0, warp 3 -> shaft 2, warp 4 -> shaft 1, warp 5 -> shaft 1. There are 3 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 1,3; pedal B lifts shafts 1,2,3; pedal C lifts shafts 2,3. The weaver starts with no shaft lifted. pick 1: press pedal C; pick 2: press pedal B; pick 3: release shafts 1,2,3; pick 4: press pedal B; pick 5: press pedal B; pick 6: release shafts 1,2,3. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses every pick in the order listed, from pick 1 through pick 6. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 2. Give the answer as a single integer.


### Answer

0


## Level 2

### Prompt

A loom has 7 warp threads. warp 1 -> shaft 0, warp 2 -> shaft 3, warp 3 -> shaft 1, warp 4 -> shaft 2, warp 5 -> shaft 1, warp 6 -> shaft 2, warp 7 -> shaft 4. There are 5 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 1,2,3,5; pedal B lifts shafts 5; pedal C lifts shafts 1,2,3,4,5; pedal D lifts shafts 1,2,3,5; pedal E lifts shafts 1,2,3,5. The weaver starts with no shaft lifted. pick 1: press pedal D; pick 2: press pedal C; pick 3: press pedal C; pick 4: release shafts 1,2,3,4; pick 5: no change (shed holds); pick 6: press pedal C; pick 7: press pedal D; pick 8: press pedal D; pick 9: press pedal C; pick 10: press pedal D. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses every pick in the order listed, from pick 1 through pick 10. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 4. Give the answer as a single integer.


### Answer

0


### Prompt

A loom has 7 warp threads. warp 1 -> shaft 0, warp 2 -> shaft 3, warp 3 -> shaft 0, warp 4 -> shaft 2, warp 5 -> shaft 3, warp 6 -> shaft 4, warp 7 -> shaft 1. There are 5 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 1,5; pedal B lifts shafts 4,5; pedal C lifts shafts 4,5; pedal D lifts shafts 2,4; pedal E lifts shafts 3,4. The weaver starts with no shaft lifted. pick 1: press pedal A; pick 2: press pedal D; pick 3: no change (shed holds); pick 4: release shafts 1,2,4,5; pick 5: no change (shed holds); pick 6: press pedal E; pick 7: press pedal B; pick 8: release shafts 5; pick 9: no change (shed holds); pick 10: release shafts 3,4. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses picks 1 through 6 in order, then it reverses and crosses picks 10 back down to 7, then continues to the end. Use this order for measuring runs. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 4. Give the answer as a single integer.


### Answer

5


## Level 5

### Prompt

A loom has 10 warp threads. warp 1 -> shaft 3, warp 2 -> shaft 6, warp 3 -> shaft 5, warp 4 -> shaft 0, warp 5 -> shaft 4, warp 6 -> shaft 3, warp 7 -> shaft 0, warp 8 -> shaft 7, warp 9 -> shaft 1, warp 10 -> shaft 2. There are 8 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 1; pedal B lifts shafts 3,5; pedal C lifts shafts 2,5,8; pedal D lifts shafts 1,4,5,6,7,8; pedal E lifts shafts 1,2,3,4,5,6,7,8; pedal F lifts shafts 2,3,6,7; pedal G lifts shafts 8; pedal H lifts shafts 1,2,3,4,5,6,7,8. The weaver starts with no shaft lifted. pick 1: press pedal C; pick 2: press pedal F; pick 3: press pedal B; pick 4: press pedal E; pick 5: press pedal E; pick 6: release shafts 1,3,4,6; pick 7: press pedal A; pick 8: press pedal A; pick 9: press pedal B; pick 10: no change (shed holds); pick 11: no change (shed holds); pick 12: no change (shed holds); pick 13: no change (shed holds); pick 14: no change (shed holds); pick 15: no change (shed holds); pick 16: release shafts 1,2,3,5,7,8. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses every pick in the order listed, from pick 1 through pick 16. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 7. Give the answer as a single integer.


### Answer

3


### Prompt

A loom has 10 warp threads. warp 1 -> shaft 5, warp 2 -> shaft 0, warp 3 -> shaft 7, warp 4 -> shaft 1, warp 5 -> shaft 3, warp 6 -> shaft 4, warp 7 -> shaft 5, warp 8 -> shaft 1, warp 9 -> shaft 2, warp 10 -> shaft 6. There are 8 pedals; pressing a pedal lifts its shafts and that lift latches, meaning it stays up until explicitly released. pedal A lifts shafts 2,6,7; pedal B lifts shafts 3,4,6,7,8; pedal C lifts shafts 1,6; pedal D lifts shafts 4,7; pedal E lifts shafts 1,2,3,4,5,6,7,8; pedal F lifts shafts 1,2,5,6,7; pedal G lifts shafts 1,2,4,5,7,8; pedal H lifts shafts 1,3,4,7,8. The weaver starts with no shaft lifted. pick 1: press pedal H; pick 2: no change (shed holds); pick 3: release shafts 1,3,4,7,8; pick 4: press pedal B; pick 5: no change (shed holds); pick 6: press pedal A; pick 7: no change (shed holds); pick 8: no change (shed holds); pick 9: release shafts 2,4,7,8; pick 10: release shafts 3,6; pick 11: press pedal A; pick 12: press pedal D; pick 13: release shafts 2; pick 14: release shafts 6,7; pick 15: no change (shed holds); pick 16: release shafts 4. When the shed is formed the shuttle lays the weft over the warps whose shaft is NOT lifted (those warps stay down) and under the lifted warps. The shuttle crosses picks 1 through 12 in order, then it reverses and crosses picks 14 back down to 13, then continues to the end. Use this order for measuring runs. A float on a warp is a run of consecutive crossings (in that crossing order) where the warp stays down, i.e. the weft lies over it. Count how many warp-floats have length strictly greater than 7. Give the answer as a single integer.


### Answer

3

