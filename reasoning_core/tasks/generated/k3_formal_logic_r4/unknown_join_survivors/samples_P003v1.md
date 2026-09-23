## Level 0

Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=2, x=1
  r1: p=1, x=None
Table S (row key, join value p, value y):
  s0: p=1, y=None
  s1: p=1, y=1
  s2: p=2, y=None

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  p >= 0

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r0,s2) (r1,s0) (r1,s1)


Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=1, x=1
  r1: p=1, x=1
  r2: p=2, x=0
Table S (row key, join value p, value y):
  s0: p=2, y=1
  s1: p=None, y=0
  s2: p=2, y=None

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  x < p

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r2,s0) (r2,s2)

## Level 2

Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=2, x=1
  r1: p=1, x=0
Table S (row key, join value p, value y):
  s0: p=None, y=2
  s1: p=1, y=1
  s2: p=1, y=2

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  p <= p AND p >= y

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r1,s1)


Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=3, x=0
  r1: p=2, x=1
  r2: p=2, x=1
  r3: p=2, x=None
Table S (row key, join value p, value y):
  s0: p=3, y=2
  s1: p=None, y=None
  s2: p=3, y=1
  s3: p=2, y=2

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  NOT ( p != 2 )

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r1,s3) (r2,s3) (r3,s3)

## Level 5

Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=2, x=1
  r1: p=1, x=2
  r2: p=3, x=2
Table S (row key, join value p, value y):
  s0: p=4, y=1
  s1: p=2, y=3
  s2: p=1, y=0
  s3: p=4, y=1
  s4: p=3, y=3

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  NOT ( p >= None AND p = 3 AND y <= y )

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r0,s1) (r1,s2)


Evaluate a bag natural join followed by a selection over two small tables.

Table R (row key, join value p, value x):
  r0: p=None, x=3
  r1: p=1, x=1
  r2: p=2, x=2
Table S (row key, join value p, value y):
  s0: p=None, y=1
  s1: p=2, y=1
  s2: p=3, y=None

Join R and S on attribute p (rows match when their p values are equal; NULL never matches). A matched row carries p, x (from R) and y (from S). This is a bag join: every matching (R,S) pair is its own output row.

Then apply the selection predicate:
  NOT ( p != y AND p < y AND p != 3 )

The predicate uses SQL three-valued logic: a comparison involving NULL yields UNKNOWN, and NOT UNKNOWN is UNKNOWN. A row survives only when the predicate evaluates to TRUE.

Answer the keys of the surviving joined rows as an ordered list, one (Rkey,Skey) per survivor in join order (R rows top to bottom, then S rows top to bottom within each R row), duplicates repeated, separated by spaces. If the list would be empty, output the two characters [ ] instead.

Answer: (r2,s1)
