# Level 0

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 2): -3x^2 - x - 5/2; on (2, inf): -2x^2 + 6x + 1. Compute the first distributional derivative f^(1) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 2): -6x - 1; (2, inf): -4x + 6; DELTAS: 43/2*delta(x-2)
```

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 1): 3/2; on (1, inf): 3. Compute the first distributional derivative f^(1) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 1): 0; (1, inf): 0; DELTAS: 3/2*delta(x-1)
```

# Level 2

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 0): -(3/2)x^3 + x^2 - 4x + 6; on (0, 3/2): -3x^3 - 5x^2 - 6x + 6; on (3/2, inf): 6x^2 + 3x + 1. Compute the second distributional derivative f^(2) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 0): -9x + 2; (0, 3/2): -18x - 10; (3/2, inf): 12; DELTAS: -2*delta(x-0) + 249/4*delta(x-3/2) + 347/8*delta'(x-3/2)
```

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 1): -(5/2)x^3 - x^2 + (5/2)x; on (1, 4): -(1/2)x^3 + x^2 + (5/2)x - 3; on (4, inf): 4x^3 + x^2 - 6x + 2. Compute the second distributional derivative f^(2) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 1): -15x - 2; (1, 4): -3x + 2; (4, inf): 24x + 2; DELTAS: 10*delta(x-1) + 1*delta'(x-1) + 415/2*delta(x-4) + 259*delta'(x-4)
```

# Level 5

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 1): -3x + 4; on (1, 3): (3/2)x^2 + 5; on (3, inf): -(4/3)x^2 - 6x - 5. Compute the third distributional derivative f^(3) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 1): 0; (1, 3): 0; (3, inf): 0; DELTAS: 3*delta(x-1) + 12*delta'(x-1) + 11/2*delta''(x-1) - 17/3*delta(x-3) - 46*delta'(x-3) - 107/2*delta''(x-3)
```

Prompt:

```
Let f be the piecewise polynomial function (a distribution) on the real line defined as follows: on (-inf, 1): (5/3)x^3 - 3x^2 + (5/3)x + 3; on (1, 2): -(5/2)x^3 + x^2 + 1; on (2, inf): 3x^3 - (5/2)x^2 - (3/2)x - 5/2. Compute the third distributional derivative f^(3) as a distribution. Write the answer as a canonical sum: first the piecewise polynomial part, with the polynomial on each interval in reduced form (e.g. '(-inf, 2/3): 2x^2 - 3x + 1/2'), the intervals separated by '; ', and then, if any, the weighted Dirac delta terms at the breakpoints, after 'DELTAS: ', each as weight*delta(x-b), weight*delta'(x-b) for the first derivative of the delta, delta'' for the second, and so on, the terms joined with ' + ', all weights as reduced fractions and breakpoints as rationals.
```

Answer:

```
(-inf, 1): 10; (1, 2): -15; (2, inf): 18; DELTAS: -17*delta(x-1) - 37/3*delta'(x-1) - 23/6*delta''(x-1) + 59*delta(x-2) + 101*delta'(x-2) + 47/2*delta''(x-2)
```

