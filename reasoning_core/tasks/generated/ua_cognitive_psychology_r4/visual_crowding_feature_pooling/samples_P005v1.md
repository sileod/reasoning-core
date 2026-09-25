## Level 0

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature green, pooling weight 0.07
position 1: feature white, pooling weight 0.41
position 2: feature red, pooling weight 0.67
Target at position 2. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
green

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature green, pooling weight 0.02
position 1: feature white, pooling weight 0.78
position 2: feature red, pooling weight 0.0
Target at position 1. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
white

## Level 2

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature black, pooling weight 0.13
position 1: feature red, pooling weight 0.15
position 2: feature blue, pooling weight 0.56
position 3: feature white, pooling weight 1.96
position 4: feature white, pooling weight 0.45
Target at position 3. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
black

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature green, pooling weight 0.0
position 1: feature white, pooling weight 1.4
position 2: feature black, pooling weight 0.46
position 3: feature red, pooling weight 0.29
position 4: feature black, pooling weight 0.0
Target at position 1. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
black

## Level 5

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature black, pooling weight 0.0
position 1: feature black, pooling weight 1.76
position 2: feature red, pooling weight 0.0
position 3: feature green, pooling weight 0.0
position 4: feature green, pooling weight 0.0
position 5: feature blue, pooling weight 0.0
position 6: feature green, pooling weight 0.0
position 7: feature black, pooling weight 0.01
Target at position 1. A segmentation barrier separates positions 0..0 from the rest; only the target's partition is pooled, items outside it get weight 0. Two successive pooling stages are applied: at each stage every item's weight is divided by (1 + half its distance in positions from the target), attenuating farther flankers. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
black

Prompt:
Feature degrees: red=0, green=45, blue=90, black=135, white=180. Features pool as the weighted mean of the degrees of pooled items, using each item's pooling weight; tie rounds to the lower degree. Pooled items are those in the target's pooling neighborhood (all items unless a barrier narrows it).
Items:
position 0: feature blue, pooling weight 0.17
position 1: feature black, pooling weight 0.25
position 2: feature red, pooling weight 1.13
position 3: feature blue, pooling weight 0.3
position 4: feature white, pooling weight 0.02
position 5: feature white, pooling weight 0.06
position 6: feature black, pooling weight 0.04
position 7: feature black, pooling weight 0.04
Target at position 2. Two successive pooling stages are applied: at each stage every item's weight is divided by (1 + half its distance in positions from the target), attenuating farther flankers. Report the perceived feature (the nearest symbol to the pooled mean) as one symbol from ['red', 'green', 'blue', 'black', 'white'].

Answer:
green
