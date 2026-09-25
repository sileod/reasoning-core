## Level 0
### Example 1
Truthmaker semantics. The named individuals are {a, b}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: (Q(a) and ((P(a) and not Q(a)) and not P(a)))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** NO

### Example 2
Truthmaker semantics. The named individuals are {a, b}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: (((P(b) or not Q(a)) and not Q(a)) and P(b))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** P(b)

## Level 2
### Example 1
Truthmaker semantics. The named individuals are {a, b, c, d}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: (((((Q(a) and P(b)) and Q(b)) or not P(b)) and P(d)) and P(a))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** P(a) P(d)

### Example 2
Truthmaker semantics. The named individuals are {a, b, c, d}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: ((P(a) and P(b)) and ((not P(b) and not Q(d)) and P(b)))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** NO

## Level 5
### Example 1
Truthmaker semantics. The named individuals are {a, b, c, d}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: (((((not P(a) or R(c)) or Q(c)) and not R(b)) or ((((not P(c) and not Q(d)) or not Q(c)) or (((R(d) and not R(c)) and P(b)) and not R(c))) or not P(a))) or not Q(c))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** EMPTY

### Example 2
Truthmaker semantics. The named individuals are {a, b, c, d}. A fact is an atomic claim like P(a) (positive) or not P(a) (negative). A situation is a set of facts that obtain. A situation S supports a clause as follows: S supports P(x) iff the fact P(x) is in S; S supports not P(x) iff the fact P(x) is not in S; S supports (A and B) iff it supports both; S supports (A or B) iff it supports at least one; S supports (for every x in D: F) iff it supports F(x) for each x in D; S supports (for some x in D: F) iff it supports F(x) for some x in D.

Consider the clause: (for every x in {a, b, c, d}: not P(x))

Give the unique minimal supporting situation (the smallest set of facts by inclusion that supports the clause). If none exists or more than one minimal situation exists, answer exactly NO. Otherwise list the facts of the unique situation separated by spaces and sorted lexicographically, e.g. 'P(a) Q(b)', or exactly EMPTY if no facts are needed.

**Answer:** EMPTY
