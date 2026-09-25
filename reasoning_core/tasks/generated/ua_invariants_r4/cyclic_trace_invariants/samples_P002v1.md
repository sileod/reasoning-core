# samples P002v1: cyclic_trace_invariants

Each instance gives two matrix words over noncommuting real square matrices and asks
whether their traces are equal. '^T' transposes a factor, '^X' marks a skew-symmetric
factor M = -M^T. Use trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T).

## Level 0

### Example 1
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B:
word 1: B * A * A
word 2: A^T * A^T * B^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: yes

### Example 2
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B:
word 1: A^T * B^T * A
word 2: B^T * B^T * A^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: no

## Level 2

### Example 1
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B, C:
word 1: A * B^T * B^T * B * C^T
word 2: B * C^T * A * B^T * B^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: yes

### Example 2
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B, C:
word 1: A * B * B * B^T * C^T
word 2: C^T * A * B * B * B^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: yes

## Level 5

### Example 1
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B, C, D:
word 1: D * A^T * B^T * C^T * B^T * B * D * A
word 2: C^T * B^T * B * D * A * D * A^T * B^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: yes

### Example 2
Prompt:
```
Working with square matrices over the reals, where matrix multiplication is NOT commutative: XY generally differs from YX. A superscript X denotes a skew-symmetric factor M with M = -M^T, and a superscript T denotes the matrix transpose. Two standard laws hold for any matrices M and N: trace(MN) = trace(NM) (cyclicity) and trace(M) = trace(M^T) (transpose invariance). Consider these two matrix words over the symbols A, B, C, D:
word 1: C * D * C * B * C * A^T * A * C
word 2: C^T * D^T * C^T * C^T * C^T * A^T * A^T * C^T
Are the traces of these two words equal? Answer exactly 'yes' or 'no'.
```
Answer: no
