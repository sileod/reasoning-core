# Samples: P009v1

## Level 0 example 1

### Prompt

At a hearing, speakers A, B, C, D each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = true
F2 = false
F3 = false
F4 = (F2 XOR F3)
F5 = (F3 OR F4)
F6 = (F1 AND F5)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. D claims: (H(A) AND F4)
C2. B claims: NOT ((H(C) XOR H(A)) XOR F5)
C3. A claims: (H(D) AND F5)
C4. C claims: NOT F6
C5. D claims: (H(A) XOR F6)
C6. B claims: ((H(D) AND H(C)) XOR F4)
C7. C claims: NOT ((H(A) AND H(B)) XOR F5)
C8. A claims: ((H(C) AND H(A)) XOR F4)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

LLHL

## Level 0 example 2

### Prompt

At a hearing, speakers A, B, C, D each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = true
F2 = false
F3 = true
F4 = (F2 OR F3)
F5 = (F4 IFF F3)
F6 = (F1 XOR F5)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. C claims: NOT (H(A) IFF F6)
C2. B claims: ((H(C) XOR H(D)) XOR F4)
C3. D claims: (H(A) IFF F5)
C4. D claims: ((H(A) IFF H(C)) XOR F4)
C5. B claims: ((H(C) IFF H(B)) XOR F5)
C6. A claims: (H(B) XOR F5)
C7. C claims: ((H(D) IFF H(A)) XOR F4)
C8. A claims: ((H(D) IFF H(B)) XOR F6)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

LHLL

## Level 2 example 1

### Prompt

At a hearing, speakers A, B, C, D, E each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = false
F2 = true
F3 = true
F4 = (F1 IFF F3)
F5 = (F2 OR F4)
F6 = (F5 XOR F4)
F7 = (F2 IFF F6)
F8 = (F7 OR F1)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. D claims: NOT (H(C) XOR F6)
C2. B claims: NOT ((H(D) XOR H(E)) XOR F7)
C3. C claims: NOT F8
C4. D claims: NOT (H(E) OR F8)
C5. E claims: NOT ((H(B) OR H(E)) XOR F7)
C6. B claims: NOT F7
C7. C claims: NOT (H(D) OR F6)
C8. A claims: (H(C) IFF F4)
C9. E claims: ((H(A) IFF H(C)) XOR F4)
C10. A claims: ((H(C) AND H(E)) XOR F7)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

HLLLL

## Level 2 example 2

### Prompt

At a hearing, speakers A, B, C, D, E each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = false
F2 = true
F3 = false
F4 = (F1 IFF F3)
F5 = (F4 IFF F2)
F6 = (F4 XOR F5)
F7 = (F6 OR F2)
F8 = (F7 IFF F3)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. C claims: ((H(E) XOR H(A)) XOR F7)
C2. D claims: NOT ((H(A) OR H(B)) XOR F7)
C3. E claims: ((H(B) AND H(C)) XOR F5)
C4. C claims: NOT ((H(E) OR H(C)) XOR F4)
C5. B claims: NOT ((H(C) OR H(B)) XOR F8)
C6. A claims: F4
C7. D claims: NOT F6
C8. B claims: ((H(A) AND H(B)) XOR F8)
C9. A claims: (H(B) AND F5)
C10. E claims: ((H(D) IFF H(A)) XOR F6)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

C9

## Level 5 example 1

### Prompt

At a hearing, speakers A, B, C, D, E, F, G, H each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = true
F2 = false
F3 = true
F4 = (F3 OR F1)
F5 = (F4 OR F1)
F6 = (F4 XOR F5)
F7 = (F6 XOR F3)
F8 = (F1 IFF F7)
F9 = (F8 IFF F4)
F10 = (F2 IFF F9)
F11 = (F3 XOR F10)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. F claims: NOT (H(A) IFF F11)
C2. G claims: NOT (H(F) OR F9)
C3. A claims: (H(G) IFF F5)
C4. H claims: NOT ((H(F) AND H(H)) XOR F7)
C5. G claims: (H(D) IFF F5)
C6. C claims: ((H(B) XOR H(F)) XOR F7)
C7. D claims: NOT (H(C) XOR F11)
C8. D claims: NOT ((H(F) AND H(H)) XOR F8)
C9. E claims: NOT ((H(B) XOR H(E)) XOR F11)
C10. E claims: ((H(H) OR H(D)) XOR F7)
C11. B claims: NOT F9
C12. F claims: NOT (H(A) AND F10)
C13. H claims: (H(B) AND F11)
C14. A claims: (H(A) IFF F7)
C15. C claims: ((H(F) XOR H(B)) XOR F9)
C16. B claims: NOT ((H(E) XOR H(H)) XOR F6)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

LLLLHHLL

## Level 5 example 2

### Prompt

At a hearing, speakers A, B, C, D, E, F, G, H each have one fixed role from the roster H (honest) or L (liar).
Roles may repeat; no counts are imposed. Every claim by H must be true and every claim by L must be false.
The following fact definitions are given as true rules, not speaker claims. Each F is Boolean. AND requires both operands, OR is inclusive, XOR means exactly one, IFF means equal truth values, and NOT reverses truth.
F1 = false
F2 = true
F3 = true
F4 = (F3 XOR F2)
F5 = (F4 XOR F2)
F6 = (F1 AND F5)
F7 = (F6 XOR F3)
F8 = (F7 AND F1)
F9 = (F8 AND F4)
F10 = (F1 AND F9)
F11 = (F10 AND F7)
In claims, H(A) means 'A has role H' (similarly for other names). Claims are numbered in the order to process:
C1. F claims: ((H(B) OR H(E)) XOR F10)
C2. A claims: NOT (H(H) OR F6)
C3. A claims: ((H(C) OR H(G)) XOR F4)
C4. E claims: (H(F) AND F11)
C5. G claims: (H(G) XOR F11)
C6. C claims: ((H(B) AND H(E)) XOR F9)
C7. G claims: NOT ((H(D) AND H(A)) XOR F11)
C8. D claims: NOT F7
C9. F claims: ((H(G) XOR H(H)) XOR F4)
C10. B claims: (H(C) XOR F8)
C11. D claims: ((H(E) OR H(F)) XOR F5)
C12. E claims: NOT ((H(H) XOR H(C)) XOR F6)
C13. C claims: (H(H) XOR F4)
C14. H claims: NOT (H(A) XOR F4)
C15. B claims: NOT ((H(F) OR H(A)) XOR F10)
C16. H claims: NOT (H(B) IFF F10)
Use Boolean constraint propagation or exhaustive role assignment search. If all claims can hold under the role rules, return the lexicographically smallest role string in speaker order above, with H before L; for example HLLH for four speakers. Otherwise return the first blocking claim Ck: the smallest k such that no assignment satisfies claims C1 through Ck (ignore later claims). Example format: C7. Output only the role string or claim label.

### Answer

C10
