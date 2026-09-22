Level 0
Prompt:
Tables with row counts:
T0: 210 rows
T1: 367 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,20) 15%, [20,40) 23%, [40,60) 18%, [60,80) 18%, [80,100) 26%
T1: [0,25) 24%, [25,50) 25%, [50,75) 33%, [75,100) 18%

Estimate the number of result rows of the following expression:
T1 WHERE col IN [28,97)
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
260
Prompt:
Tables with row counts:
T0: 223 rows
T1: 302 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,20) 27%, [20,40) 15%, [40,60) 21%, [60,80) 16%, [80,100) 21%
T1: [0,25) 25%, [25,50) 23%, [50,75) 30%, [75,100) 22%

Estimate the number of result rows of the following expression:
( T0 JOIN ( T1 WHERE col IN [12,25) AND T1 WHERE col IN [29,54) ) [independence] )
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
20

Level 2
Prompt:
Tables with row counts:
T0: 155 rows
T1: 240 rows
T2: 315 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,20) 23%, [20,40) 24%, [40,60) 11%, [60,80) 21%, [80,100) 21%
T1: [0,25) 25%, [25,50) 23%, [50,75) 23%, [75,100) 29%
T2: [0,25) 30%, [25,50) 25%, [50,75) 25%, [75,100) 20%

Estimate the number of result rows of the following expression:
( T0 WHERE col IN [80,96) OR T0 WHERE col IN [37,54) )
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
41
Prompt:
Tables with row counts:
T0: 355 rows
T1: 109 rows
T2: 87 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,25) 20%, [25,50) 30%, [50,75) 22%, [75,100) 28%
T1: [0,20) 16%, [20,40) 25%, [40,60) 17%, [60,80) 18%, [80,100) 24%
T2: [0,20) 25%, [20,40) 25%, [40,60) 15%, [60,80) 20%, [80,100) 15%

Estimate the number of result rows of the following expression:
T2 WHERE col IN [28,43)
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
15

Level 5
Prompt:
Tables with row counts:
T0: 292 rows
T1: 176 rows
T2: 124 rows
T3: 384 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,25) 31%, [25,50) 28%, [50,75) 20%, [75,100) 21%
T1: [0,25) 22%, [25,50) 21%, [50,75) 27%, [75,100) 30%
T2: [0,25) 28%, [25,50) 21%, [50,75) 24%, [75,100) 27%
T3: [0,25) 24%, [25,50) 30%, [50,75) 21%, [75,100) 25%

Estimate the number of result rows of the following expression:
( T3 WHERE col IN [12,71) OR ( T3 WHERE col IN [93,96) OR T3 WHERE col IN [96,100) ) )
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
242
Prompt:
Tables with row counts:
T0: 124 rows
T1: 386 rows
T2: 265 rows
T3: 296 rows

Column histograms (each bin [lo, hi) holds weight% of that table's rows, uniform within the bin):
T0: [0,25) 20%, [25,50) 31%, [50,75) 23%, [75,100) 26%
T1: [0,20) 23%, [20,40) 18%, [40,60) 16%, [60,80) 20%, [80,100) 23%
T2: [0,25) 20%, [25,50) 20%, [50,75) 26%, [75,100) 34%
T3: [0,20) 17%, [20,40) 27%, [40,60) 21%, [60,80) 13%, [80,100) 22%

Estimate the number of result rows of the following expression:
T3 WHERE col IN [39,96)
An independence join computes left*right/100; a containment join takes the smaller side.
Report the estimated cardinality as one non-negative integer.
Answer
157

