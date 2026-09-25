## Level 0

### Example 1

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcd}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; abd; ac; b; bd; c.
What are the minimal (non-inherited) conflict pairs of the structure? A conflict pair {X, Y} is minimal when X and Y are in conflict and no cause of X is in conflict with Y, and no cause of Y is in conflict with X.
List each pair with the letters joined (smaller letter first) and the pairs in ascending alphabetical order, separated by commas. For example, if the minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`.

**Answer:**
bc

### Example 2

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcd}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; ac; c.
What are the minimal (non-inherited) conflict pairs of the structure? A conflict pair {X, Y} is minimal when X and Y are in conflict and no cause of X is in conflict with Y, and no cause of Y is in conflict with X.
List each pair with the letters joined (smaller letter first) and the pairs in ascending alphabetical order, separated by commas. For example, if the minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`.

**Answer:**
bc

## Level 2

### Example 1

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcde}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; abd; ac; c.
What are the minimal (non-inherited) conflict pairs of the structure? A conflict pair {X, Y} is minimal when X and Y are in conflict and no cause of X is in conflict with Y, and no cause of Y is in conflict with X.
List each pair with the letters joined (smaller letter first) and the pairs in ascending alphabetical order, separated by commas. For example, if the minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`.

**Answer:**
bc

### Example 2

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcde}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; abd; ac; acd; acde; ad; ade; c; cd; cde; d; de.
What are the minimal (non-inherited) conflict pairs of the structure? A conflict pair {X, Y} is minimal when X and Y are in conflict and no cause of X is in conflict with Y, and no cause of Y is in conflict with X.
List each pair with the letters joined (smaller letter first) and the pairs in ascending alphabetical order, separated by commas. For example, if the minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`.

**Answer:**
bc, be

## Level 5

### Example 1

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcdefg}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; abc; abcd; abcde; abcf; abcfg.
What are the minimal (non-inherited) conflict pairs of the structure? A conflict pair {X, Y} is minimal when X and Y are in conflict and no cause of X is in conflict with Y, and no cause of Y is in conflict with X.
List each pair with the letters joined (smaller letter first) and the pairs in ascending alphabetical order, separated by commas. For example, if the minimal conflicts were {a,b} and {c,d} the answer would be exactly `ab, cd`.

**Answer:**
df

### Example 2

**Prompt:**
A prime event structure fixes a partial order (causality) and a conflict relation over a set of events. Two events are in conflict exactly when no configuration contains them together; event A causes event B exactly when every configuration containing B also contains A. A conflict inherited from a cause onto its effect is still a conflict.
The universe of events is {abcdefg}. The configuration family (every configuration, i.e. each causally-closed, conflict-free subset of events reachable in some step) is:
; a; ab; abc; abcd; abcde; abcdef; abcdeg.
What are the immediate causes of event f? The immediate causes of an event are its maximal proper causes: the events M such that M causes f and no other cause lies strictly between M and f.
List them in ascending order, separated by commas, using the given event letters. For example, if the immediate causes were a and c the answer would be exactly `a, c`.

**Answer:**
e

