## Level 0

**Prompt:**

A while loop over state variables {x0, x1}, initialized to (3, 1). Each iteration updates every x_i to x_i + 1. The loop continues while 2*x0-2*x1+4 <= 0.

Candidate loop invariant: x0-x1-2 <= 0.
Postcondition: x0-x1+1 == 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

-8;6

**Prompt:**

A while loop over state variables {x0, x1}, initialized to (0, 1). Each iteration updates every x_i to x_i + 1. The loop continues while 2*x0+2*x1-4 == 0.

Candidate loop invariant: x0-2*x1+1 <= 0.
Postcondition: -x0+2*x1-1 == 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

-3;5

## Level 2

**Prompt:**

A while loop over state variables {x0, x1, x2}, initialized to (0, 0, 0). Each iteration updates every x_i to x_i + 1. The loop continues while 2*x0 == 0.

Candidate loop invariant: 2*x0-x1-x2-6 <= 0.
Postcondition: -2*x0-x1-2*x2-4 == 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1, x2 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

0;11;-10

**Prompt:**

A while loop over state variables {x0, x1, x2}, initialized to (2, 3, 3). Each iteration updates every x_i to x_i + 1. The loop continues while -x0+x1+2*x2-2 <= 0.

Candidate loop invariant: x0-2*x1-2*x2+3 <= 0.
Postcondition: -2*x0-x1+6 <= 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1, x2 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

-6;11;-8

## Level 5

**Prompt:**

A while loop over state variables {x0, x1, x2, x3}, initialized to (3, 2, 3, 0). Each iteration updates every x_i to x_i + 1. The loop continues while -x0-2*x2+2*x3-5 == 0.

Candidate loop invariant: -x0+x1-x2-9 <= 0.
Postcondition: x0+x1+x3+6 == 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1, x2, x3 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

-1;-3;7;9

**Prompt:**

A while loop over state variables {x0, x1, x2, x3}, initialized to (0, 2, 0, 3). Each iteration updates every x_i to x_i + 1. The loop continues while -2*x0-x1+x2+x3-8 <= 0.

Candidate loop invariant: -2*x0+2*x1-x2-4 <= 0.
Postcondition: -x0-2*x1-2*x2+x3+1 <= 0.

Is the candidate invariant inductive (true initially and preserved by each iteration) and, together with the loop condition, does it imply the postcondition? Answer exactly 'valid' if yes, or give one violating state as comma-separated x0, x1, x2, x3 values that satisfies the invariant and the loop condition but violates the postcondition.

**Answer:**

14;-3;-10;-3

