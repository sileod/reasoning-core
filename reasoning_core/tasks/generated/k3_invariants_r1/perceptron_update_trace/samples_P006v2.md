# Perceptron update trace (P006v2) samples

Fixed seed 1705404348; two examples per requested level.

## Level 0

### Example 1

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 3 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [0, -2], label 1
    example 1: features [1, -2], label 1
    example 2: features [2, 0], label 1
    example 3: features [1, -1], label 1
    
    Answer as a single integer.

Answer:

    -1

### Example 2

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 3 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [2, 0], label 1
    example 1: features [-2, -2], label 1
    example 2: features [2, 1], label 1
    example 3: features [-1, -2], label -1
    
    Answer as a single integer.

Answer:

    1

## Level 2

### Example 1

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 5 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [2, -3, -2], label 1
    example 1: features [2, 0, -3], label -1
    example 2: features [0, -2, -3], label 1
    example 3: features [1, 2, 1], label -1
    example 4: features [-2, 2, -2], label 1
    example 5: features [-2, 0, -1], label -1
    
    Answer as a single integer.

Answer:

    5

### Example 2

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 5 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [-1, -1, 2], label 1
    example 1: features [0, 3, -2], label -1
    example 2: features [-2, 2, 0], label -1
    example 3: features [-1, -3, 2], label 1
    example 4: features [3, -3, 0], label 1
    example 5: features [2, -2, -1], label -1
    
    Answer as a single integer.

Answer:

    2

## Level 5

### Example 1

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 8 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [-1, -2, 0, 4], label -1
    example 1: features [2, 3, 4, 1], label 1
    example 2: features [-3, -3, -1, 2], label -1
    example 3: features [4, -1, 0, 3], label 1
    example 4: features [2, -1, -4, 1], label -1
    example 5: features [-4, -1, 4, 3], label -1
    example 6: features [-4, 4, 2, 0], label -1
    example 7: features [0, -4, 1, 0], label 1
    example 8: features [2, 0, 2, 0], label -1
    
    Answer as a single integer.

Answer:

    8

### Example 2

Prompt:

    Run the standard perceptron algorithm on the following ordered integer feature-label pairs. Initialize the weights to the zero vector (no bias). In each epoch scan the examples in the order shown; for (x, y) it is a mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at most 8 epochs, stopping early if an entire epoch makes zero mistakes. Report the 0-based index of the FIRST example that causes a mistake in the final epoch that is run, or -1 if that final epoch has no mistakes (the algorithm converged). For example, if the first mistake in the final epoch is the example at index 2, answer 2.
    
    example 0: features [4, 2, 1, 4], label -1
    example 1: features [0, -1, 2, -2], label 1
    example 2: features [3, 0, 3, 4], label -1
    example 3: features [-2, 3, 2, 1], label 1
    example 4: features [4, 3, 0, 0], label -1
    example 5: features [3, 0, 1, -2], label 1
    example 6: features [1, -2, 2, -2], label -1
    example 7: features [-1, -2, 3, 4], label 1
    example 8: features [-4, 3, -3, 0], label 1
    
    Answer as a single integer.

Answer:

    5

