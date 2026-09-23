# Samples P003v1

## Level 0

### Example 1

**Prompt:**

> There are 5 candidates numbered 0 to 4.
> In pairwise majority elections: 0 beats 2 by margin 1; 1 beats 0 by margin 1; 1 beats 2 by margin 1; 1 beats 3 by margin 1; 3 beats 0 by margin 1; 3 beats 2 by margin 1; 4 beats 0 by margin 1; 4 beats 1 by margin 1; 4 beats 2 by margin 1; 4 beats 3 by margin 1.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Give the Smith set's members as a comma-separated list sorted ascending, e.g. 1,4,5.

**Answer:**

`4`

### Example 2

**Prompt:**

> There are 5 candidates numbered 0 to 4.
> In pairwise majority elections: 1 beats 0 by margin 1; 1 beats 2 by margin 1; 1 beats 3 by margin 1; 1 beats 4 by margin 1; 2 beats 0 by margin 1; 2 beats 3 by margin 1; 2 beats 4 by margin 1; 3 beats 0 by margin 1; 3 beats 4 by margin 1; 4 beats 0 by margin 1.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Give the Smith set's members as a comma-separated list sorted ascending, e.g. 1,4,5.

**Answer:**

`1`


## Level 2

### Example 1

**Prompt:**

> There are 7 candidates numbered 0 to 6.
> In pairwise majority elections: 0 beats 3 by margin 2; 0 beats 4 by margin 2; 0 beats 6 by margin 1; 1 beats 0 by margin 1; 1 beats 2 by margin 1; 1 beats 4 by margin 2; 2 beats 0 by margin 3; 2 beats 3 by margin 1; 2 beats 4 by margin 1; 2 beats 5 by margin 3; 3 beats 1 by margin 3; 3 beats 6 by margin 2; 4 beats 3 by margin 2; 4 beats 6 by margin 2; 5 beats 0 by margin 3; 5 beats 1 by margin 1; 5 beats 3 by margin 3; 5 beats 4 by margin 1; 6 beats 1 by margin 3; 6 beats 2 by margin 3; 6 beats 5 by margin 1.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Give the Smith set's members as a comma-separated list sorted ascending, e.g. 1,4,5.

**Answer:**

`0,1,2,3,4,5,6`

### Example 2

**Prompt:**

> There are 7 candidates numbered 0 to 6.
> In pairwise majority elections: 0 beats 1 by margin 2; 0 beats 2 by margin 2; 0 beats 3 by margin 3; 0 beats 5 by margin 3; 1 beats 3 by margin 2; 2 beats 1 by margin 2; 2 beats 5 by margin 3; 3 beats 2 by margin 1; 3 beats 6 by margin 3; 4 beats 0 by margin 2; 4 beats 1 by margin 2; 4 beats 2 by margin 2; 4 beats 3 by margin 1; 4 beats 5 by margin 3; 4 beats 6 by margin 1; 5 beats 1 by margin 3; 5 beats 3 by margin 1; 6 beats 0 by margin 3; 6 beats 1 by margin 2; 6 beats 2 by margin 3; 6 beats 5 by margin 3.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Give the Smith set's members as a comma-separated list sorted ascending, e.g. 1,4,5.

**Answer:**

`4`


## Level 5

### Example 1

**Prompt:**

> There are 9 candidates numbered 0 to 8.
> In pairwise majority elections: 0 beats 4 by margin 1; 0 beats 6 by margin 5; 1 beats 0 by margin 4; 1 beats 2 by margin 1; 1 beats 4 by margin 6; 1 beats 8 by margin 5; 2 beats 0 by margin 2; 2 beats 3 by margin 3; 2 beats 4 by margin 3; 2 beats 7 by margin 6; 2 beats 8 by margin 1; 3 beats 0 by margin 6; 3 beats 1 by margin 5; 3 beats 4 by margin 2; 3 beats 6 by margin 1; 3 beats 7 by margin 6; 3 beats 8 by margin 1; 4 beats 8 by margin 6; 5 beats 0 by margin 5; 5 beats 1 by margin 3; 5 beats 2 by margin 6; 5 beats 3 by margin 1; 5 beats 4 by margin 4; 5 beats 6 by margin 6; 5 beats 8 by margin 3; 6 beats 1 by margin 6; 6 beats 2 by margin 1; 6 beats 4 by margin 1; 7 beats 0 by margin 3; 7 beats 1 by margin 6; 7 beats 4 by margin 6; 7 beats 5 by margin 5; 7 beats 6 by margin 1; 8 beats 0 by margin 5; 8 beats 6 by margin 4; 8 beats 7 by margin 1.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Is candidate 4 in the Smith set? Answer 1 for yes, 0 for no.

**Answer:**

`1`

### Example 2

**Prompt:**

> There are 9 candidates numbered 0 to 8.
> In pairwise majority elections: 0 beats 1 by margin 3; 0 beats 6 by margin 6; 0 beats 7 by margin 3; 1 beats 4 by margin 1; 1 beats 5 by margin 1; 1 beats 6 by margin 4; 2 beats 0 by margin 4; 2 beats 1 by margin 5; 2 beats 3 by margin 6; 2 beats 5 by margin 2; 2 beats 8 by margin 6; 3 beats 0 by margin 3; 3 beats 1 by margin 5; 3 beats 4 by margin 5; 3 beats 5 by margin 6; 3 beats 7 by margin 4; 3 beats 8 by margin 2; 4 beats 0 by margin 3; 4 beats 2 by margin 3; 4 beats 7 by margin 4; 5 beats 0 by margin 2; 5 beats 4 by margin 4; 5 beats 6 by margin 2; 5 beats 8 by margin 6; 6 beats 2 by margin 2; 6 beats 3 by margin 6; 6 beats 4 by margin 5; 6 beats 7 by margin 2; 6 beats 8 by margin 2; 7 beats 1 by margin 6; 7 beats 2 by margin 5; 7 beats 5 by margin 5; 7 beats 8 by margin 2; 8 beats 0 by margin 3; 8 beats 1 by margin 4; 8 beats 4 by margin 3.
> The Smith set is the smallest set of candidates such that every candidate in the set defeats every candidate outside the set, tracing beat relations upward transitively.
> Is candidate 7 in the Smith set? Answer 1 for yes, 0 for no.

**Answer:**

`1`

