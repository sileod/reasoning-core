## Level 0
### Prompt
Subjects and objects are the same 4 nodes S0..S3. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S0 has S2, S1 has S0, S1 has S2, S2 has S1, S2 has S3, S3 has S1, S3 has S2.
Controls: take(S0, S3); take(S1, S2); grant(S3, S0); grant(S0, S2); create(S1, S0).

After closure, the queried right is whether S2 has S0. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
no

### Prompt
Subjects and objects are the same 4 nodes S0..S3. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S1 has S0, S1 has S3, S3 has S1.
Controls: grant(S1, S3); grant(S2, S0); take(S1, S2).

After closure, the queried right is whether S3 has S0. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
yes

## Level 2
### Prompt
Subjects and objects are the same 6 nodes S0..S5. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S1 has S2, S3 has S4, S5 has S1.
Controls: create(S3, S2); grant(S3, S4); take(S5, S0).

After closure, the queried right is whether S4 has S2. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
yes

### Prompt
Subjects and objects are the same 6 nodes S0..S5. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S0 has S3, S0 has S4, S1 has S0, S1 has S2, S1 has S3, S1 has S5, S2 has S1, S2 has S3, S2 has S5, S4 has S3, S4 has S5, S5 has S2, S5 has S3.
Controls: take(S0, S1); take(S2, S1); take(S3, S4); take(S5, S2); grant(S0, S5); grant(S3, S5); grant(S0, S1); grant(S5, S2); create(S2, S0); create(S5, S0).

After closure, the queried right is whether S3 has S2. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
no

## Level 5
### Prompt
Subjects and objects are the same 9 nodes S0..S8. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S1 has S2, S1 has S3, S1 has S5, S2 has S1, S2 has S7, S3 has S5, S3 has S8, S4 has S1, S4 has S5, S8 has S0, S8 has S1, S8 has S4, S8 has S6.
Controls: take(S8, S4); take(S3, S8); create(S7, S2).

After closure, the queried right is whether S3 has S1. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
yes

### Prompt
Subjects and objects are the same 9 nodes S0..S8. An edge 'X has Y' means subject X holds the right on object Y. The controls below describe how rights are derived; running them to closure repeatedly adds every right they can produce until no more change is possible. Control semantics:
  take(A, B): if A already has B, then for every object V that B has, A derives V.
  grant(A, B): if A already has B, then for every object V that A has, B derives V.
  create(A, B): A creates and therefore has B.
Initially: S0 has S5, S1 has S0, S1 has S6, S2 has S0, S2 has S3, S2 has S4, S2 has S6, S3 has S1, S3 has S5, S3 has S6, S4 has S0, S4 has S2, S4 has S5, S4 has S6, S4 has S8, S5 has S7, S6 has S5, S6 has S8, S7 has S0, S7 has S2, S7 has S4, S7 has S5, S8 has S3, S8 has S4, S8 has S6.
Controls: take(S5, S7); take(S7, S1); take(S7, S2); take(S4, S5); take(S0, S7); grant(S0, S8); grant(S1, S8); grant(S8, S4); grant(S4, S2); grant(S7, S5); create(S2, S6); create(S7, S6); create(S1, S7); create(S5, S2).

After closure, the queried right is whether S0 has S8. Is that right derivable (present after closure)? Answer exactly 'yes' or 'no'.
### Answer
no

