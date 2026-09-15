## Level 0
### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: binary byte sequence: 11101111 10001000 10110110

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

C:62006

### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: binary byte sequence: 11101111 10000111 10011100

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

C:61916

## Level 2
### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: binary byte sequence: 11001101 10110110
Segment 2: code point: 50

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

C:886 | B:50

### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: code point: 981
Segment 2: code point: 49209
Segment 3: binary byte sequence: 11110010 10111010 10010110 10000011

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

B:207 149 | B:236 128 185 | C:763267

## Level 5
### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: code point: 111
Segment 2: binary byte sequence: 11001000 10011101
Segment 3: code point: 1059
Segment 4: code point: 112
Segment 5: code point: 1068
Segment 6: code point: 228859
Segment 7: code point: 75
Segment 8: binary byte sequence: 11001101 10001100
Segment 9: binary byte sequence: 11110001 10011010 10100000 10010101
Segment 10: code point: 58571

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

B:111 | C:541 | B:208 163 | B:112 | B:208 172 | B:240 183 183 187 | B:75 | C:844 | C:370709 | B:238 147 139

### Example
**Prompt:**

Translate each Unicode segment between a code point (an integer) and its UTF-8 encoding given as a binary byte sequence (8 bits per byte). For a segment given as a code point, give its UTF-8 byte sequence as decimal byte values; for a segment given as a binary byte sequence, give the decoded code point.

Segment 1: binary byte sequence: 11001101 10100011
Segment 2: code point: 61209

Give the results in the same order, joined by ' | '. Use 'B: v1 v2 ...' for a byte list and 'C: v' for a code point.

**Answer:**

C:867 | B:238 188 153

