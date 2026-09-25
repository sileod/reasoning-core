# Witness uniformity semantics samples

## Level 0

### Example 1

Consider quantified clauses over the integer domain D = [0, 1]. The witness variables are ['y0', 'y1'] and the universal variables are ['x0']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1]: at least one clause is satisfied? The clauses are:
(y0>0 AND x0<1) AND (x0!=1 AND y0!=1)
Answer 'yes' or 'no'.

**Answer:** no

### Example 2

Consider quantified clauses over the integer domain D = [0, 1]. The witness variables are ['y0', 'y1'] and the universal variables are ['x0']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1]: at least one clause is satisfied? The clauses are:
(x0>1 AND x0<1) AND (x0!=1 AND y0>1)
Answer 'yes' or 'no'.

**Answer:** no

## Level 2

### Example 1

Consider quantified clauses over the integer domain D = [0, 1]. The witness variables are ['y0', 'y1', 'y2'] and the universal variables are ['x0', 'x1']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1], forall x1 in [0, 1]: at least one clause is satisfied? The clauses are:
(x1=0 AND y0<1) AND (y0=1 AND x1=1) AND (y1!=0 AND x0!=0)
Answer 'yes' or 'no'.

**Answer:** no

### Example 2

Consider quantified clauses over the integer domain D = [0, 1]. The witness variables are ['y0', 'y1', 'y2'] and the universal variables are ['x0', 'x1']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1], forall x1 in [0, 1]: at least one clause is satisfied? The clauses are:
(y2<1 AND x1=1) AND (y1!=0 AND y2>1) AND (y0=0 AND y0<0)
Answer 'yes' or 'no'.

**Answer:** no

## Level 5

### Example 1

Consider quantified clauses over the integer domain D = [0, 1, 2]. The witness variables are ['y0', 'y1', 'y2', 'y3'] and the universal variables are ['x0', 'x1']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1, 2], forall x1 in [0, 1, 2]: at least one clause is satisfied? The clauses are:
(y2>1 AND y2!=1) AND (y3<1 AND x1!=2) AND (y0!=0 AND y1>0) AND (x0>1 AND y3>2)
Answer 'yes' or 'no'.

**Answer:** yes

### Example 2

Consider quantified clauses over the integer domain D = [0, 1, 2]. The witness variables are ['y0', 'y1', 'y2', 'y3'] and the universal variables are ['x0', 'x1']. A uniform witness policy is a single assignment fixing every witness variable, used regardless of the values the universal variables take. Does there exist a uniform witness policy such that forall x0 in [0, 1, 2], forall x1 in [0, 1, 2]: at least one clause is satisfied? The clauses are:
(y3>0 AND y2!=2) AND (x0>2 AND y1!=0) AND (y2<1 AND x0=0) AND (y2<2 AND x0<0)
Answer 'yes' or 'no'.

**Answer:** yes
