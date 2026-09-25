# Samples for periodic_density_equivalence (P004v1)

## Level 0

### Example 1

**Prompt:**
```
On a ring of 5 sites there are two periodic integer fields:
  u = [-2, -1, -2, 2, 0]
  v = [1, -1, 2, 3, 3]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 5. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
-1*v[+1] + 8*u[+2] + -1*u[+3]

Expression B has monomials:
-1*u[+2] + 8*u[+1] + -1*v[+0]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** EQ

### Example 2

**Prompt:**
```
On a ring of 5 sites there are two periodic integer fields:
  u = [3, 1, -1, -3, -3]
  v = [-3, -3, 0, 1, -3]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 5. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
4*v[+0] + 8*u[+2] + -3*v[+3]

Expression B has monomials:
8*u[+3] + -5*v[+1] + -3*v[+3]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** NEQ

## Level 2

### Example 1

**Prompt:**
```
On a ring of 7 sites there are two periodic integer fields:
  u = [0, 5, -2, 3, 3, 0, -3]
  v = [-2, -3, 0, 2, 2, 4, 5]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 7. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
8*v[-1] + 8*v[-3] + -7*u[-1] + -7*v[+2] + 4*v[-3]

Expression B has monomials:
-7*u[+2] + -7*v[+5] + 4*v[+0] + 8*v[+0] + 8*v[+2]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** EQ

### Example 2

**Prompt:**
```
On a ring of 7 sites there are two periodic integer fields:
  u = [0, 0, 2, -2, -1, 2, 1]
  v = [3, 2, -4, -5, -2, 2, -1]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 7. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
-1*u[-3]*u[-3] + 8*u[+2]*u[-2] + -3*u[+1] + 2*v[-2]*v[+1] + -3*u[+0]

Expression B has monomials:
8*u[+5]*u[+1] + -3*u[-1] + -3*u[+4] + -1*v[+0]*v[+3] + -1*u[-1]*u[-1]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** NEQ

## Level 5

### Example 1

**Prompt:**
```
On a ring of 10 sites there are two periodic integer fields:
  u = [1, 8, 3, 1, -1, -1, 5, 3, -8, -7]
  v = [-8, 4, 2, -3, 7, 3, 7, 4, 7, -7]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 10. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
6*v[-2] + 2*v[+2]*v[-2] + -7*v[+9]*u[+2] + 8*v[-2]*u[-2]*u[+8] + -5*v[+5]*v[+10] + -5*v[+3]*u[+11]*u[+3] + -1*u[+8]*u[+12]*u[+3] + -5*u[+12]*u[+1]

Expression B has monomials:
6*v[-4] + 2*v[+0]*v[-4] + -5*v[+1]*u[+9]*u[+1] + -7*v[+7]*u[+0] + -5*u[+10]*u[-1] + -5*v[+3]*v[+8] + 8*v[-4]*u[-4]*u[+6] + -1*u[+6]*u[+10]*u[+1]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** EQ

### Example 2

**Prompt:**
```
On a ring of 10 sites there are two periodic integer fields:
  u = [0, 0, 0, -4, 3, -3, -8, -4, -8, 8]
  v = [1, -2, 4, -4, 8, -6, -4, 8, -7, -5]
A local energy density at a site i is a sum of monomials. Each monomial like c*u[a]*v[b] means coefficient c times field u read at site i+a times field v read at site i+b; a single-field monomial like c*u[a] uses only that field. Indices wrap modulo 10. The total energy of an expression is the sum of its density over every site i.

Expression A has monomials:
-1*u[+2]*u[+5] + -1*u[+7] + 4*u[-1]*u[+6]*v[+6] + 8*v[-2]*v[+2] + -1*u[+1]*u[+9]*u[+1] + -5*u[+10]*v[+4]*v[+0] + 2*v[-5] + -7*v[+3]

Expression B has monomials:
2*v[-3] + -7*v[-3] + 4*u[+0]*u[+7]*v[+7] + 2*u[+9] + 8*v[-3]*v[+1] + -5*u[+9]*v[+3]*v[-1] + -1*u[+1]*u[+9]*u[+1] + -1*u[+3]*u[+6]

Decide whether the total energy of A equals that of B. Respond with the single token EQ or NEQ only.
```

**Answer:** NEQ
