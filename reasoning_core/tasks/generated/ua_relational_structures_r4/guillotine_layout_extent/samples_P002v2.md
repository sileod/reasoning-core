## Level 0
### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 10x11
  leaf 1: 2x7
Gutter width: 1

Slicing plan (root left; leaf indices; L means leaf):
  Hg(0,1)

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
10x14
```

### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 15x5
  leaf 1: 12x14
Gutter width: 1

Slicing plan (root left; leaf indices; L means leaf):
  Hg(0,1)

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
15x18
```

## Level 2
### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 7x10
  leaf 1: 20x25
  leaf 2: 9x22
  leaf 3: 5x17
Gutter width: 1

Slicing plan (root left; leaf indices; L means leaf):
  Vg(Vg(Hg(0,1),2),3)

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
41x28
```

### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 17x3
  leaf 1: 18x9
  leaf 2: 24x11
  leaf 3: 25x16
Gutter width: 1

Slicing plan (root left; leaf indices; L means leaf):
  Vg(Vg(0,1),H(2,3))

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
39x27
```

## Level 5
### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 2x38
  leaf 1: 29x7
  leaf 2: 10x30
  leaf 3: 2x32
  leaf 4: 33x34
  leaf 5: 5x6
  leaf 6: 4x19
  leaf 7: 25x14
Gutter width: 2

Slicing plan (root left; leaf indices; L means leaf):
  V(Vg(Vg(0,1),2),Hg(Vg(Vg(3,4),5),V(6,7)))

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
68x49
```

### Example
**Prompt**
```text
A guillotine layout packs leaf rectangles that may each be rotated 90
degrees (equivalently swapping width and height). The slicing plan is a
binary tree. Each internal cut is V (vertical: sub-blocks sit side by
side, widths add, and heights are forced to align across the shared cut)
or H (horizontal: sub-blocks stack, heights add, widths align). A cut
marked Vg or Hg is a gutter cut running on the same V or H axis but
additionally consuming a fixed gutter width from the spliced span.

Leaf rectangles (width x height):
  leaf 0: 10x31
  leaf 1: 21x35
  leaf 2: 27x9
  leaf 3: 7x8
  leaf 4: 11x16
  leaf 5: 24x34
  leaf 6: 16x32
  leaf 7: 8x31
Gutter width: 2

Slicing plan (root left; leaf indices; L means leaf):
  V(Hg(H(0,1),Vg(2,Vg(3,4))),Vg(5,Vg(6,7)))

Rotations are chosen to minimize enclosing area. Because leaf edges must
align with cut lines across sibling subtrees, the smaller sibling is
grown to the larger in the shared dimension. Report the minimum-area
enclosing width and height as WxH (e.g. 14x9).
```
**Answer**
```text
106x44
```
