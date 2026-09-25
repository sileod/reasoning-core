# Samples P007v3

## Level 0

### Example 1

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [y := (<0,1>)] in the normal-form term ((\w.(<x,0>)) y), then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(<x,0>)

### Example 2

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [x := (\x.(\z.0))] in the normal-form term x, then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(\x.(\z.0))


## Level 2

### Example 1

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [x := (projsnd((<(\x.w),(projfst((<(<2,1>),2>)))>)))] in the normal-form term (<0,2>), then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(<0,2>)

### Example 2

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [x := 2] in the normal-form term ((\w.(\z.2)) x), then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(\z.2)


## Level 5

### Example 1

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [w := 2] in the normal-form term ((\z.(projfst((<(<(projfst((<(<y,x>),(\x.(projsnd((<(<1,y>),(\x.(\z.0))>))))>))),(projsnd((<2,2>)))>),w>)))) w), then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(<(<y,x>),2>)

### Example 2

**Prompt:**

In the simply-typed lambda calculus with products, projects, and base numerals, perform the substitution [z := (\w.(projfst((<y,0>))))] in the normal-form term ((\v.(\y.(\x.(\v.((<1,(\u.1)>) (<(\x.2),0>)))))) z), then immediately reduce every redex created by the replacement until you reach a beta-normal form that is itself normal. Write only the final beta-normal term, in the same surface syntax used above.

**Answer:**

(\y.(\x.(\v.((<1,(\u.1)>) (<(\x.2),0>)))))

