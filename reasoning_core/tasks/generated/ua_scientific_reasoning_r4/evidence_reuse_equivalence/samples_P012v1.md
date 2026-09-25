# Samples: evidence_reuse_equivalence (P012v1)

Each pair of derivations cites sentence identifiers from a fixed universe; the task asks whether their support sets coincide as sets of identifiers, answering yes or no.

## Level 0

### Example 1

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: D, B, B, D
Derivation 2 cites: D, B, B

**Answer**: yes

### Example 2

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: A, B, A
Derivation 2 cites: B, B, A

**Answer**: yes

## Level 2

### Example 1

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D, E, F}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: A, A, B, A, B, F, F, E, B, A, B, E, E, E
Derivation 2 cites: E, A, E, F, F, A, A, B, F

**Answer**: yes

### Example 2

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D, E, F}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: B, D, C, D, C, F, B, F, F, D, C, C, F
Derivation 2 cites: C, B, C, F, B, D, D, C

**Answer**: yes

## Level 5

### Example 1

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D, E, F, G, H, I}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: I, F, I, I, C, E, C, F, E, I, C, F, I, E, D, F, F, I, H, D, H, H, I, G, H, F, E
Derivation 2 cites: A, B, C, C, C, A, C, B, A, C, B, B, C, B, B, C

**Answer**: no

### Example 2

**Prompt**

The fixed universe of sentence identifiers is {A, B, C, D, E, F, G, H, I}. Two derivations each cite sentence premises from this universe. A premise may be cited more than once inside a derivation, but as an identifier it still names one sentence, so the support set of a derivation ignores how many times each identifier is cited and the order of citation. Do the two derivations draw on the same support set of sentence identifiers? Answer exactly yes or no.

Derivation 1 cites: I, H, I, A, F, I, F, I, A, H, G, G, H, C, F, E, A, G, C, I, E, H, I, H, C, C, H, G, H, G, G
Derivation 2 cites: H, I, A, E, E, C, C, F, I, C, E, C, E, G, C, H, F, E, H, E

**Answer**: yes
