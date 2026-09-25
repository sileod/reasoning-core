## Level 0

### Example 1

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1.
Each factor takes integer levels 0..2. The design is a balanced subset; only these cells were measured:
  (F0=0, F1=0): response 9
  (F0=1, F1=0): response 2
  (F0=1, F1=2): response 23
  (F0=2, F1=0): response 27
  (F0=2, F1=1): response 9
  (F0=2, F1=2): response 14

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 2.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `-7`

### Example 2

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1.
Each factor takes integer levels 0..2. The design is a balanced subset; only these cells were measured:
  (F0=0, F1=2): response 15
  (F0=1, F1=0): response 8
  (F0=1, F1=2): response 7
  (F0=2, F1=0): response 7
  (F0=2, F1=1): response 20
  (F0=2, F1=2): response 18

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 2.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `2`

## Level 2

### Example 1

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1.
Each factor takes integer levels 0..2. The design is a balanced subset; only these cells were measured:
  (F0=0, F1=0): response 23
  (F0=0, F1=1): response 22
  (F0=0, F1=2): response 15
  (F0=1, F1=0): response 7
  (F0=1, F1=1): response 5
  (F0=1, F1=2): response 5
  (F0=2, F1=0): response 3
  (F0=2, F1=2): response 14

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 2.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `6`

### Example 2

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1.
Each factor takes integer levels 0..2. The design is a balanced subset; only these cells were measured:
  (F0=0, F1=0): response 22
  (F0=0, F1=1): response 15
  (F0=0, F1=2): response 4
  (F0=1, F1=1): response 30
  (F0=1, F1=2): response 7
  (F0=2, F1=0): response 25
  (F0=2, F1=1): response 1
  (F0=2, F1=2): response 0

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 2.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `1`

## Level 5

### Example 1

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1, F2.
Each factor takes integer levels 0..3. The design is a balanced subset; only these cells were measured:
  (F0=1, F1=0, F2=1): response 4
  (F0=1, F1=0, F2=2): response 28
  (F0=1, F1=1, F2=2): response 14
  (F0=1, F1=1, F2=3): response 1
  (F0=1, F1=2, F2=2): response 11
  (F0=1, F1=3, F2=0): response 7
  (F0=1, F1=3, F2=1): response 11
  (F0=2, F1=3, F2=0): response 15
  (F0=3, F1=1, F2=3): response 29
  (F0=3, F1=2, F2=0): response 21
  (F0=3, F1=3, F2=3): response 1

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 3.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `-12`

### Example 2

**Prompt:**

```
An experiment measures a response under joint interventions on factors labeled F0, F1, F2.
Each factor takes integer levels 0..3. The design is a balanced subset; only these cells were measured:
  (F0=0, F1=2, F2=2): response 19
  (F0=0, F1=3, F2=1): response 13
  (F0=0, F1=3, F2=2): response 22
  (F0=1, F1=0, F2=0): response 25
  (F0=2, F1=3, F2=0): response 15
  (F0=2, F1=3, F2=2): response 26
  (F0=3, F1=0, F2=0): response 15
  (F0=3, F1=1, F2=2): response 18
  (F0=3, F1=2, F2=3): response 18
  (F0=3, F1=3, F2=0): response 17
  (F0=3, F1=3, F2=3): response 5

Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is 3.
Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.
The additive prediction at the (top, top) cell is G + E0 + E1.
The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.

Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).
```

**Answer:** `-2`
