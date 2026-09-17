# Samples: stabilizer_tableau_simulation (P010v2)

## Level 0

### Example 1

Prompt:

A Clifford-circuit simulator stores 3 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: + 10 00 10; + 00 00 10; + 10 01 10
Apply gates left to right: S A; S A; S C; CNOT A C; S A; CNOT B C; H A; H B
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure X on qubit B, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 3 qubits in total.

Answer: 0

### Example 2

Prompt:

A Clifford-circuit simulator stores 3 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: - 11 01 11; + 11 10 01; + 10 10 11
Apply gates left to right: S A; H B; H C; H C; S B; CNOT B C; CNOT B C; H A; CNOT B A; CNOT C A; CNOT B A; S A
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure X on qubit C, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 3 qubits in total.

Answer: 1

## Level 2

### Example 1

Prompt:

A Clifford-circuit simulator stores 3 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: + 10 00 10; + 10 00 00; + 10 10 10
Apply gates left to right: H C; H B; CNOT B C; S B; S A; CNOT B A; CNOT B C; S B; S C; CNOT B A; H B; CNOT C A; S C; H A; S A; H C; CNOT C B; CNOT C A
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure X on qubit B, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 3 qubits in total.

Answer: 0

### Example 2

Prompt:

A Clifford-circuit simulator stores 3 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: - 00 11 00; - 01 00 10; - 00 00 10
Apply gates left to right: H A; S C; CNOT B C; H A; S B; H A; CNOT C B; S B; H B; CNOT B C; H A; H B; H A; H B; S A
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure Y on qubit A, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 3 qubits in total.

Answer: 0

## Level 5

### Example 1

Prompt:

A Clifford-circuit simulator stores 4 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C, D in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: + 11 10 01 11; - 11 10 00 00; - 01 01 01 11; - 01 01 00 11
Apply gates left to right: S C; S B; CNOT B C; S D; CNOT A C; S B; S D; H B; S C; H D; H A; S A; CNOT C D; CNOT C A; S A; CNOT A C; S B; S D; CNOT C A; S B; S A; S D; H D; CNOT A D; CNOT C D
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure Z on qubit A, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 4 qubits in total.

Answer: 0

### Example 2

Prompt:

A Clifford-circuit simulator stores 4 independent commuting stabilizer generators. The initial pure state is the simultaneous plus-one eigenstate of these signed rows. Columns are qubits A, B, C, D in that order. Each pair is xz: 00=I, 10=X, 01=Z, 11=Y; the leading sign multiplies the whole tensor product.
Initial rows: + 01 00 00 00; - 00 01 01 00; + 01 00 01 00; - 01 00 01 01
Apply gates left to right: CNOT B D; S B; CNOT A B; S D; CNOT D C; CNOT D C; S D; S B; H D; CNOT C A; H C; S C; H A; CNOT A D; H C; CNOT B D; S C; CNOT A D; H B; H C; CNOT C B; CNOT D C; H D; CNOT D A; H C; CNOT D C
H is Hadamard; S=diag(1,i); CNOT lists control then target. Use the Gottesman-Knill tableau algorithm, tracking signs: conjugate every generator by each gate, and multiply rows if needed to obtain the measured Pauli. Measure X on qubit B, with identity on every other qubit. This measurement is guaranteed deterministic. Report zero for eigenvalue plus one or one for eigenvalue minus one, as a single digit (format example: 0). Keep the column order above; there are 4 qubits in total.

Answer: 1
