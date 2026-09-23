# Samples for positional_weight_station_packing (P005v1)

## Level 0

### Example 1

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D
    Durations:
      A: 6  B: 1  C: 2  D: 5
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> (none)
      C -> A
      D -> B
    Cycle time: 15
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=A,B,C,D idle=1 | balance_delay=1/15

### Example 2

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D
    Durations:
      A: 2  B: 6  C: 6  D: 1
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> (none)
      C -> A B
      D -> A
    Cycle time: 6
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=B idle=0 | S2=A,D idle=3 | S3=C idle=0 | balance_delay=1/6

## Level 2

### Example 1

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D E F G
    Durations:
      A: 5  B: 10  C: 10  D: 4  E: 8  F: 7  G: 4
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> A
      C -> (none)
      D -> A B C
      E -> B C D
      F -> D E
      G -> A B D E F
    Cycle time: 16
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=A,B idle=1 | S2=C,D idle=2 | S3=E,F idle=1 | S4=G idle=12 | balance_delay=1/4

### Example 2

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D E F G
    Durations:
      A: 6  B: 4  C: 7  D: 1  E: 3  F: 8  G: 5
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> A
      C -> A B
      D -> A B
      E -> A C D
      F -> A
      G -> A B F
    Cycle time: 26
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=A,B,C,D,F idle=0 | S2=E,G idle=18 | balance_delay=9/26

## Level 5

### Example 1

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D E F G H I J K L
    Durations:
      A: 10  B: 4  C: 7  D: 16  E: 15  F: 12  G: 8  H: 3  I: 6  J: 11  K: 5  L: 3
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> A
      C -> B
      D -> B C
      E -> A B C D
      F -> A D E
      G -> B C F
      H -> A B C D G
      I -> C D E F G H
      J -> A B C D E G H I
      K -> A C D E H I J
      L -> A C D G J K
    Cycle time: 26
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=A,B,C idle=5 | S2=D idle=10 | S3=E idle=11 | S4=F,G,H idle=3 | S5=I,J,K,L idle=1 | balance_delay=3/13

### Example 2

**Prompt:**

    An assembly line has precedence-constrained tasks, each with a fixed duration, to be placed into one or more stations of equal cycle time. Ranked positional weight (RPW) packs tasks greedily: the positional weight of a task is its own duration plus the durations of all of its (direct and indirect) successors; sort tasks by descending positional weight (ties by label, alphabetically), then assign each task, in that order, to the lowest-numbered station whose remaining capacity still fits the task, all of whose predecessors are already placed (in this or an earlier station). A station's idle time is cycle time minus the sum of the durations assigned to it, and the balance delay is (number_of_stations * cycle_time - total_work) / (number_of_stations * cycle_time), reduced to lowest terms.
    
    Tasks: A B C D E F G H I J K L
    Durations:
      A: 15  B: 1  C: 5  D: 7  E: 15  F: 16  G: 5  H: 14  I: 16  J: 7  K: 14  L: 8
    Precedence (a -> b means a must finish before b can begin):
      A -> (none)
      B -> A
      C -> A
      D -> A C
      E -> B C
      F -> A B C D E
      G -> A C D E F
      H -> A B D E F G
      I -> A B C D F G H
      J -> A B C D E F G I
      K -> B E F G H I J
      L -> A B C E G I J K
    Cycle time: 17
    
    Give the station packing as 'S1=A,B idle=3 | S2=C idle=0 | balance_delay=1/4': one station roster per station in order (its sorted labels), the station's idle time, then the balance delay as a reduced fraction.

**Answer:**

    S1=A,B idle=1 | S2=C,D idle=5 | S3=E idle=2 | S4=F idle=1 | S5=G idle=12 | S6=H idle=3 | S7=I idle=1 | S8=J idle=10 | S9=K idle=3 | S10=L idle=9 | balance_delay=47/170

