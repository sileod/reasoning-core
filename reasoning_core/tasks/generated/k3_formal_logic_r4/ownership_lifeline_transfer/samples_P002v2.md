# Level 0

**Example 1**

Prompt:

Track a single value under the variables A B C. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: freeze
2: freeze
3: drop B
4: freeze
5: freeze
6: freeze
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

3: moved-value

**Example 2**

Prompt:

Track a single value under the variables A B C. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: borrow B to C
2: reborrow C to A
3: reborrow A to A
4: borrow B to A
5: move B to C
6: borrow B to A
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

5: borrow-in-use

# Level 2

**Example 1**

Prompt:

Track a single value under the variables A B C D E. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: borrow D to A
2: reborrow C to A
3: return A
4: borrow D to E
5: freeze
6: reborrow E to B
7: borrow D to E
8: return B
9: return E
10: borrow D to A
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

2: no-active-loan

**Example 2**

Prompt:

Track a single value under the variables A B C D E. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: borrow C to B
2: return B
3: move C to D
4: freeze
5: freeze
6: freeze
7: freeze
8: borrow D to B
9: drop B
10: freeze
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

9: moved-value

# Level 5

**Example 1**

Prompt:

Track a single value under the variables A B C D E F G H. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: borrow H to A
2: move B to E
3: move E to B
4: freeze
5: borrow B to C
6: freeze
7: return C
8: freeze
9: freeze
10: borrow B to F
11: borrow B to C
12: reborrow C to H
13: borrow B to F
14: freeze
15: reborrow C to A
16: borrow B to H
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

1: moved-value

**Example 2**

Prompt:

Track a single value under the variables A B C D E F G H. Exactly one variable is the current owner of the value; any other variable is 'moved' and no longer owns it. Several variables may hold overlapping shared borrows simultaneously. The events are:
- `move X to Y`: ownership transfers from X to Y (illegal if X is not the owner, or if the value is frozen or any borrow is held).
- `borrow X to Y`: owner X lends a shared borrow that Y now holds (illegal if X is not the owner; borrows may accumulate even when frozen).
- `reborrow X to Y`: Y takes a borrow from X's existing borrow (illegal if X holds no loan).
- `return X`: X releases the borrow it holds (illegal if X holds no loan).
- `freeze`: the value becomes frozen, blocking any move or drop.
- `drop X`: X destroys the value (illegal if X is not the owner, or if the value is frozen or any borrow is held).
The events below are applied in order.
1: borrow H to G
2: return G
3: move H to E
4: move E to G
5: borrow G to D
6: return D
7: borrow G to H
8: return E
9: freeze
10: borrow G to E
11: borrow G to H
12: borrow G to B
13: return H
14: borrow G to C
15: borrow G to E
16: reborrow B to E
Find the FIRST event that is illegal. Answer with its 1-based index and the rule it violates, exactly as `N: rule` where rule is one of `moved-value`, `borrow-in-use`, or `no-active-loan`. For example: `5: moved-value`.

Answer:

8: no-active-loan
