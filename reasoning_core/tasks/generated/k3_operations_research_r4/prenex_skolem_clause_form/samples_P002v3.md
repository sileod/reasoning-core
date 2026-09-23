# samples_P002v3: prenex_skolem_clause_form

Two complete prompt/answer examples at levels 0, 2 and 5. Answers are the gold answers the task scores.

## Level 0

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: forall x.(exists y.(not((R and R))))
Give the exact Skolem term that replaces the existential variable bound in the prenex as this variable: the variable y.
Write the term exactly as rendered, e.g. f(x) or sk2(y,z) or a plain constant such as sk1. Answer with the term and nothing else.

### Answer

sk0(x)

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: exists x.(forall y.((not(Q) or G(y))))
Give the exact Skolem term that replaces the existential variable bound in the prenex as this variable: the variable x.
Write the term exactly as rendered, e.g. f(x) or sk2(y,z) or a plain constant such as sk1. Answer with the term and nothing else.

### Answer

sk0


## Level 2

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: forall x.(forall y.(exists z.(exists w.((((Q(f(y)) and H(z)) or H) -> Q(x))))))
Write the final clause set as a semicolon-separated list of clauses, each clause a brace-enclosed comma-separated set of literals such as {not P(a), Q(b)}; {R(x)}. Use the predicate, function and Skolem function names exactly as introduced. Answer with the clause set and nothing else.

### Answer

{Q(x), not H(sk0(x,y)), not Q(f(y))}; {Q(x), not H}

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: exists x.(exists y.(forall z.(forall w.(((not(P(z)) and H) or R(z))))))
Write the final clause set as a semicolon-separated list of clauses, each clause a brace-enclosed comma-separated set of literals such as {not P(a), Q(b)}; {R(x)}. Use the predicate, function and Skolem function names exactly as introduced. Answer with the clause set and nothing else.

### Answer

{H, R(z)}; {R(z), not P(z)}


## Level 5

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: exists x.(exists y.(exists z.(exists w.(forall u.(forall v.(exists t.(((not((H(h(t,w)) and H)) -> G(f(u),f(u))) or G))))))))
Give the exact Skolem term that replaces the existential variable bound in the prenex as this variable: the variable w.
Write the term exactly as rendered, e.g. f(x) or sk2(y,z) or a plain constant such as sk1. Answer with the term and nothing else.

### Answer

sk3

### Prompt

Convert the following first-order formula to clause form by pushing negations to negation normal form, pulling quantifiers out into a prenex, replacing each existential by a Skolem term that depends on the universal variables in scope, and distributing to conjunctive normal form.
Formula: exists x.(exists y.(forall z.(exists w.(exists u.(exists v.(forall t.(((((Q(h(w,x),f(v)) -> Q) or G) -> H(h(y,u),f(z))) -> G))))))))
Write the final clause set as a semicolon-separated list of clauses, each clause a brace-enclosed comma-separated set of literals such as {not P(a), Q(b)}; {R(x)}. Use the predicate, function and Skolem function names exactly as introduced. Answer with the clause set and nothing else.

### Answer

{G, Q, not Q(h(sk2(z),sk0),f(sk4(z)))}; {G, not H(h(sk1,sk3(z)),f(z))}


