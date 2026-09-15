# Level 0
```
A Bayesian network has variables [0, 1] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 7/10.
P(1=0) = 3/10.
Marginalize over all unlisted variables. What is P(1=1)?
Answer as an exact rational a/b.
```
Answer: 7/10

```
A Bayesian network has variables [0, 1] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 3/5.
P(1=0) = 3/10.
Marginalize over all unlisted variables. What is P(0=0)?
Answer as an exact rational a/b.
```
Answer: 3/5

# Level 2
```
A Bayesian network has variables [0, 1, 2, 3] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 2/5.
P(1=0 | parents) = 4/5 when parents (0,) = (0,); 7/10 when parents (0,) = (1,).
P(2=0 | parents) = 2/5 when parents (0,) = (0,); 1/10 when parents (0,) = (1,).
P(3=0 | parents) = 4/5 when parents (2,) = (0,); 4/5 when parents (2,) = (1,).
Marginalize over all unlisted variables. What is P(0=0, 3=1)?
Answer as an exact rational a/b.
```
Answer: 2/25

```
A Bayesian network has variables [0, 1, 2, 3] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 3/5.
P(1=0 | parents) = 2/5 when parents (0,) = (0,); 1/2 when parents (0,) = (1,).
P(2=0 | parents) = 1/5 when parents (0,) = (0,); 7/10 when parents (0,) = (1,).
P(3=0 | parents) = 7/10 when parents (1,) = (0,); 1/5 when parents (1,) = (1,).
Marginalize over all unlisted variables. What is P(1=1)?
Answer as an exact rational a/b.
```
Answer: 14/25

# Level 5
```
A Bayesian network has variables [0, 1, 2, 3, 4] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 3/10.
P(1=0 | parents) = 1/10 when parents (0,) = (0,); 3/10 when parents (0,) = (1,).
P(2=0) = 1/10.
P(3=0 | parents) = 1/5 when parents (1,) = (0,); 3/10 when parents (1,) = (1,).
P(4=0) = 2/5.
Marginalize over all unlisted variables. What is P(0=1, 2=0, 4=0)?
Answer as an exact rational a/b.
```
Answer: 7/250

```
A Bayesian network has variables [0, 1, 2, 3, 4] over states 0..1 in that fixed order. Each node's table gives P(node state = 0 | parent states); the complementary mass is on state 1.
P(0=0) = 1/10.
P(1=0 | parents) = 7/10 when parents (0,) = (0,); 3/10 when parents (0,) = (1,).
P(2=0 | parents) = 1/2 when parents (0, 1) = (0, 0); 1/5 when parents (0, 1) = (1, 0); 2/5 when parents (0, 1) = (0, 1); 4/5 when parents (0, 1) = (1, 1).
P(3=0 | parents) = 4/5 when parents (2,) = (0,); 3/5 when parents (2,) = (1,).
P(4=0) = 2/5.
Marginalize over all unlisted variables. What is P(4=0)?
Answer as an exact rational a/b.
```
Answer: 2/5

