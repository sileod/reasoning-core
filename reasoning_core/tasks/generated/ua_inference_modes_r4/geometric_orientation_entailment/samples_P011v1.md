## Level 0
### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, B, D: cw
   B, C, D: cw
   B, C, E: cw
   B, D, E: cw
Queried triple: A, D, E
What verdict follows from the stated facts about that triple?

**Answer:**

alternatives

### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, C, D: cw
   A, D, E: cw
   B, C, D: ccw
   B, C, E: ccw
Queried triple: C, D, E
What verdict follows from the stated facts about that triple?

**Answer:**

cw

## Level 2
### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, B, C: cw
   A, B, D: ccw
   A, B, F: ccw
   A, C, E: ccw
   A, E, F: ccw
   B, C, D: cw
   B, D, E: cw
   C, D, E: cw
   C, D, F: cw
   C, E, F: ccw
   D, E, F: ccw
Queried triple: B, D, F
What verdict follows from the stated facts about that triple?

**Answer:**

cw

### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, B, D: cw
   A, C, D: cw
   A, C, F: cw
   A, D, E: ccw
   A, D, F: ccw
   A, E, F: ccw
   B, C, D: ccw
   B, C, E: cw
   B, D, E: cw
   C, D, E: ccw
   C, E, F: ccw
Queried triple: A, C, E
What verdict follows from the stated facts about that triple?

**Answer:**

cw

## Level 5
### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, B, C: ccw
   A, B, D: cw
   A, B, E: cw
   A, B, G: ccw
   A, C, D: cw
   A, C, E: cw
   A, C, F: ccw
   A, C, G: cw
   A, D, E: ccw
   A, D, F: ccw
   A, D, G: ccw
   A, E, F: ccw
   A, E, G: ccw
   B, C, D: ccw
   B, C, E: ccw
   B, C, F: ccw
   B, C, G: cw
   B, D, E: ccw
   B, D, G: cw
   B, E, F: cw
   B, E, G: cw
   B, F, G: cw
   C, D, E: ccw
   C, D, F: cw
   C, D, G: ccw
   C, E, G: ccw
   C, F, G: ccw
   D, E, F: ccw
   D, E, G: ccw
   D, F, G: cw
Queried triple: B, D, F
What verdict follows from the stated facts about that triple?

**Answer:**

cw

### Example
**Prompt:**

A set of labeled planar points lies on the boundary of a common convex hull, so every triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the known orientation facts for some triples of points. If they force a single orientation for the queried triple, reply cw or ccw; if several orientations stay consistent with the facts, reply alternatives.

Known orientation facts:
   A, B, C: ccw
   A, B, D: ccw
   A, B, F: cw
   A, B, G: ccw
   A, C, E: cw
   A, C, F: cw
   A, C, G: cw
   A, D, E: cw
   A, D, F: cw
   A, D, G: cw
   A, E, F: cw
   A, E, G: ccw
   A, F, G: ccw
   B, C, D: cw
   B, C, E: ccw
   B, C, F: ccw
   B, C, G: cw
   B, D, E: ccw
   B, D, F: ccw
   B, D, G: cw
   B, E, F: cw
   B, E, G: cw
   C, D, E: cw
   C, D, F: cw
   C, D, G: cw
   C, E, F: cw
   C, F, G: ccw
   D, E, G: ccw
   D, F, G: ccw
   E, F, G: cw
Queried triple: C, E, G
What verdict follows from the stated facts about that triple?

**Answer:**

ccw
