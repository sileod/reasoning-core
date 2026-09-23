# XOR Peeling Recovery Samples (P004v1)

## Level 0

### Level 0 example 1

**Prompt:**

There are 5 source symbols: s0, s1, s2, s3, s4.
There are 5 XOR checks, each an equation over some of the symbols:
  s2 = 1
  s3 = 1
  s1 XOR s2 = 1
  s4 = 1
  s2 = 0
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s2 s1 s3 s4

### Level 0 example 2

**Prompt:**

There are 5 source symbols: s0, s1, s2, s3, s4.
There are 5 XOR checks, each an equation over some of the symbols:
  s0 XOR s2 = 1
  s0 XOR s4 = 0
  s0 = 1
  s0 XOR s2 = 0
  s4 = 0
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s0 s2 s4

## Level 2

### Level 2 example 1

**Prompt:**

There are 7 source symbols: s0, s1, s2, s3, s4, s5, s6.
There are 9 XOR checks, each an equation over some of the symbols:
  s0 XOR s3 XOR s6 = 1
  s1 = 1
  s2 XOR s3 = 1
  s0 XOR s1 XOR s2 = 1
  s1 = 0
  s2 XOR s5 = 1
  s0 XOR s2 XOR s5 = 1
  s0 = 1
  s0 XOR s4 = 1
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s0 s1 s2 s3 s4 s5 s6

### Level 2 example 2

**Prompt:**

There are 7 source symbols: s0, s1, s2, s3, s4, s5, s6.
There are 9 XOR checks, each an equation over some of the symbols:
  s1 XOR s4 XOR s6 = 1
  s1 = 0
  s1 = 0
  s1 XOR s6 = 0
  s2 XOR s3 XOR s5 = 1
  s3 XOR s4 = 1
  s0 XOR s6 = 1
  s5 XOR s6 = 0
  s1 XOR s4 XOR s5 = 0
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s1 s6 s0 s4 s3 s5 s2

## Level 5

### Level 5 example 1

**Prompt:**

There are 10 source symbols: s0, s1, s2, s3, s4, s5, s6, s7, s8, s9.
There are 15 XOR checks, each an equation over some of the symbols:
  s0 XOR s6 XOR s7 = 0
  s0 XOR s3 XOR s7 = 1
  s1 XOR s3 XOR s5 XOR s9 = 1
  s0 = 1
  s3 = 1
  s0 XOR s7 = 0
  s0 XOR s1 XOR s3 XOR s7 = 1
  s5 XOR s8 = 1
  s5 XOR s9 = 0
  s3 XOR s4 XOR s6 XOR s7 = 1
  s0 XOR s1 XOR s7 XOR s8 = 0
  s4 XOR s7 = 0
  s1 XOR s3 XOR s6 XOR s9 = 0
  s2 XOR s8 = 0
  s9 = 0
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s0 s3 s7 s1 s4 s6 s8 s2 s5 s9

### Level 5 example 2

**Prompt:**

There are 10 source symbols: s0, s1, s2, s3, s4, s5, s6, s7, s8, s9.
There are 15 XOR checks, each an equation over some of the symbols:
  s3 = 1
  s4 = 1
  s0 XOR s1 = 1
  s2 XOR s6 = 0
  s2 XOR s6 XOR s8 XOR s9 = 0
  s3 XOR s5 XOR s6 = 0
  s4 XOR s5 XOR s6 = 0
  s3 XOR s4 XOR s8 = 1
  s5 XOR s6 = 1
  s9 = 1
  s9 = 0
  s6 = 0
  s2 XOR s5 XOR s7 = 0
  s0 XOR s6 XOR s7 XOR s9 = 0
  s6 = 1
Peeling: repeatedly, if a check mentions exactly one not-yet-recovered symbol, recover that symbol (assign it the check's value and remove it from every check). Stop when no check mentions exactly one unrecovered symbol. Whenever several symbols are peelable at once, recover the one with the smallest index first.
Give the recovery order: the symbols in the exact order they are recovered, separated by single spaces. Do not list any symbol that is never recovered. Format: s0 s3 s1

**Answer:**

s3 s4 s6 s2 s5 s7 s8 s9 s0 s1
