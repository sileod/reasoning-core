## Level 0

### Example 1

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   2/3
  0   1   2/3
  1   0   2/3
  1   1   2/3

What is the missing-data class of this mechanism?

**Answer:**

MCAR

### Example 2

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   1/3
  0   1   3/4
  1   0   —
  1   1   1/2

What is the missing-data class of this mechanism?

**Answer:**

MNAR

## Level 2

### Example 1

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   3/4
  0   1   3/4
  1   0   —
  1   1   —

What is the missing-data class of this mechanism?

**Answer:**

MCAR

### Example 2

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   1/5
  0   1   —
  1   0   1/5
  1   1   2/5

What is the missing-data class of this mechanism?

**Answer:**

MAR

## Level 5

### Example 1

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   —
  0   1   1/3
  1   0   1/2
  1   1   1/3

What is the missing-data class of this mechanism?

**Answer:**

MAR

### Example 2

**Prompt:**

There are two binary variables X and Y. X may be missing; Y is always observed. The table below gives, for every possible full-data record (X, Y), the probability P that X is observed given that record. A row marked with — is a structural zero: that record can never occur, so no missingness probability applies to it.

Class definitions:
- MCAR: P depends on neither X nor Y.
- MAR: P depends only on Y (the observed value).
- MNAR: P depends on X (the missing value) itself, even after accounting for Y.

  X   Y     P
  0   0   1/3
  0   1   —
  1   0   1/3
  1   1   1/3

What is the missing-data class of this mechanism?

**Answer:**

MCAR
