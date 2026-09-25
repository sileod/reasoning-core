# Samples for stoichiometric_bootstrap_planning (P005v2)

## Level 0

### Example 1

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 2): consumes raw x1; produces T x1, W x1
  Re (cost 1): consumes nothing; produces T x2
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Ra0 (cost 1): consumes nothing; produces B x1, T x2
There are 6 species. Waste produced in total (1 max per waste species). Loan: B x2 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 1, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 1 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Rex1
```

### Example 2

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 2): consumes raw x1; produces T x1, W x1
  Re (cost 1): consumes nothing; produces T x1
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Ra0 (cost 1): consumes nothing; produces I0 x1
There are 6 species. Waste produced in total (1 max per waste species). Loan: B x2 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 1, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 1 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Rex1
```

## Level 2

### Example 1

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 4): consumes raw x1; produces T x1, W x1
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Ra0 (cost 1): consumes W x2; produces T x1
There are 6 species. Waste produced in total (3 max per waste species). Loan: B x2 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 3, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 3 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Ra0x3
```

### Example 2

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 2): consumes raw x1; produces T x1, W x1
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Ra0 (cost 1): consumes B x1, C x1, W x2; produces T x1
There are 6 species. Waste produced in total (3 max per waste species). Loan: B x2 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 3, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 3 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Rdx3
```

## Level 5

### Example 1

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  I1: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 2): consumes raw x1; produces T x1, W x1
  Re (cost 1): consumes nothing; produces T x1
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Rg1 (cost 1): consumes I0 x2; produces I1 x3
  Ra0 (cost 3): consumes B x1, raw x1; produces I1 x2
  Ra1 (cost 1): consumes B x1, I1 x1, W x1; produces B x1, T x2
There are 7 species. Waste produced in total (6 max per waste species). Loan: B x3 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 5, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 6 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Ra1x3,Rg0x1,Rg1x1
```

### Example 2

Prompt:

```
You are planning a chemical synthesis. Species and their roles:
  raw: unlimited raw material
  T: target product
  I0: intermediate (must end at zero)
  I1: intermediate (must end at zero)
  C: reusable catalyst (must end at zero)
  B: borrowed species (must be restored)
  W: waste byproduct
Available reactions (coefficient entries mean that many molecules):
  Rd (cost 3): consumes raw x1; produces T x1, W x1
  Re (cost 1): consumes B x1; produces T x2
  Rb (cost 1): consumes raw x1; produces B x1
  Rg0 (cost 1): consumes raw x1; produces I0 x2
  Rg1 (cost 1): consumes I0 x1; produces I1 x2
  Ra0 (cost 2): consumes B x1; produces B x1, I0 x2
  Ra1 (cost 3): consumes raw x1; produces I0 x2
There are 7 species. Waste produced in total (6 max per waste species). Loan: B x3 borrowed.
Fire reactions (reaction name followed by the number of times, e.g. R3x2) so that the target T reaches at least 5, every intermediate, catalyst and borrowed species ends back at zero, and no waste species exceeds 6 produced. Minimize the total cost (sum of firing costs). Output the least-cost firing plan as a comma-separated sorted-by-name list of only non-zero firings, e.g. R1x2,R3x1,R2x4.
```

Answer:

```
Rbx3,Rex3
```
