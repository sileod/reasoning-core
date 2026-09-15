# Samples for matrix_characteristic_polynomial (P003v2)

Two prompt/answer examples at each of levels 0, 2 and 5.

## Level 0

### Example 1

**Prompt:**

An unknown n=2 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=0, tr(A^2)=10. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[-5, 0, 1]
```

### Example 2

**Prompt:**

An unknown n=2 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=-1, tr(A^2)=23. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[-11, 1, 1]
```

## Level 2

### Example 1

**Prompt:**

An unknown n=3 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=1, tr(A^2)=31, tr(A^3)=31. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_3, c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[5, -15, -1, 1]
```

### Example 2

**Prompt:**

An unknown n=3 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=4, tr(A^2)=48, tr(A^3)=220. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_3, c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[12, -16, -4, 1]
```

## Level 5

### Example 1

**Prompt:**

An unknown n=4 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=-2, tr(A^2)=36, tr(A^3)=-62, tr(A^4)=564. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_4, c_3, c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[27, -14, -16, 2, 1]
```

### Example 2

**Prompt:**

An unknown n=4 symmetric integer matrix A is characterized only by traces of its powers: tr(A^1)=5, tr(A^2)=57, tr(A^3)=191, tr(A^4)=1609. Using the Faddeev-LeVerrier recurrence (c_k = -(s_k + c_1 s_{k-1} + ... + c_{k-1} s_1)/k, where s_k = tr(A^k) and c_1 = -s_1), determine the characteristic polynomial of A. Report the coefficient vector in ascending degree order, starting with the constant term and ending with the leading coefficient, as the list [c_4, c_3, c_2, c_1, 1]. The answer is this list of integers, e.g. [-4, 0, 1] for x^2 - 4.

**Answer:**

```text
[-8, 58, -16, -5, 1]
```
