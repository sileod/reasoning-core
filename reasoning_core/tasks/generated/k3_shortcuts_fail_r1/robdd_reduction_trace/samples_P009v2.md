
Level 0

Example 1

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: not (((y or x) and not (x))). Variable order: x, y.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(x, 1, ite(y, 0, 1))

Example 2

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: not (not ((x or 0))). Variable order: x, y.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(x, 1, 0)


Level 2

Example 1

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: not ((((not (u) and not (y)) or ((u and y) or (1 and y))) or not (not ((y and u))))). Variable order: x, y, z, u.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(y, 0, ite(u, 1, 0))

Example 2

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: not (((((y or y) and (y or x)) and ((u and 0) or (1 or x))) or not (((u and x) or (1 or 0))))). Variable order: x, y, z, u.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(y, 0, 1)


Level 5

Example 1

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: (((not (not (not (((z or v) or (0 or v))))) or not (((((v and v) or (v and z)) or ((u and y) and (1 or v))) or (not ((v and y)) or ((x or 0) and (y and y)))))) or not ((((((u or x) or (u and 0)) and not (not (x))) or (not ((w or 1)) or not ((v and u)))) or not ((((x or 1) or (z or z)) and ((u or 0) and not (z))))))) or ((((not (not ((v and y))) or (not ((1 or 0)) or (not (z) or not (w)))) or ((((0 and y) or (1 and w)) and ((0 or v) or (u or w))) and not (((y and v) and not (w))))) and (((not ((y or 1)) or (not (v) and not (y))) and not (((x and 1) or (0 or u)))) and ((((w and v) and (1 or 1)) or ((0 or v) or (z and z))) and (not ((x and 1)) or not ((w or u)))))) or (((not (not (not (w))) or not ((not (1) or not (x)))) or not (((not (1) and not (z)) and not ((0 or u))))) and not ((not ((not (w) and (y and v))) and ((not (x) and (0 or z)) and ((u and w) or (u and 1)))))))). Variable order: x, y, z, u, v, w.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(x, 1, ite(y, ite(z, ite(u, ite(v, ite(w, 0, 1), 0), 1), 1), ite(z, ite(u, 0, 1), 1)))

Example 2

Prompt:
For the boolean function below, build the reduced ordered binary decision diagram (ROBDD) under the fixed variable order and write the canonical serialized ITE structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon cofactoring with isomorphic subtrees merged and nodes eliminated when their two children are identical.
Function: (not (not (((((not (x) and not (u)) or (not (u) and (0 or y))) and (((y or v) or not (u)) and (not (0) and (0 and 0)))) or (not (((x or x) or (y and 0))) and not (((1 or u) and not (1))))))) or (not (not (not (not (not ((u or v)))))) and (not ((not (((w or z) and (z or v))) or (not (not (1)) or ((w or w) or (w or v))))) or not ((((not (0) and (u and v)) or ((0 and 0) and not (x))) and not (((w and u) and (z and y)))))))). Variable order: x, y, z, u, v, w.
Answer with only the serialized ITE structure of the reduced BDD, using 0 for false and 1 for true. For example, ite(x, ite(y, 0, 1), 1).

Answer:
ite(x, ite(u, 0, ite(v, 0, 1)), 1)
