# samples_P001v1 - pickup_delivery_route_search

## Level 0

### Example 1

**Prompt:**

A courier starts at cell (0,0) on a 4x4 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 1 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (0, 3), delivery (0, 0)
  Job 1: pickup (0, 2), delivery (2, 0)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`0P0D1P1D`

### Example 2

**Prompt:**

A courier starts at cell (0,0) on a 4x4 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 1 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (2, 1), delivery (2, 2)
  Job 1: pickup (1, 0), delivery (2, 3)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`1P1D0P0D`

## Level 2

### Example 1

**Prompt:**

A courier starts at cell (0,0) on a 5x5 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 2 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (1, 1), delivery (0, 3)
  Job 1: pickup (0, 0), delivery (3, 4)
  Job 2: pickup (4, 3), delivery (0, 0)
  Job 3: pickup (3, 2), delivery (0, 0)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`1P0P0D1D2P3P2D3D`

### Example 2

**Prompt:**

A courier starts at cell (0,0) on a 5x5 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 2 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (0, 3), delivery (0, 4)
  Job 1: pickup (2, 0), delivery (3, 1)
  Job 2: pickup (0, 1), delivery (0, 0)
  Job 3: pickup (1, 2), delivery (4, 3)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`0P0D3P2P2D1P1D3D`

## Level 5

### Example 1

**Prompt:**

A courier starts at cell (0,0) on a 6x6 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 3 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (2, 0), delivery (5, 0)
  Job 1: pickup (3, 3), delivery (1, 4)
  Job 2: pickup (0, 2), delivery (0, 5)
  Job 3: pickup (4, 3), delivery (4, 4)
  Job 4: pickup (2, 1), delivery (0, 3)
  Job 5: pickup (3, 4), delivery (3, 2)
  Job 6: pickup (5, 3), delivery (3, 0)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`0P0D6P3P3D5P1P5D6D4P2P4D1D2D`

### Example 2

**Prompt:**

A courier starts at cell (0,0) on a 6x6 grid, moving only horizontally or vertically (Manhattan distance).
The vehicle carries at most 3 goods at once. Each job must be picked up at its pickup cell then delivered to its delivery cell; a delivery cannot happen before its pickup.
Jobs:
  Job 0: pickup (5, 4), delivery (5, 2)
  Job 1: pickup (0, 1), delivery (1, 0)
  Job 2: pickup (3, 5), delivery (5, 2)
  Job 3: pickup (3, 0), delivery (2, 3)
  Job 4: pickup (2, 0), delivery (0, 2)
  Job 5: pickup (4, 1), delivery (3, 0)
  Job 6: pickup (1, 3), delivery (4, 1)
Find a sequence of pickups and deliveries that respects the capacity, delivers every job after its pickup, and minimizes total travel. Answer with the stop order as a compact string like '0P1P0D1D' where 'jP' is picking up job j and 'jD' is delivering job j, for the shortest route (ties broken lexicographically).

**Answer:**

`1P1D3P4P4D6P3D2P0P0D2D5P6D5D`
