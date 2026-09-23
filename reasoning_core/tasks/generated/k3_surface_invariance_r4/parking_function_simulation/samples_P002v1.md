# Parking Function Simulation v1 -- P002v1 samples

## Level 0

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 3 parking spaces numbered 0 to 2. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 2, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 1 0 2 1.
What is the position (1-indexed) of the first car that fails to find a spot, or the word none if every car parks? Answer with the required value only.

**Answer:**

1

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 4 parking spaces numbered 0 to 3. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 3, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 2 1.
What is the list of spaces that end up occupied, as a string of 1s (occupied) and 0s (free) of length 4? Answer with the required value only.

**Answer:**

0110

## Level 2

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 5 parking spaces numbered 0 to 4. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 4, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 1 1 2 0.
What is the list of spaces that end up occupied, as a string of 1s (occupied) and 0s (free) of length 5? Answer with the required value only.

**Answer:**

11110

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 9 parking spaces numbered 0 to 8. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 8, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 6 3 3 1 8 4 4 6 0 3.
What is whether every car can park, as the single word yes or no? Answer with the required value only.

**Answer:**

no

## Level 5

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 11 parking spaces numbered 0 to 10. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 10, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 2 6 4 5 9 3 5 1 3 5 8 3 3.
What is the total number of spaces moved past preferred spots summed over all cars that found a spot? Answer with the required value only.

**Answer:**

12

### Example

**Prompt:**

Cars arrive one at a time onto a one-way street with 15 parking spaces numbered 0 to 14. Each car states its preferred spot. A car parks at its preferred spot if it is free; otherwise it moves forward to the next free spot beyond (there is no backing up). After the car with preferred spot 14, a car that finds no free spot at or beyond its preference fails and does not park.
The cars arrive in this order with these preferred spots: 12 5 4 6 0 14 11 8 6 8 8 0 1 5 10 3 9 13 4.
What is the total number of spaces moved past preferred spots summed over all cars that found a spot? Answer with the required value only.

**Answer:**

14

