## Level 0
### Prompt
A population is modeled as a contact graph with nodes 0..5. Edges: 0 connected to 1, 2, 5; 1 connected to 0, 3, 4; 2 connected to 0, 5; 3 connected to 1, 4; 4 connected to 1, 3; 5 connected to 0, 2. On day 0 exactly these nodes are infectious: 1. An infectious node stays infectious for 2 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [0].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
6 3 1

### Prompt
A population is modeled as a contact graph with nodes 0..5. Edges: 0 connected to 3, 5; 1 connected to 2, 3; 2 connected to 1, 4; 3 connected to 0, 1, 4; 4 connected to 2, 3, 5; 5 connected to 0, 4. On day 0 exactly these nodes are infectious: 2. An infectious node stays infectious for 2 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [4].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
6 5 1


## Level 2
### Prompt
A population is modeled as a contact graph with nodes 0..9. Edges: 0 connected to 2, 5; 1 connected to 4, 9; 2 connected to 0, 5; 3 connected to 4, 7; 4 connected to 1, 3; 5 connected to 0, 2, 6; 6 connected to 5, 8; 7 connected to 3; 8 connected to 6, 9; 9 connected to 1, 8. On day 0 exactly these nodes are infectious: 0, 8. An infectious node stays infectious for 2 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [2, 5].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
10 8 1

### Prompt
A population is modeled as a contact graph with nodes 0..9. Edges: 0 connected to 2, 3, 8; 1 connected to 2, 3, 4, 7, 9; 2 connected to 0, 1, 9; 3 connected to 0, 1; 4 connected to 1, 6, 9; 5 connected to 7, 8; 6 connected to 4; 7 connected to 1, 5, 9; 8 connected to 0, 5; 9 connected to 1, 2, 4, 7. On day 0 exactly these nodes are infectious: 4, 5. An infectious node stays infectious for 2 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [3, 8].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
10 8 1


## Level 5
### Prompt
A population is modeled as a contact graph with nodes 0..15. Edges: 0 connected to 2, 4; 1 connected to 6, 9, 13; 2 connected to 0, 10; 3 connected to 4, 14; 4 connected to 0, 3, 7; 5 connected to 11, 13, 15; 6 connected to 1, 15; 7 connected to 4, 12, 14; 8 connected to 9, 15; 9 connected to 1, 8; 10 connected to 2, 13; 11 connected to 5, 12; 12 connected to 7, 11; 13 connected to 1, 5, 10; 14 connected to 3, 7; 15 connected to 5, 6, 8. On day 0 exactly these nodes are infectious: 4, 5, 10. An infectious node stays infectious for 4 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [9, 12, 14].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
16 13 2

### Prompt
A population is modeled as a contact graph with nodes 0..15. Edges: 0 connected to 1, 12; 1 connected to 0; 2 connected to 10, 11; 3 connected to 4, 13; 4 connected to 3, 14; 5 connected to 6, 11; 6 connected to 5, 7; 7 connected to 6, 15; 8 connected to 9, 12; 9 connected to 8, 13; 10 connected to 2, 14; 11 connected to 2, 5; 12 connected to 0, 8; 13 connected to 3, 9; 14 connected to 4, 10; 15 connected to 7. On day 0 exactly these nodes are infectious: 3, 4, 9. An infectious node stays infectious for 4 consecutive days, then becomes immune. On each day, every susceptible, non-immune node that has at least one currently-infectious neighbor becomes infectious the following day.
Run this SIR process twice from the same day-0 infections. In run A, immunize no one. In run B, before day 0, permanently remove (immunize) these nodes so they can never be infected: [1, 11, 15].
Give three integers separated by spaces: the total number of distinct nodes ever infected in run A, then the same total for run B, then the smallest day index t>=0 at which run A's and run B's currently-infectious node sets first differ (day 0 is the seed day). Format example: '5 3 2'.

### Answer
16 10 4

