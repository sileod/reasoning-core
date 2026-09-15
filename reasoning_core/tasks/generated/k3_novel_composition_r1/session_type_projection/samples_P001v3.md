# Samples: session_type_projection (P001v3)

## Level 0

### Example 1

**Prompt**

Global multiparty session type over participants P0, P2:
  G = P2 ? d . P0 ! a . end
Project G onto the local behaviour of participant P0. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = P0 ! a
Decide whether L is exactly the projection of G onto P0, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

equal

### Example 2

**Prompt**

Global multiparty session type over participants P1:
  G = P1 ? d . P1 ! a . end
Project G onto the local behaviour of participant P1. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = (P1 ? d) . (P1 ! a)
Decide whether L is exactly the projection of G onto P1, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

equal

## Level 2

### Example 1

**Prompt**

Global multiparty session type over participants P0, P1, P2, P4:
  G = P1 ? m . P4 ? a . P0 ? m . P2 ! k . end
Project G onto the local behaviour of participant P0. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = P0 ? m
Decide whether L is exactly the projection of G onto P0, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

equal

### Example 2

**Prompt**

Global multiparty session type over participants P1, P3, P4:
  G = P1 ? d . P3 ! a . P3 ! k . P4 ? m . end
Project G onto the local behaviour of participant P3. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = (P3 ! a) . (P3 ! k)
Decide whether L is exactly the projection of G onto P3, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

equal

## Level 5

### Example 1

**Prompt**

Global multiparty session type over participants P1, P3, P4, P6:
  G = P6 ! m . P1 ? d . P4 ? d . P4 ! k . P1 ? a . P1 ! d . P3 ? k . end
Project G onto the local behaviour of participant P3. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = P3 ! k
Decide whether L is exactly the projection of G onto P3, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

not

### Example 2

**Prompt**

Global multiparty session type over participants P2, P3, P4, P6, P7:
  G = P4 ! a . P6 ! k . P4 ? d . P2 ! a . P3 ! a . P7 ? m . P7 ? d . end
Project G onto the local behaviour of participant P2. In a global type a node 'A ! m' means A sends message m (A projects to a send, others skip it); 'B ? m' means B receives message m (B projects to a receive, others skip it). Sequence 'T1 . T2' projects to the sequential composition of the projections (empty parts dropped). Recursion 'mu X. B' where the participant occurs in B projects to 'mu X. Bproj', else it is dropped. The claimed local type is:
  L = P2 ! a
Decide whether L is exactly the projection of G onto P2, as computed by these rules. Reply with the single token 'equal' when they coincide and the single token 'not' when they differ.

**Answer**

equal
