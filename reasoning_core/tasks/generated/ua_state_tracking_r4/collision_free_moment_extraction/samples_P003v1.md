# Samples for collision_free_moment_extraction (P003v1)

## Level 0

### Example 1

**Prompt:**

A dataset of records, each holding 2 attributes named ['A', 'B'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = 3, P_B = 5, M_AB = -5. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^1 · B^1, that is the sum of x_A(r_1) * x_B(r_2) over all tuples (r_1, ..., r_2) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

20

### Example 2

**Prompt:**

A dataset of records, each holding 2 attributes named ['A', 'B'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = -5, P_B = 0, M_AB = 11. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^1 · B^1, that is the sum of x_A(r_1) * x_B(r_2) over all tuples (r_1, ..., r_2) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

-11

## Level 2

### Example 1

**Prompt:**

A dataset of records, each holding 3 attributes named ['A', 'B', 'C'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = 1, P_B = 84, P_C = 107, M_AB = -53, M_AC = 141, M_BC = 1403, M_ABC = 1197. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^1 · B^2 · C^2, that is the sum of x_A(r_1) * x_B(r_2) * x_C(r_3) over all tuples (r_1, ..., r_3) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

3806

### Example 2

**Prompt:**

A dataset of records, each holding 3 attributes named ['A', 'B', 'C'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = 1, P_B = 6, P_C = 59, M_AB = 7, M_AC = 93, M_BC = 79, M_ABC = 77. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^1 · B^1 · C^2, that is the sum of x_A(r_1) * x_B(r_2) * x_C(r_3) over all tuples (r_1, ..., r_3) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

-542

## Level 5

### Example 1

**Prompt:**

A dataset of records, each holding 4 attributes named ['A', 'B', 'C', 'D'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = -104, P_B = -3, P_C = 53, P_D = -51, M_AB = 1570, M_AC = -2220, M_AD = 11068, M_BC = -134, M_BD = 902, M_CD = -2072, M_ABC = 11309, M_ABD = -60156, M_ACD = 249626, M_BCD = 11824, M_ABCD = -1235419. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^3 · B^1 · C^2 · D^3, that is the sum of x_A(r_1) * x_B(r_2) * x_C(r_3) * x_D(r_4) over all tuples (r_1, ..., r_4) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

1015590

### Example 2

**Prompt:**

A dataset of records, each holding 4 attributes named ['A', 'B', 'C', 'D'], was aggregated into the following exact statistics. Each statistic is a sum over every record in the dataset, and in these aggregate statistics two different attribute factors may be read from the same record: P_A = 121, P_B = 2, P_C = -3, P_D = 73, M_AB = 2, M_AC = 700, M_AD = 638, M_BC = 14, M_BD = 54, M_CD = -439, M_ABC = -2135, M_ABD = 303, M_ACD = 1707, M_BCD = 3787, M_ABCD = 46269. Compute the sum over all ordered choices of distinct records — one different record per factor — of the monomial A^2 · B^1 · C^3 · D^2, that is the sum of x_A(r_1) * x_B(r_2) * x_C(r_3) * x_D(r_4) over all tuples (r_1, ..., r_4) where no two record indices coincide (r_i ≠ r_j for i ≠ j), removing every index collision. Report the exact integer result.

**Answer:**

229240
