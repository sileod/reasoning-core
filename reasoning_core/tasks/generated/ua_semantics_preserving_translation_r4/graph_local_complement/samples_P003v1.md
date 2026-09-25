# samples_P003v1

## Level 0

Starting edge list:
(1,3) (2,3)
This is a simple undirected graph on vertices 0..3.

Apply in order:
pivot on edge (1,3)
delete vertex 1
pivot on edge (2,3)

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (2,3) present?

Answer: yes

Starting edge list:
(0,1) (2,3)
This is a simple undirected graph on vertices 0..3.

Apply in order:
delete vertex 1
delete vertex 3

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (0,2) present?

Answer: no

## Level 2

Starting edge list:
(1,5) (1,4) (1,2) (2,3) (2,5) (0,3) (4,5)
This is a simple undirected graph on vertices 0..5.

Apply in order:
pivot on edge (0,3)
pivot on edge (1,5)
delete vertex 1
local complement at vertex 0
local complement at vertex 4

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (0,3) present?

Answer: yes

Starting edge list:
(0,3) (1,3) (2,3) (1,2) (0,4) (4,5) (1,4) (0,2)
This is a simple undirected graph on vertices 0..5.

Apply in order:
delete vertex 3
pivot on edge (1,4)
pivot on edge (4,1)
pivot on edge (1,4)
delete vertex 4

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (2,5) present?

Answer: no

## Level 5

Starting edge list:
(7,8) (0,3) (1,7) (2,8) (2,6) (3,7) (1,5) (1,4) (0,4) (5,7) (3,4) (3,6) (4,8) (2,7) (5,8) (6,8) (1,3) (0,7)
This is a simple undirected graph on vertices 0..8.

Apply in order:
pivot on edge (0,7)
delete vertex 1
delete vertex 6
delete vertex 0
local complement at vertex 8
local complement at vertex 5
pivot on edge (2,5)
pivot on edge (8,3)

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (4,8) present?

Answer: no

Starting edge list:
(4,8) (2,5) (1,5) (2,7) (7,8) (0,2) (5,6) (3,4) (5,7) (4,5) (1,7) (2,3) (0,7) (2,6) (3,7) (1,6) (3,6) (0,1) (2,4) (1,2) (2,8)
This is a simple undirected graph on vertices 0..8.

Apply in order:
pivot on edge (3,6)
delete vertex 4
delete vertex 7
pivot on edge (2,8)
local complement at vertex 0
local complement at vertex 3
local complement at vertex 5
delete vertex 5

Reply yes if the queried edge is present after all operations, and no otherwise.
Is the edge (0,8) present?

Answer: yes
