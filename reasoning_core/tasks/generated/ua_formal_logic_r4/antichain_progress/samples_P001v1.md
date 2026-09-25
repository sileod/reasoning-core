# P001v1 samples

## Level 0

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 3 precedes timestamp 71
- timestamp 3 precedes timestamp 55
- timestamp 71 precedes timestamp 87
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [71]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 3 dominated?
- Is timestamp 71 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** No Yes

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 13 precedes timestamp 48
- timestamp 79 precedes timestamp 28
- timestamp 28 precedes timestamp 13
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [13, 28, 48]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 48 dominated?
- Is timestamp 79 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** Yes No

## Level 2

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 17 precedes timestamp 81
- timestamp 81 precedes timestamp 96
- timestamp 96 precedes timestamp 45
- timestamp 14 precedes timestamp 96
- timestamp 14 precedes timestamp 67
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [45, 67, 81]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 45 dominated?
- Is timestamp 14 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** Yes No

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 23 precedes timestamp 61
- timestamp 33 precedes timestamp 23
- timestamp 61 precedes timestamp 65
- timestamp 65 precedes timestamp 22
- timestamp 83 precedes timestamp 22
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [23, 61]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 83 dominated?
- Is timestamp 23 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** No Yes

## Level 5

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 68 precedes timestamp 88
- timestamp 68 precedes timestamp 55
- timestamp 53 precedes timestamp 19
- timestamp 58 precedes timestamp 59
- timestamp 54 precedes timestamp 88
- timestamp 19 precedes timestamp 54
- timestamp 19 precedes timestamp 66
- timestamp 59 precedes timestamp 55
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [19, 54, 55, 58, 66, 68]
Frontier 2 contains timestamps: [19, 88]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 53 dominated?
- Is timestamp 88 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** No Yes

### Example

A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:
- timestamp 28 precedes timestamp 89
- timestamp 28 precedes timestamp 2
- timestamp 28 precedes timestamp 93
- timestamp 93 precedes timestamp 12
- timestamp 63 precedes timestamp 66
- timestamp 63 precedes timestamp 12
- timestamp 63 precedes timestamp 2
- timestamp 63 precedes timestamp 14
Precedence is transitive: if a precedes b and b precedes c, then a precedes c.

A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.
Frontier 1 contains timestamps: [2, 12, 14, 17, 28, 89, 93]
Frontier 2 contains timestamps: [2, 12, 28, 89, 93]

For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.
- Is timestamp 63 dominated?
- Is timestamp 14 dominated?

Reply with Yes or No for each query, in order, separated by spaces.

**Answer:** No Yes
