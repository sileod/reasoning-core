# Samples for macro_hygiene_expansion (P002v1)

Two complete prompt/answer examples at each of levels 0, 2 and 5.

## Level 0

### Example 1 (level 0)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(g) = (\e. (((g (((g g) g) g)) g) (g ((g (((g (((g ((g g) g)) g) (g (g g)))) g) g)) g))) \t. g)

Expand this call completely:
(M0 \c. g)

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
(\e. (((\c. g (((\c. g \c. g) \c. g) \c. g)) \c. g) (\c. g ((\c. g (((\c. g (((\c. g ((\c. g \c. g) \c. g)) \c. g) (\c. g (\c. g \c. g)))) \c. g) \c. g)) \c. g))) \t. \c. g)
```

### Example 2 (level 0)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(s) = s  [exempt: s]

Expand this call completely:
(M0 s)

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
s
```

## Level 2

### Example 1 (level 2)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(c) = (\c. \q. (c c) \q. (c c))  [exempt: c]
M1(s, r) = (((r r) \a. r) r)
M2(a) = \a. a

Expand this call completely:
(M1 \d. r (\q. (((r (r r)) s) r) (r (r s))))

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
((((\q. (((r (r r)) s) r) (r (r s))) (\q. (((r (r r)) s) r) (r (r s)))) \a. (\q. (((r (r r)) s) r) (r (r s)))) (\q. (((r (r r)) s) r) (r (r s))))
```

### Example 2 (level 2)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(g, t) = g
M1(f, q) = f  [exempt: f]
M2(p, e) = (M1 p e)  [exempt: p]

Expand this call completely:
(M1 q)

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
q
```

## Level 5

### Example 1 (level 5)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(e, c, t) = (((t \p. (((t t) c) (e (t ((t (c e)) c))))) (\u. \g. (t ((e c) t)) (c ((t (e c)) (e (t e)))))) (t \d. \c. e))  [exempt: c]
M1(g, t, p) = (\c. (\c. ((((p p) g) (t p)) (g g)) (t \d. ((g (g (g (g (g p))))) (p t)))) \f. (p \c. \q. (t g)))  [exempt: g]
M2(u) = (u ((\g. \r. (u u) \t. ((u u) u)) u))
M3(c) = (M0 \r. (c (c c)) (c c) \s. \r. c)
M4(u, e) = (M3 \p. (e \p. u))  [exempt: e]
M5(a, u) = (a \d. u)

Expand this call completely:
(M4 (u u) u)

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
(((\s. \r. \p. (u \p. (u u)) \p. (((\s. \r. \p. (u \p. (u u)) \s. \r. \p. (u \p. (u u))) (\p. (u \p. (u u)) \p. (u \p. (u u)))) (\r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))) (\s. \r. \p. (u \p. (u u)) ((\s. \r. \p. (u \p. (u u)) ((\p. (u \p. (u u)) \p. (u \p. (u u))) \r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))))) (\p. (u \p. (u u)) \p. (u \p. (u u)))))))) (\x_0. \g. (\s. \r. \p. (u \p. (u u)) ((\r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))) (\p. (u \p. (u u)) \p. (u \p. (u u)))) \s. \r. \p. (u \p. (u u)))) ((\p. (u \p. (u u)) \p. (u \p. (u u))) ((\s. \r. \p. (u \p. (u u)) (\r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))) (\p. (u \p. (u u)) \p. (u \p. (u u))))) (\r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))) (\s. \r. \p. (u \p. (u u)) \r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u)))))))))) (\s. \r. \p. (u \p. (u u)) \d. \c. \r. (\p. (u \p. (u u)) (\p. (u \p. (u u)) \p. (u \p. (u u))))))
```

### Example 2 (level 5)

Prompt:

```
Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing
each parameter of M's body with the matching argument. Arguments are expanded to values
first. During substitution, if a binder inside a macro body would capture a free variable
of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended
capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed
(capture by those binders is the declared intent).

Macros:
M0(c) = \c. c
M1(r) = ((\s. r r) (r (\a. r (\e. r ((r (r r)) r)))))
M2(q) = q
M3(a, q) = a
M4(q, c) = q  [exempt: q]
M5(q, r) = (\u. \q. \p. (r (((r r) q) (r r))) q)  [exempt: r]

Expand this call completely:
(M4 \r. (\d. \p. c c))

What is the fully expanded term, with all macro calls resolved and binders
renamed exactly as described? Give the term using lambda syntax consisting of
a binder `\name <term>`, application `(f a)`, and variable names.
```

Answer:

```
\r. (\d. \p. c c)
```
