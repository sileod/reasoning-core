## Level 0

**Example 1**

Prompt:
```
A monotone trigger network has sources A, B, C, D. Its gates are:
  Gate G1 over inputs (C, D) fires when at least 1 of its inputs fire.
  Gate G2 over inputs (A, C) fires when at least 2 of its inputs fire.
  Gate G3 over inputs (B, C) fires when at least 1 of its inputs fire.
The target T fires when at least 3 of G1, G2, G3 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: A,C.

One edit is applied to the network: Gate G3 over inputs (B, C) is switched to an AND gate (fires when all fire).

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: A,B,C; REMOVED: A,C
```

**Example 2**

Prompt:
```
A monotone trigger network has sources A, B, C, D. Its gates are:
  Gate G1 over inputs (B, C, D) fires when at least 2 of its inputs fire.
  Gate G2 over inputs (B, C) fires when at least 1 of its inputs fire.
  Gate G3 over inputs (B, C) fires when at least 1 of its inputs fire.
The target T fires when at least 2 of G1, G2, G3 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: B;C.

One edit is applied to the network: Gate G2 over inputs (B, C) is switched to an AND gate (fires when all fire).

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: B,C;B,D;C,D; REMOVED: B;C
```

## Level 2

**Example 1**

Prompt:
```
A monotone trigger network has sources A, B, C, D, E, F. Its gates are:
  Gate G1 over inputs (A, F) fires when at least 1 of its inputs fire.
  Gate G2 over inputs (A, D) fires when at least 2 of its inputs fire.
  Gate G3 over inputs (A, D) fires when at least 2 of its inputs fire.
  Gate G4 over inputs (D, F) fires when at least 2 of its inputs fire.
  Gate G5 over inputs (A, C) fires when at least 2 of its inputs fire.
The target T fires when at least 3 of G1, G2, G3, G4, G5 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: A,D.

One edit is applied to the network: The target T now fires when at least 5 of its inputs (G1, G2, G3, G4, G5) fire.

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: A,C,D,F; REMOVED: A,D
```

**Example 2**

Prompt:
```
A monotone trigger network has sources A, B, C, D, E, F. Its gates are:
  Gate G1 over inputs (A, D, E) fires when at least 1 of its inputs fire.
  Gate G2 over inputs (C, D, E) fires when at least 1 of its inputs fire.
  Gate G3 over inputs (C) fires when at least 1 of its inputs fire.
  Gate G4 over inputs (B, D, F) fires when at least 1 of its inputs fire.
  Gate G5 over inputs (D) fires when at least 1 of its inputs fire.
The target T fires when at least 4 of G1, G2, G3, G4, G5 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: A,B,C;A,C,F;B,C,E;C,E,F;D.

One edit is applied to the network: Gate G2 over inputs (C, D, E) is switched to an AND gate (fires when all fire).

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: C,D; REMOVED: A,B,C;A,C,F;B,C,E;C,E,F;D
```

## Level 5

**Example 1**

Prompt:
```
A monotone trigger network has sources A, B, C, D, E, F, G, H, I. Its gates are:
  Gate G1 over inputs (A, B, D) fires when at least 3 of its inputs fire.
  Gate G2 over inputs (A, B, G, H, I) fires when at least 2 of its inputs fire.
  Gate G3 over inputs (D, I) fires when at least 1 of its inputs fire.
  Gate G4 over inputs (A, C, E, H, I) fires when at least 5 of its inputs fire.
  Gate G5 over inputs (A, E, G, I) fires when at least 2 of its inputs fire.
  Gate G6 over inputs (B, E, G) fires when at least 1 of its inputs fire.
  Gate G7 over inputs (B, C, E, F, I) fires when at least 4 of its inputs fire.
  Gate G8 over inputs (B, E, F, G, I) fires when at least 5 of its inputs fire.
The target T fires when at least 7 of G1, G2, G3, G4, G5, G6, G7, G8 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: A,B,C,D,E,H,I;A,B,C,E,F,G,H,I;A,B,D,E,F,G,I.

One edit is applied to the network: The target T now fires when at least 1 of its inputs (G1, G2, G3, G4, G5, G6, G7, G8) fire.

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: A,H;B;D;E;G;I; REMOVED: A,B,C,D,E,H,I;A,B,C,E,F,G,H,I;A,B,D,E,F,G,I
```

**Example 2**

Prompt:
```
A monotone trigger network has sources A, B, C, D, E, F, G, H, I. Its gates are:
  Gate G1 over inputs (C, D, F) fires when at least 2 of its inputs fire.
  Gate G2 over inputs (B, D, E, F, G) fires when at least 4 of its inputs fire.
  Gate G3 over inputs (A, B, C, D, E, G) fires when at least 2 of its inputs fire.
  Gate G4 over inputs (D, E, F, I) fires when at least 4 of its inputs fire.
  Gate G5 over inputs (C, E, G) fires when at least 2 of its inputs fire.
  Gate G6 over inputs (A, G, I) fires when at least 1 of its inputs fire.
  Gate G7 over inputs (A, E, F, H) fires when at least 3 of its inputs fire.
  Gate G8 over inputs (C, F, H, I) fires when at least 3 of its inputs fire.
The target T fires when at least 2 of G1, G2, G3, G4, G5, G6, G7, G8 fire.

A minimal triggering set is an inclusion-minimal subset of sources whose activation makes the target fire. The currently known minimal triggering sets of T are: A,B;A,C;A,D;A,E;A,F,H;A,G;B,C,F;B,C,I;B,D,F;B,D,I;B,E,F,H;B,E,I;B,G;C,D;C,E;C,F,H;C,F,I;C,G;C,H,I;D,E,F;D,E,I;D,F,I;D,G;E,G;F,H,I.

One edit is applied to the network: The target T now fires when at least 3 of its inputs (G1, G2, G3, G4, G5, G6, G7, G8) fire.

After the edit, report the minimal triggering sets that were ADDED (newly minimal) and those that were REMOVED (no longer minimal). Combine witness sets from the target's inputs and absorb any set that became a superset of another. Write each minimal triggering set as a comma-separated sorted list of source labels, and the added and removed collections as label sets separated by semicolons, e.g. ADDED: A,B;D REMOVED: - (use - for an empty collection).
```

Answer:
```
ADDED: A,B,F,H;A,C,D;A,C,E;A,C,F;A,C,H,I;A,D,F;A,E,F;A,E,H;A,F,G,H;A,F,H,I;B,C,F,H;B,C,H,I;B,D,E,F;B,D,F,I;B,F,G,H,I;C,D,E;C,D,F,H;C,D,I;C,E,F;C,E,I;D,E,F,H;D,E,F,I;D,F,G;D,F,H,I;E,F,H,I; REMOVED: A,B;A,C;A,D;A,E;A,F,H;A,G;B,C,F;B,C,I;B,D,F;B,D,I;B,E,F,H;B,E,I;B,G;C,D;C,E;C,F,H;C,H,I;D,E,F;D,E,I;D,F,I;D,G;F,H,I
```
