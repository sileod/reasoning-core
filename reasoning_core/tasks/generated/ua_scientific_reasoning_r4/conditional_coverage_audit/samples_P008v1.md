# Level 0
## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 76%.
Stratum 1: true=[1,1] sets=[{0,1},{1}]
Stratum 2: true=[0,0,0] sets=[{1},{1},{1}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [1, 0]; failing: [2]

## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 75%.
Stratum 1: true=[0,0,1] sets=[{0,1},{0},{0,1}]
Stratum 2: true=[0,0,0] sets=[{1},{1},{1}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [1, 0]; failing: [2]

# Level 2
## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 70%.
Stratum 1: true=[1,0,1,1] sets=[{0,1},{1},{0},{0}]
Stratum 2: true=[0,1,1,0] sets=[{1},{0},{0},{1}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [1/4, 0]; failing: [1, 2]

## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 57%.
Stratum 1: true=[1,1,1] sets=[{0},{0},{0}]
Stratum 2: true=[0,1,1,0] sets=[{0},{1},{0,1},{0,1}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [0, 1]; failing: [1]

# Level 5
## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 63%.
Stratum 1: true=[1,1] sets=[{1},{0,1}]
Stratum 2: true=[1,0] sets=[{1},{0}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [1, 1]; failing: []

## Example
Prompt:
This is a finite-sample confidence audit. The sampling space is split into ancillary strata. Every point carries a true binary value (0 or 1) and a reported confidence set (a singleton such as {0} or the full set {0,1}); the reported set covers the point exactly when the true value is a member, and short reported sets are the stopping-event/reported-width subset that can break coverage. Advertised coverage A is an integer percentage: each stratum must cover at least A% of its own points. For every stratum compute its conditional coverage = (points in it that are covered by their reported set) / (points in it), and list every stratum whose coverage is strictly below A%. Advertised coverage: 86%.
Stratum 1: true=[0,1,1,1,0] sets=[{0,1},{1},{0,1},{1},{0}]
Stratum 2: true=[1,0,1,0,0,0,0,1] sets=[{0,1},{0,1},{1},{0},{0},{0,1},{0},{1}]
Stratum 3: true=[0,1,0,0,0,0] sets=[{0},{1},{0},{0,1},{0},{0,1}]
Stratum 4: true=[0,0,1,0,1] sets=[{0},{0},{1},{0,1},{0}]
Stratum 5: true=[1,1,1,1] sets=[{0},{0},{0},{0}]
Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] with every fraction reduced and stratum indices 1-based and ascending (no failing strata -> failing: []).
Answer:
coverage: [1, 1, 1, 4/5, 0]; failing: [4, 5]
