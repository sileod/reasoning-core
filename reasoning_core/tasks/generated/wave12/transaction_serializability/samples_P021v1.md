## Level 0
### Example 1
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T3, R, x3) (T1, R, x2) (T2, R, x3) (T1, W, x1) (T1, W, x1) (T1, R, x2) (T3, W, x2) (T3, R, x2)

There are 3 transactions T1..T3. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: T1,T2,T3

### Example 2
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T1, W, x1) (T3, W, x2) (T1, R, x3) (T3, W, x2) (T2, R, x2) (T3, R, x1) (T1, R, x1) (T2, W, x3)

There are 3 transactions T1..T3. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: T1,T3,T2


## Level 2
### Example 1
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T1, W, x3) (T5, W, x3) (T5, R, x1) (T5, W, x3) (T2, W, x2) (T4, W, x2) (T1, R, x1) (T4, R, x1) (T3, W, x2) (T3, R, x3) (T3, R, x2) (T3, W, x1)

There are 5 transactions T1..T5. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: T1,T2,T4,T5,T3

### Example 2
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T1, R, x3) (T4, W, x2) (T2, R, x3) (T1, R, x3) (T2, R, x3) (T5, W, x3) (T3, R, x3) (T4, W, x2) (T1, R, x1) (T4, W, x2) (T2, W, x1) (T3, R, x1)

There are 5 transactions T1..T5. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: T1,T2,T4,T5,T3


## Level 5
### Example 1
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T1, W, x1) (T1, R, x4) (T8, W, x3) (T4, R, x6) (T1, R, x2) (T6, W, x4) (T6, W, x3) (T8, R, x5) (T2, R, x1) (T2, W, x4) (T6, R, x2) (T4, R, x6) (T3, W, x6) (T6, W, x2) (T8, R, x5) (T5, W, x2) (T2, W, x1) (T2, R, x2)

There are 8 transactions T1..T8. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: T1,T4,T3,T7,T8,T6,T5,T2

### Example 2
A database executes the following interleaved transaction operations, where each is (T_i, A, V) meaning transaction T_i performs access A on variable V (A is R for read, W for write).
(T6, W, x2) (T8, W, x4) (T5, W, x6) (T1, R, x6) (T4, W, x6) (T1, W, x6) (T6, W, x6) (T7, R, x3) (T5, W, x3) (T8, W, x1) (T6, W, x1) (T6, R, x4) (T3, R, x5) (T3, W, x3) (T8, R, x3) (T6, R, x1) (T4, W, x6) (T2, R, x6)

There are 8 transactions T1..T8. Build the conflict-precedence relation (a conflict when two operations by different transactions on the same variable both write, or one writes and the other reads). The schedule is serializable iff this precedence graph has no cycle. If serializable, report the canonical serial order, which is the lexicographically smallest valid topological ordering. Otherwise report NONE.

Answer with 'NONE' (not serializable) or a comma-separated list such as 'T1,T2,T3'.
Answer: NONE


