## Level 0

Example 1

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
q : a3
Expression: (\a.(a q))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

(t0 -> t1) -> t1


Example 2

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
w : a3
Expression: (\q.(\j.w))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

t0 -> (t1 -> t2)


## Level 2

Example 1

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
b : a3, p : a9, tval : a10
Expression: (\y.(\m.(let s = (m, b) in (p tval))))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

t0 -> (t1 -> t2)


Example 2

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
n : a12, s : a7, w : a13
Expression: (\fn.(let g = (fn s) in (g, (n w))))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

(t0 -> t1) -> (t2 * t3)


## Level 5

Example 1

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
g : a8, h : a21, j : a26, m : a14, n : a3, p : a2, pair : a12, tval : a20, v1 : a27, v2 : a28, v3 : a31
Expression: ((let r = (p n) in (let z = (\k.g) in (\b.(\w.(\x.(let c = p in pair)))))), (((let a = ((let fn = (\y.pair) in (let q = m in q)), (tval h)) in (let f = ((let s = pair in g), (j g)) in v1)), v2), (let v4 = (v3 v1) in tval)))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

((t0 -> (t1 -> (t2 -> t3))) * ((t4 * t5) * (t6 -> t7)))


Example 2

Prompt:

Using Hindley-Milner type inference, find the most general (principal) type of the following lambda expression.
Environment (types of the free variables), using atoms A, B, C and type variables a0, a1, ...:
f : a12, j : a19, m : a13, p : a14, pair : a20, tval : a4, w : a8
Expression: (let h = (\q.((\s.(let y = (q tval) in (\k.w))), (\r.(((let x = f in w), (q, q)), ((let c = r in m), (let g = r in p)))))) in (\b.(j pair)))
Give the principal type of the expression in a canonical form using atoms A/B/C and type variables t0, t1, ... (renamed in order of first appearance), arrows written '->' and pairs with '*', with parentheses only where needed. For example, the arrow overs the pair (t0 * A) -> t1 is (t0 * A) -> t1, and A -> B -> t0 goes: A -> B -> t0. Answer with the type only.


Answer:

t0 -> t1

