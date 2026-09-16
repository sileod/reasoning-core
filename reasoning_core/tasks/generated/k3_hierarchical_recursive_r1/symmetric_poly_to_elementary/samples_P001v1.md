## Level 0
### Example 1
**Prompt:**
```
The polynomial P in the variables x1, x2 is symmetric, where P = x1^5 + x2^5. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e2 (en is the product of all 2 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(5,0):1, (3,1):-5, (1,2):5]
```

### Example 2
**Prompt:**
```
The polynomial P in the variables x1, x2 is symmetric, where P = -x1^5 - x2^5. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e2 (en is the product of all 2 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(5,0):-1, (3,1):5, (1,2):-5]
```

## Level 2
### Example 1
**Prompt:**
```
The polynomial P in the variables x1, x2 is symmetric, where P = 2x1^6*x2 + 2x1*x2^6. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e2 (en is the product of all 2 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(5,1):2, (3,2):-10, (1,3):10]
```

### Example 2
**Prompt:**
```
The polynomial P in the variables x1, x2 is symmetric, where P = x1^5*x2^2 + 2x1^3 + x1^2*x2^5 + 2x2^3. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e2 (en is the product of all 2 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(3,2):1, (3,0):2, (1,3):-3, (1,1):-6]
```

## Level 5
### Example 1
**Prompt:**
```
The polynomial P in the variables x1, x2, x3 is symmetric, where P = x1^9*x2 + x1^9*x3 + x1^7*x2^3 + x1^7*x3^3 - 2x1^5*x2^2*x3 - 2x1^5*x2*x3^2 + x1^3*x2^7 + x1^3*x3^7 - 2x1^2*x2^5*x3 - 2x1^2*x2*x3^5 + x1*x2^9 - 2x1*x2^5*x3^2 - 2x1*x2^2*x3^5 + x1*x3^9 + x2^9*x3 + x2^7*x3^3 + x2^3*x3^7 + x2*x3^9. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e3 (en is the product of all 3 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(8,1,0):1, (7,0,1):-1, (6,2,0):-8, (5,1,1):12, (4,3,0):21, (4,0,2):-4, (3,2,1):-34, (3,1,1):-2, (2,4,0):-20, (2,1,2):9, (2,0,2):2, (1,3,1):29, (1,2,1):6, (1,0,3):4, (0,5,0):4, (0,2,2):-9, (0,1,2):-10]
```

### Example 2
**Prompt:**
```
The polynomial P in the variables x1, x2, x3 is symmetric, where P = -x1^7*x2^2*x3 - x1^7*x2*x3^2 + x1^3*x2 + x1^3*x3 - x1^2*x2^7*x3 - x1^2*x2*x3^7 + x1^2*x2 + x1^2*x3 - x1*x2^7*x3^2 + x1*x2^3 - x1*x2^2*x3^7 + x1*x2^2 + x1*x3^3 + x1*x3^2 + x2^3*x3 + x2^2*x3 + x2*x3^3 + x2*x3^2. Express P uniquely in the basis of elementary symmetric polynomials e1, ..., e3 (en is the product of all 3 variables). Output the expansion as a list of terms `(a1,...,an):coeff` meaning the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated by commas inside square brackets. Coefficients are integers or fractions like 3/4. Omit zero terms. For example, [ (1,0,...,0):5 ] means the polynomial equals 5*e1.
```
**Answer:**
```
[(5,1,1):-1, (4,0,2):1, (3,2,1):5, (2,1,2):-9, (2,1,0):1, (1,3,1):-5, (1,1,0):1, (1,0,3):4, (1,0,1):-1, (0,2,2):7, (0,2,0):-2, (0,0,1):-3]
```

