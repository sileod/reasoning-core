# Level 0

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 5 ± 1
  B = 7 ± 2
  C = 9 ± 3

  n0 = multiply of C and B; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n1 = add of B and n0; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
What is the value of the final output n1? Give the number rounded to 3 decimal places.

### Answer

70.000

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 7 ± 2
  B = 3 ± 2
  C = 3 ± 3

  n0 = add of B and C; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n1 = divide of A and B; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
What is the half-width (absolute uncertainty) of the final output n1? Give the number rounded to 3 decimal places.

### Answer

2.222

# Level 2

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 4 ± 1
  B = 7 ± 3
  C = 3 ± 1
  D = 2 ± 1
  E = 3 ± 1

  n0 = add of C and A; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n1 = multiply of B and n0; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n2 = add of B and D; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n3 = divide of B and D; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
Which single input contributes the most to the uncertainty of the final output n3? Name it by its single letter.

### Answer

D

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 8 ± 3
  B = 5 ± 3
  C = 7 ± 1
  D = 6 ± 1
  E = 5 ± 1

  n0 = multiply of C and A; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n1 = add of B and n0; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n2 = multiply of A and E; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n3 = multiply of D and E; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
Which single input contributes the most to the uncertainty of the final output n3? Name it by its single letter.

### Answer

E

# Level 5

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 5 ± 2
  B = 2 ± 3
  C = 4 ± 2
  D = 2 ± 3
  E = 3 ± 1
  F = 5 ± 1
  G = 9 ± 3
  H = 2 ± 2

  n0 = divide of A and G; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n1 = divide of A and n0; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n2 = multiply of A and H; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n3 = divide of H and n0; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n4 = divide of n3 and D; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n5 = multiply of E and n4; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n6 = add of n2 and n1; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
What is the half-width (absolute uncertainty) of the final output n6? Give the number rounded to 3 decimal places.

### Answer

19.056

## Example

### Prompt

A measurement network combines several noisy readouts. Absolute uncertainties are given as half-widths of the intervals (value ± half-width). Each operator combines its two operands' uncertainties either by the worst-case linear rule (half-widths add) or by the root-sum-square rule (add squares, take the square root), depending on whether the two operands' noises are fully dependent or independent, as stated per step.

Inputs:
  A = 2 ± 1
  B = 5 ± 2
  C = 3 ± 1
  D = 3 ± 3
  E = 7 ± 2
  F = 8 ± 3
  G = 8 ± 2
  H = 7 ± 2

  n0 = add of H and F; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n1 = multiply of H and E; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n2 = multiply of H and A; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
  n3 = divide of G and n1; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n4 = multiply of H and D; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n5 = subtract of D and n3; these two operands' noises are independent, so combine their uncertainties by the root-sum-square rule, i.e. add the squares of the half-widths and take the square root.
  n6 = multiply of n4 and D; these two operands' noises are fully dependent, so combine their uncertainties by the worst-case linear rule, i.e. the half-widths add.
What is the half-width (absolute uncertainty) of the final output n6? Give the number rounded to 3 decimal places.

### Answer

128.521
