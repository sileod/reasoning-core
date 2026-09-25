# Level 0

## Example 1

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
(UP(2*) AND ~(2))

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {0,1,3,4}

## Example 2

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
((4* AND 3) AND P{3}(3*))

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {3}

# Level 2

## Example 1

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
(0* AND (2 OR 3))

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {2,3}

## Example 2

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
((3 OR 4) AND (0* AND 1*))

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {3,4}

# Level 5

## Example 1

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4,5}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
~(P{2,4}(5*))

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {0,1,3,5}

## Example 2

Prompt:

We work in a tiny alternative-semantics model over the domain of individuals D = {0,1,2,3,4,5}.
Every expression denotes a set of individuals (its alternatives). The composition rules are:
  - an unfocused constant n denotes the singleton {n};
  - a focused constant n* denotes the whole domain D;
  - a predicate P with extension E restricts: P(X) = X INTERSECT E;
  - the complement modifier ~ inverts: ~(X) = D minus X;
  - conjunction joins requirements: A AND B = A INTERSECT B;
  - disjunction collects options: A OR B = A UNION B;
  - the focus operator UP widens any option set to the whole D.

Displayed expression:
(3* AND 5)

Give the resulting alternative set, written as {a,b,c} in ascending order, or the bare word 'empty' if the resulting set is empty.


Answer: {5}


Generated deterministically with seed 368817805.
