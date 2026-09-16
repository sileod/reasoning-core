# Attribute Grammar Evaluation - samples P005v3

## Level 0

### Example 1

**Prompt:**

```
An arithmetic expression is built from the following parse tree. Each node carries two attributes. Inherited 'ctx' starts at 0 at the root and flows down the tree; synthesized value flows up. The rules for this grammar are:
- N(v): a leaf emitting v + ctx
- env(k, T): the child T runs with ctx += k and contributes its value
- add/mul/sub(L, R): both children inherit the same ctx; the node value is L + R, L * R, or L - R respectively.
Evaluate the grammar and report the root's synthesized value.

Parse tree:

    env(2, N(-1))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
1
```

### Example 2

**Prompt:**

```
An arithmetic expression is built from the following parse tree. Each node carries two attributes. Inherited 'ctx' starts at 0 at the root and flows down the tree; synthesized value flows up. The rules for this grammar are:
- N(v): a leaf emitting v + ctx
- env(k, T): the child T runs with ctx += k and contributes its value
- add/mul/sub(L, R): both children inherit the same ctx; the node value is L + R, L * R, or L - R respectively.
Evaluate the grammar and report the root's synthesized value.

Parse tree:

    env(2, N(-8))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
-6
```

## Level 2

### Example 1

**Prompt:**

```
A Boolean expression is built from the following parse tree. Inherited 'ctx' starts at 0 at the root and flows down; synthesized value flows up. Rules:
- C(v): a leaf emitting (v > ctx)
- env(k, T): the child T runs with ctx += k and contributes its value
- and/or(L, R): both children inherit the same ctx; the node value is the logical AND or OR.
- not(T): logical NOT of the child.
Evaluate the grammar and report the root's value as exactly 'true' or 'false'.

Parse tree:

    env(-2, env(-4, C(-1)))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
true
```

### Example 2

**Prompt:**

```
A Boolean expression is built from the following parse tree. Inherited 'ctx' starts at 0 at the root and flows down; synthesized value flows up. Rules:
- C(v): a leaf emitting (v > ctx)
- env(k, T): the child T runs with ctx += k and contributes its value
- and/or(L, R): both children inherit the same ctx; the node value is the logical AND or OR.
- not(T): logical NOT of the child.
Evaluate the grammar and report the root's value as exactly 'true' or 'false'.

Parse tree:

    or(env(3, C(3)), env(0, C(0)))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
false
```

## Level 5

### Example 1

**Prompt:**

```
A string is built from the following parse tree. Inherited 'ctx' starts at 0 at the root and flows down; synthesized value flows up. Rules:
- S('c'): a leaf emitting the character 'c' repeated (1 + |ctx| mod 3) times
- env(k, T): the child T runs with ctx += k and contributes its value
- cat(L, R): concatenation, both children inherit the same ctx.
- rep(k, T): the child's string repeated k times.
Evaluate the grammar and report the root's exact resulting string.

Parse tree:

    cat(cat(rep(2, cat(S('y'), S('x'))), cat(cat(S('x'), S('y')), cat(S('a'), S('c')))), env(-3, rep(3, env(6, S('a')))))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
yxyxxyacaaa
```

### Example 2

**Prompt:**

```
An arithmetic expression is built from the following parse tree. Each node carries two attributes. Inherited 'ctx' starts at 0 at the root and flows down the tree; synthesized value flows up. The rules for this grammar are:
- N(v): a leaf emitting v + ctx
- env(k, T): the child T runs with ctx += k and contributes its value
- add/mul/sub(L, R): both children inherit the same ctx; the node value is L + R, L * R, or L - R respectively.
Evaluate the grammar and report the root's synthesized value.

Parse tree:

    env(3, add(mul(env(0, N(-2)), env(6, N(-2))), add(env(-2, N(-1)), sub(N(9), N(5)))))

What is the root's synthesized value? Give only the answer, nothing else.
```

**Answer:**

```
11
```
