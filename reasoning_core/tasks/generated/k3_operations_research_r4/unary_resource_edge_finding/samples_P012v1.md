## Level 0

### Example 1

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 8, deadline 14, duration 2
task 1: release 5, deadline 10, duration 2
task 2: release 7, deadline 10, duration 3
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the earliest start of task 1 that is forced by the other tasks' load. Give only that tightened earliest start as an integer.

Answer: 5

### Example 2

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 3, deadline 11, duration 3
task 1: release 0, deadline 4, duration 2
task 2: release 2, deadline 9, duration 2
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the earliest start of task 0 that is forced by the other tasks' load. Give only that tightened earliest start as an integer.

Answer: 3

## Level 2

### Example 1

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 10, deadline 26, duration 4
task 1: release 7, deadline 26, duration 5
task 2: release 18, deadline 23, duration 3
task 3: release 2, deadline 14, duration 3
task 4: release 13, deadline 16, duration 3
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the earliest start of task 0 that is forced by the other tasks' load. Give only that tightened earliest start as an integer.

Answer: 16

### Example 2

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 18, deadline 24, duration 5
task 1: release 8, deadline 13, duration 5
task 2: release 11, deadline 26, duration 2
task 3: release 10, deadline 20, duration 3
task 4: release 8, deadline 23, duration 3
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the earliest start of task 3 that is forced by the other tasks' load. Give only that tightened earliest start as an integer.

Answer: 13

## Level 5

### Example 1

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 29, deadline 42, duration 5
task 1: release 35, deadline 42, duration 2
task 2: release 24, deadline 27, duration 3
task 3: release 24, deadline 34, duration 2
task 4: release 24, deadline 35, duration 3
task 5: release 10, deadline 32, duration 7
task 6: release 6, deadline 40, duration 5
task 7: release 3, deadline 44, duration 7
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the latest end of task 5 that is forced by the other tasks' load. Give only that tightened latest end as an integer.

Answer: 22

### Example 2

A single machine processes tasks one at a time without interruption (a unary resource). Each task must run inside its own window [release, deadline]; nothing can be split and the machine is never idle unless it must wait for a release.
task 0: release 22, deadline 32, duration 7
task 1: release 0, deadline 21, duration 6
task 2: release 35, deadline 39, duration 2
task 3: release 29, deadline 39, duration 5
task 4: release 2, deadline 14, duration 3
task 5: release 0, deadline 24, duration 4
task 6: release 29, deadline 39, duration 2
task 7: release 4, deadline 18, duration 5
There is one machine and every schedule shown below is a valid order of the tasks that keeps each inside its window. Run overload and edge-finding passes to infer the latest end of task 3 that is forced by the other tasks' load. Give only that tightened latest end as an integer.

Answer: 36
