# Samples P029v1 - three_way_merge_resolution

## Level 0

### Example 1

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base d, left G, right Y
index 1, base e, left D, right e
index 2, base g, left D, right W
index 3, base e, left e, right X
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

<G|d|Y>
D
<D|g|W>
X


### Example 2

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base e, left e, right Z
index 1, base g, left H, right g
index 2, base d, left d, right Z
index 3, base b, left b, right W
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

Z
H
Z
W


## Level 2

### Example 1

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base b, left E, right W
index 1, base b, left b, right b
index 2, base g, left C, right g
index 3, base d, left A, right d
index 4, base g, left g, right X
index 5, base a, left a, right a
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

<E|b|W>
b
C
A
X
a


### Example 2

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base e, left e, right X
index 1, base f, left A, right Y
index 2, base c, left c, right c
index 3, base e, left F, right W
index 4, base e, left G, right e
index 5, base a, left H, right X
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

X
<A|f|Y>
c
<F|e|W>
G
<H|a|X>


## Level 5

### Example 1

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base f, left G, right f
index 1, base b, left b, right b
index 2, base g, left B, right g
index 3, base c, left c, right Z
index 4, base f, left B, right Z
index 5, base f, left B, right Y
index 6, base c, left G, right Z
index 7, base e, left F, right e
index 8, base f, left f, right Y
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

G
b
B
Z
<B|f|Z>
<B|f|Y>
<G|c|Z>
F
Y


### Example 2

**Prompt:**

Three-way merge. The base version has lines with these contents (showing base, left-author edit, then right-author edit per line):
index 0, base g, left G, right g
index 1, base d, left F, right W
index 2, base e, left e, right Z
index 3, base g, left A, right g
index 4, base b, left E, right b
index 5, base c, left E, right c
index 6, base e, left H, right e
index 7, base c, left c, right W
index 8, base g, left E, right g
Merge the two edits line by line. A line both authors changed to different values is a conflict: emit it as a bracketed triple <left|base|right>. A line only one author changed takes that author's new content. A line nobody changed keeps its base content. Return one merged output line per base index, in ascending index order, joined by newlines.

**Answer:**

G
<F|d|W>
Z
A
E
E
H
W
E

