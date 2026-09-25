## Level 0

We evolve a cluster seed with symbolic frozen variables.
There are 3 mutable variables x0, x1, x2 and frozen variables f0, f1.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 -1 -1
  1 0 1
  1 -1 0
  0 1 1
  0 0 0
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 0
  mutate the seed at mutable index 1
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 0.

Answer
(x1*x2 + 1)/x0

---

We evolve a cluster seed with symbolic frozen variables.
There are 3 mutable variables x0, x1, x2 and frozen variables f0, f1.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 1 1
  -1 0 1
  -1 -1 0
  0 1 0
  0 1 1
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 0
  mutate the seed at mutable index 1
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 0.

Answer
(x1*x2 + 1)/x0

---

## Level 2

We evolve a cluster seed with symbolic frozen variables.
There are 4 mutable variables x0, x1, x2, x3 and frozen variables g_103, f1.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 -1 -1 -1
  1 0 -1 1
  1 1 0 1
  1 -1 -1 0
  1 0 1 1
  1 0 1 0
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 0
  mutate the seed at mutable index 2
  mutate the seed at mutable index 1
  rename frozen variable f0 to g_103
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 0.

Answer
(f1*g_103*x1*x2*x3 + 1)/x0

---

We evolve a cluster seed with symbolic frozen variables.
There are 4 mutable variables x0, x1, x2, x3 and frozen variables f0, g_103.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 -1 1 -1
  1 0 1 1
  -1 -1 0 1
  1 -1 -1 0
  1 0 1 0
  0 1 1 0
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 1
  mutate the seed at mutable index 0
  mutate the seed at mutable index 1
  rename frozen variable f1 to g_103
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 0.

Answer
(f0*g_103*x1*x3 + g_103*x2 + x0*x2**2*x3)/(x0*x1)

---

## Level 5

We evolve a cluster seed with symbolic frozen variables.
There are 4 mutable variables x0, x1, x2, x3 and frozen variables f0, f1, g_104.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 -2 1 2
  2 0 2 2
  -1 -2 0 2
  -2 -2 -2 0
  2 1 0 1
  2 1 2 0
  0 1 0 0
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 3
  mutate the seed at mutable index 1
  mutate the seed at mutable index 2
  relabel the mutable variables so that new index j holds the variable that was at old index 1, 3, 0, 2
  rename frozen variable f2 to g_104
  relabel the mutable variables so that new index j holds the variable that was at old index 3, 0, 1, 2
  relabel the mutable variables so that new index j holds the variable that was at old index 2, 0, 1, 3
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 2.

Answer
(f0**3*f1*g_104*x0**4*x1**4*x2**4 + 2*f0**2*f1*g_104*x0**2*x1**2*x2**2 + f0*f1*g_104 + x0**2*x2**2*x3**2)/(x1*x3**2)

---

We evolve a cluster seed with symbolic frozen variables.
There are 4 mutable variables x0, x1, x2, x3 and frozen variables g_103, g_105, f2.
The initial extended exchange matrix B (rows: mutable x's then frozen variables; columns: the mutable x's) is:
  0 1 -2 2
  -1 0 -1 1
  2 1 0 1
  -2 -1 -1 0
  0 0 0 2
  2 0 1 0
  2 0 2 0
Initially each mutable variable x_i equals its own symbol x_i.
Apply these seed-evolution operations in order:
  mutate the seed at mutable index 1
  mutate the seed at mutable index 3
  mutate the seed at mutable index 2
  rename frozen variable f0 to g_103
  relabel the mutable variables so that new index j holds the variable that was at old index 0, 3, 2, 1
  rename frozen variable f1 to g_105
  relabel the mutable variables so that new index j holds the variable that was at old index 0, 3, 1, 2
After all operations, report the rational expression (in the stated symbols, fully cancelled and with canonical rational coefficients) of the mutable cluster variable at current index 2.

Answer
(g_103**2*x0**3*x1*x2**2 + x0*x2 + x3)/(x1*x3)

---
