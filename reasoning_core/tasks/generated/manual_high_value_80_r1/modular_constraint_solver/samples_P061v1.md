# Samples P061v1: modular_constraint_solver

Each instance gives a system of modular congruences and asks for the canonical ('R mod M') solution or 'inconsistent'.

## Level 0

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 0 mod 2
x = 5 mod 19
x = 7 mod 17

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `24 mod 646`

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 0 mod 4
x = 4 mod 8
x = 0 mod 6

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `12 mod 24`

## Level 2

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 6 mod 15
x = 6 mod 33
x = 0 mod 6
x = 6 mod 30
x = 18 mod 27

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `666 mod 2970`

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 5 mod 29
x = 2 mod 13
x = 32 mod 40
x = 5 mod 8
x = 22 mod 31

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `inconsistent`

## Level 5

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 36 mod 80
x = 26 mod 38
x = 77 mod 84
x = 24 mod 37
x = 6 mod 64
x = 7 mod 49
x = 15 mod 88
x = 0 mod 2

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `inconsistent`

**Example**

**Prompt:**

```
We are solving for an integer x that must satisfy every congruence below simultaneously. Each line 'x = a mod m' means x leaves remainder a when divided by m (that is, x = a + k*m for some integer k). The moduli need not be pairwise coprime, so combine them with the generalized Chinese Remainder Theorem: the system is consistent iff for every overlapping modulus pair the residues agree modulo their greatest common divisor, and then the full solution set is a single residue class modulo the least common multiple of all the moduli.
Constraints:
x = 10 mod 19
x = 14 mod 60
x = 10 mod 19
x = 2 mod 78
x = 2 mod 52
x = 8 mod 34
x = 58 mod 64
x = 0 mod 2

If the system has no solution, answer with exactly: inconsistent
Otherwise answer with the canonical solution as 'R mod M', where R is the smallest non-negative integer satisfying the system and M is the least common multiple of all the moduli. For example, a system solved by x = 8 with modulus 12 is answered '8 mod 12'.
The answer is one line.
```

**Answer:** `314 mod 4031040`
