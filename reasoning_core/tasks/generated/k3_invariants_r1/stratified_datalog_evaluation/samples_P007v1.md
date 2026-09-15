# Samples for P007v1 (stratified_datalog_evaluation)

## Level 0

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(0,2), p0(2,2).
  p1(1).
Rules:
  p1(a) :- p1(a).
  p1(a) :- not p0(a,b), p1(a).
  p0(a,b) :- p0(a,b).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p1.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p1(1)]
```

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(2).
  p1(0,2).
Rules:
  p0(a) :- p1(a,b).
  p0(a) :- p1(a,b), p1(a,b).
  p1(a,b) :- p0(a).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p0.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p0(0), p0(2)]
```

## Level 2

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(3,3).
  p1(4,1).
  p2(4,4).
Rules:
  p1(a,b) :- p0(a,b), p0(a,b).
  p1(a,b) :- p1(a,b).
  p1(a,b) :- p0(a,b), p2(a,b).
  p2(a,b) :- p2(a,b).
  p2(a,b) :- p0(a,b).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p2.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p2(3,3), p2(4,4)]
```

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(0).
  p1(2,0), p1(2,1).
  p2(2), p2(4).
Rules:
  p1(a,b) :- p0(a).
  p2(a) :- p1(a,b), p0(a).
  p2(a) :- p1(a,b), p2(a).
  p2(a) :- p1(a,b), p1(a,b).
  p0(a) :- p1(a,b), p0(a).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p0.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p0(0)]
```

## Level 5

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(2,7), p0(5,2).
  p1(4,2), p1(5,5), p1(6,6).
  p2(0,6), p2(1,2), p2(1,6), p2(6,2).
  p3(0), p3(1), p3(5), p3(6).
Rules:
  p3(a) :- p3(a).
  p1(a,b) :- p3(a).
  p3(a) :- p3(a), p3(a).
  p2(a,b) :- p3(a).
  p2(a,b) :- p1(a,b), p2(a,b).
  p2(a,b) :- p0(a,b).
  p1(a,b) :- p3(a).
  p1(a,b) :- p0(a,b), p1(a,b).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p2.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p2(0,0), p2(0,1), p2(0,2), p2(0,3), p2(0,4), p2(0,5), p2(0,6), p2(0,7), p2(1,0), p2(1,1), p2(1,2), p2(1,3), p2(1,4), p2(1,5), p2(1,6), p2(1,7), p2(2,7), p2(5,0), p2(5,1), p2(5,2), p2(5,3), p2(5,4), p2(5,5), p2(5,6), p2(5,7), p2(6,0), p2(6,1), p2(6,2), p2(6,3), p2(6,4), p2(6,5), p2(6,6), p2(6,7)]
```

### Example

**Prompt**

```
The following is a stratified Datalog program with negation.
Facts:
  p0(1).
  p1(0), p1(6).
  p2(0), p2(4).
  p3(1), p3(3), p3(4), p3(6).
Rules:
  p1(a) :- p2(a).
  p1(a) :- not p2(a).
  p0(a) :- p1(a), p3(a).
  p0(a) :- p1(a), p1(a).
  p1(a) :- p0(a).
  p1(a) :- p2(a).
  p3(a) :- p0(a).
  p2(a) :- p2(a).
Evaluate this program under stratified Datalog semantics: order the strata along negative dependencies and saturate each stratum to a fixed point, using already-computed facts of lower strata when a negated literal appears. Determine every ground fact derivable for predicate p0.
Answer as a canonical sorted list of ground atoms with arguments in ascending numeric order, e.g. [p(0), p(2)] or [] if none are derivable.
```

**Answer**

```
[p0(0), p0(1), p0(2), p0(3), p0(4), p0(5), p0(6), p0(7)]
```
