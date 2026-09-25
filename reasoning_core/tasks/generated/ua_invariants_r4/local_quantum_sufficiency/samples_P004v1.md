## Level 0
### Example 1
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 2 qubits q0..q1 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1      (5/13|0>+12/13|1>)_{q0} (x) (4/5|0>+3/5|1>)_{q1}

Partially trace out every qubit except the subsystems whose indices are the query list [1], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

4/5|0>+3/5|1>

### Example 2
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 2 qubits q0..q1 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1/5    (5/13|0>+12/13|1>)_{q0} (x) (-3/5|0>+4/5|1>)_{q1}
p1=4/5    (3/5|0>+4/5|1>)_{q0} (x) (-5/13|0>+12/13|1>)_{q1}

Partially trace out every qubit except the subsystems whose indices are the query list [1], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

(00,00)=4021/21125;(00,01)=-8028/21125;(01,00)=-8028/21125;(01,01)=17104/21125

## Level 2
### Example 1
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 3 qubits q0..q2 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1      (-4/5|0>+3/5|1>)_{q0} (x) (-5/13|0>+-12/13|1>)_{q1} (x) (-3/5|0>+-4/5|1>)_{q2}

Partially trace out every qubit except the subsystems whose indices are the query list [1], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

-5/13|0>+-12/13|1>

### Example 2
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 3 qubits q0..q2 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1      (12/13|0>+5/13|1>)_{q0} (x) (-3/5|0>+4/5|1>)_{q1} (x) (-9/41|0>+40/41|1>)_{q2}

Partially trace out every qubit except the subsystems whose indices are the query list [2,0], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

-108/533|00>+-45/533|01>+480/533|10>+200/533|11>

## Level 5
### Example 1
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 4 qubits q0..q3 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1      (-3/5|0>+-4/5|1>)_{q0} (x) (3/5|0>+-4/5|1>)_{q1} (x) (3/5|0>+4/5|1>)_{q2} (x) (-11/61|0>+-60/61|1>)_{q3}

Partially trace out every qubit except the subsystems whose indices are the query list [2,3,0], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

99/1525|000>+132/1525|001>+108/305|010>+144/305|011>+132/1525|100>+176/1525|101>+144/305|110>+192/305|111>

### Example 2
**Prompt:**

A two-level system per qubit is described in the computational basis |0>,|1>. The joint state over 4 qubits q0..q3 is the following (already normalized) convex combination of product pure states, one term per line with its probability p_k and its tensor product of single-qubit states in the order q0,q1,...:
p0=1      (3/5|0>+4/5|1>)_{q0} (x) (3/5|0>+-4/5|1>)_{q1} (x) (-11/61|0>+-60/61|1>)_{q2} (x) (12/13|0>+5/13|1>)_{q3}

Partially trace out every qubit except the subsystems whose indices are the query list [1,3], kept in exactly that order, to obtain the reduced (marginal) state accessible to those subsystems. The reduced state is a density operator; when it is pure (rank one) give it as a ket string whose basis strings are ordered by the query index list and whose nonzero rational amplitudes appear sorted lexicographically by basis string, e.g. 3/5|00>+-4/5|11>; when it is mixed give the nonzero density-matrix entries as (row_basis,col_basis)=value, semicolon-separated and row-major over the same basis ordering, e.g. (00,00)=1/2;(00,11)=-1/2;(11,00)=-1/2;(11,11)=1/2. Fractions reduced and signs on the numerator. Give only that ket string or entry string, nothing else.

**Answer:**

36/65|00>+3/13|01>+-48/65|10>+-4/13|11>
