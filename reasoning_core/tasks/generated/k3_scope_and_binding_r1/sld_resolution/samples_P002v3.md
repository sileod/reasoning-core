# Level 0

## Example 1

### Prompt

```
Consider this definite-clause (Horn) logic program:
q(c).
q(d).
Goal: q(W)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ W=c } ; { W=d }
```

## Example 2

### Prompt

```
Consider this definite-clause (Horn) logic program:
p(d).
p(a).
Goal: p(U)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ U=d } ; { U=a }
```

# Level 2

## Example 1

### Prompt

```
Consider this definite-clause (Horn) logic program:
p(d).
p(f).
p(V) :- s(V).
s(e).
Goal: p(U)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ U=d } ; { U=f }
```

## Example 2

### Prompt

```
Consider this definite-clause (Horn) logic program:
q(d).
q(h).
q(V) :- r(V).
r(g).
Goal: q(V)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ V=d } ; { V=h }
```

# Level 5

## Example 1

### Prompt

```
Consider this definite-clause (Horn) logic program:
q(g).
q(f).
q(V) :- r(V).
r(h).
q(W) :- r(W), q(W).
Goal: q(W)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ W=g } ; { W=f }
```

## Example 2

### Prompt

```
Consider this definite-clause (Horn) logic program:
q(c).
q(h).
q(V) :- s(V).
s(f).
q(W) :- s(W), q(W).
Goal: q(U)
Using SLD resolution -- renaming variables apart before each clause use, occurs-check unification, selecting the leftmost goal, and depth-first backtracking through clause order as written -- compute the ordered answer substitutions for the goal variable(s). Write them in the order found, separated by ' ; '. Each substitution has the form: { X=c, Y=unbound }, where an unbounded goal variable is shown as 'unbound'. If no derivation succeeds, answer exactly: fail
```

### Answer

```
{ U=c } ; { U=h }
```

