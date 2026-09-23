# Level 0
```
We work with formal power series over the rationals, truncated modulo x^3; only the coefficients at degrees 0..2 are kept.
F = [0, -1, 1] meaning F(x) = -1 x^1 + 1 x^2
G = [-1/2, -1/2, -1] meaning G(x) = -1/2 + -1/2 x^1 + -1 x^2
Compute the product F(x)*G(x) truncated to order 3.
Give the first 3 coefficients of the resulting series (degrees 0..2) as a comma-separated list, integers rendered without a denominator. Example of the format: '1, 2/3, -4, 0'.
```
Answer: 0, 1/2, 0

```
We work with formal power series over the rationals, truncated modulo x^3; only the coefficients at degrees 0..2 are kept.
F = [0, 1, -1] meaning F(x) = 1 x^1 + -1 x^2
F has zero constant term and linear coefficient nonzero. Compute the compositional inverse G with F(G(x)) = x, truncated to order 3, via reversion (Lagrange-style coefficient recurrence).
Give the first 3 coefficients of the resulting series (degrees 0..2) as a comma-separated list, integers rendered without a denominator. Example of the format: '1, 2/3, -4, 0'.
```
Answer: 0, 1, 1

# Level 2
```
We work with formal power series over the rationals, truncated modulo x^5; only the coefficients at degrees 0..4 are kept.
F = [0, 5/4, 3, -6, -5/2] meaning F(x) = 5/4 x^1 + 3 x^2 + -6 x^3 + -5/2 x^4
G = [0, -2, 2/3, 1, 3] meaning G(x) = -2 x^1 + 2/3 x^2 + 1 x^3 + 3 x^4
G has zero constant term. Compute the functional composition F(G(x)) truncated to order 5 by the recurrence on powers of G.
The result may have leading zero coefficients. Give the index k >= 0 of the first nonzero coefficient and its value, separated by a space. Example of the format: '2 3/4'. Work out the truncation (use the composition recurrence) and report the leading term.
```
Answer: 1 -5/2

```
We work with formal power series over the rationals, truncated modulo x^5; only the coefficients at degrees 0..4 are kept.
F = [-5/4, -1, -5/4, 1, 1/3] meaning F(x) = -5/4 + -1 x^1 + -5/4 x^2 + 1 x^3 + 1/3 x^4
G = [-2/3, -1/4, 1, -3, 1/2] meaning G(x) = -2/3 + -1/4 x^1 + 1 x^2 + -3 x^3 + 1/2 x^4
Compute the product F(x)*G(x) truncated to order 5.
The result may have leading zero coefficients. Give the index k >= 0 of the first nonzero coefficient and its value, separated by a space. Example of the format: '2 3/4'. Work out the truncation (use the coefficient convolution recurrence) and report the leading term.
```
Answer: 0 5/6

# Level 5
```
We work with formal power series over the rationals, truncated modulo x^7; only the coefficients at degrees 0..6 are kept.
F = [-3, 4, -4, -1/6, -11/4, 7/3, -2] meaning F(x) = -3 + 4 x^1 + -4 x^2 + -1/6 x^3 + -11/4 x^4 + 7/3 x^5 + -2 x^6
G = [0, -5, -5/2, 1, -12/7, 1/5, 3/7] meaning G(x) = -5 x^1 + -5/2 x^2 + 1 x^3 + -12/7 x^4 + 1/5 x^5 + 3/7 x^6
G has zero constant term. Compute the functional composition F(G(x)) truncated to order 7 by the recurrence on powers of G.
Give the first 7 coefficients of the resulting series (degrees 0..6) as a comma-separated list, integers rendered without a denominator. Example of the format: '1, 2/3, -4, 0'.
```
Answer: -3, -20, -110, -451/6, -23511/14, -9050003/840, -5678325/112

```
We work with formal power series over the rationals, truncated modulo x^7; only the coefficients at degrees 0..6 are kept.
F = [-1/6, 5/4, 1/2, -5/4, 5/4, -10/7, 4] meaning F(x) = -1/6 + 5/4 x^1 + 1/2 x^2 + -5/4 x^3 + 5/4 x^4 + -10/7 x^5 + 4 x^6
F has nonzero constant term. Compute the multiplicative inverse 1/F(x) truncated to order 7 by the series inversion recurrence.
Give the first 7 coefficients of the resulting series (degrees 0..6) as a comma-separated list, integers rendered without a denominator. Example of the format: '1, 2/3, -4, 0'.
```
Answer: -6, -45, -711/2, -11025/4, -171567/8, -18674055/112, -290435049/224

