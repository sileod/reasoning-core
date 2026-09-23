# samples_P009v1

Task: ordered_rule_surface_derivation

Ordered context-sensitive rewrite rules over invented segment inventories: derive a surface string from an underlying form, or decide whether swapping two rules' order (feeding/bleeding) changes the surface.

## Level 0

### Example

Prompt:
```
The only segments of a language are: k, p, n, v.
Underlying form: vnnvp
Ordered rewrite rules, applied in the order listed. Each rule rewrites every matching occurrence at once, using the string as it is when that rule starts; ∅ means that side is unconstrained; 'A -> B / X _ Y' rewrites A to B when it occurs after X and before Y:
R1. v -> p / ∅ _ n
Compute the surface form obtained after applying all rules to the underlying form. The answer is the surface string of segments.
```

Answer:
```
pnnvp
```

### Example

Prompt:
```
The only segments of a language are: l, s, f, b.
Underlying form: flsll
Ordered rewrite rules, applied in the order listed. Each rule rewrites every matching occurrence at once, using the string as it is when that rule starts; ∅ means that side is unconstrained; 'A -> B / X _ Y' rewrites A to B when it occurs after X and before Y:
R1. l -> b / l _ ∅
Compute the surface form obtained after applying all rules to the underlying form. The answer is the surface string of segments.
```

Answer:
```
flslb
```

## Level 2

### Example

Prompt:
```
The only segments of a language are: z, t, p, g, v, b.
Underlying form: zzzp
Rewrite rules, applied with the same semantics as above (each rule rewrites every matching occurrence at once):
R1. z -> t / ∅ _ z
R2. t -> g / ∅ _ t
Compare the surface string when the rules are applied in the order R1 then R2 versus the order R2 then R1. Does the order of the two rules change the final surface string? The answer is Yes or No.
```

Answer:
```
Yes
```

### Example

Prompt:
```
The only segments of a language are: r, b, t, l, d, s.
Underlying form: stbst
Rewrite rules, applied with the same semantics as above (each rule rewrites every matching occurrence at once):
R1. b -> r / ∅ _ ∅
R2. s -> l / ∅ _ t
Compare the surface string when the rules are applied in the order R1 then R2 versus the order R2 then R1. Does the order of the two rules change the final surface string? The answer is Yes or No.
```

Answer:
```
No
```

## Level 5

### Example

Prompt:
```
The only segments of a language are: f, r, m, d, s, l, k, z, t.
Underlying form: dsfmkftrm
Rewrite rules, applied with the same semantics as above (each rule rewrites every matching occurrence at once):
R1. f -> l / s _ mk
R2. r -> t / ∅ _ ∅
Compare the surface string when the rules are applied in the order R1 then R2 versus the order R2 then R1. Does the order of the two rules change the final surface string? The answer is Yes or No.
```

Answer:
```
No
```

### Example

Prompt:
```
The only segments of a language are: s, n, d, r, z, v, f, l, g.
Underlying form: lfzgz
Ordered rewrite rules, applied in the order listed. Each rule rewrites every matching occurrence at once, using the string as it is when that rule starts; ∅ means that side is unconstrained; 'A -> B / X _ Y' rewrites A to B when it occurs after X and before Y:
R1. l -> n / ∅ _ f
R2. g -> d / z _ ∅
R3. d -> s / z _ ∅
R4. f -> n / n _ z
R5. s -> l / nz _ ∅
Compute the surface form obtained after applying all rules to the underlying form. The answer is the surface string of segments.
```

Answer:
```
nnzlz
```
