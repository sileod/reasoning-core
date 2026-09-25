## Level 0
### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 0, no border
  Box 1: margin 5, has a border
    Box 2: margin 6, has a border
    Box 3: margin 0, no border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
5,5

### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 3, no border
  Box 1: margin 4, no border
    Box 2: margin 0, no border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
4,4

## Level 2
### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 4, no border
  Box 1: margin 0, no border
    Box 2: margin 8, has a border
      Box 3: margin 2, no border
    Box 4: margin -3, no border
      Box 5: margin -4, has a border
  Box 6: margin 10, no border
    Box 7: margin 10, no border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
8,10

### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 6, no border
  Box 1: margin 0, no border
    Box 2: margin 4, no border
      Box 3: margin -5, no border
      Box 4: margin 6, no border
  Box 5: margin -5, has a border
    Box 6: margin -4, no border
      Box 7: margin 0, no border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
1,1

## Level 5
### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 12, no border
  Box 1: margin 9, no border
    Box 2: margin 14, no border
      Box 3: margin -1, has a border
        Box 4: margin -7, has a border
      Box 5: margin 0, no border
        Box 6: margin 10, has a border
        Box 7: margin -2, has a border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
13,12

### Prompt
The following lines describe vertically nested block boxes, indented to show nesting. The first box is the outermost; a box's children sit inside it and are indented one extra level.

Box 0: margin 0, no border
  Box 1: margin 7, no border
    Box 2: margin 7, has a border
      Box 3: margin 6, no border
        Box 4: margin -7, no border
  Box 5: margin 10, no border
    Box 6: margin -8, no border
      Box 7: margin -5, has a border
        Box 8: margin 4, has a border
      Box 9: margin -5, no border
        Box 10: margin 7, has a border

In normal block flow, adjoining vertical margins collapse into a single margin equal to the maximum positive margin plus the minimum negative margin (negative-only runs collapse to the most negative value). A box marked "no border" is transparent and empty, so its own margin sits directly against the margin of its first (for the top run) or last (for the bottom run) child and collapses through to it. A box marked "has a border" instead stops the collapse right at itself: its own margin is counted, but the run does not reach that box's children.

The collapsed outer TOP margin of the entire nested box is the collapse of the adjoining top run starting at the outermost box's margin and extending down the first-child spine until a bordered box or a childless box. The collapsed outer BOTTOM margin is the analogous collapse down the last-child spine. Apply the collapse rule to the set of margins in each run.

Report the collapsed outer TOP margin and the collapsed outer BOTTOM margin as two comma-separated integers, top first (for example "-3,5"). Answer with only that pair.
### Answer
7,2

