# Samples for weakest_precondition_computation (P009v2)

## Level 0

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 if -2 <= x <= 1 then
     x := 1*x + 1
 else
     x := 3*x + -1
 end
 x := 1*x + -2

We require the program's final value of x to satisfy the postcondition: -1 <= x <= 1

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
0 <= x <= 1
```

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 if -2 <= x <= 0 then
     x := 3*x + -3
 else
     x := 3*x + -2
 end
 x := 2*x + 0
 x := 2*x + 0

We require the program's final value of x to satisfy the postcondition: 0 <= x <= +inf

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
1 <= x <= +inf
```

## Level 2

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 x := 3*x + -2
 if -1 <= x <= 1 then
     x := 1*x + 1
 else
     x := 3*x + 1
 end
 x := 1*x + 1
 x := 2*x + 0
 x := 3*x + -2
 x := 3*x + -1

We require the program's final value of x to satisfy the postcondition: -inf <= x <= -3

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
-inf <= x <= 0
```

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 x := 2*x + 1
 x := 2*x + -3
 x := 2*x + 2
 if -2 <= x <= 0 then
     x := 2*x + 2
 else
     x := 1*x + 0
 end
 x := 1*x + -2
 x := 1*x + 3
 x := 1*x + 1

We require the program's final value of x to satisfy the postcondition: -inf <= x <= 2

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
-inf <= x <= -1
```

## Level 5

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 x := 3*x + 3
 x := 1*x + 2
 x := 3*x + 0
 if -2 <= x <= 2 then
     x := 1*x + -3
 else
     x := 2*x + 1
 end
 x := 1*x + 2
 x := 3*x + 3
 x := 2*x + 3
 x := 1*x + 1
 x := 2*x + -3
 x := 1*x + -1

We require the program's final value of x to satisfy the postcondition: -inf <= x <= -1

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
-inf <= x <= -2
```

**Prompt**
```
Consider this small program operating on an integer variable x. Statements execute in order. An if statement runs its then-branch when the guard holds, otherwise its else-branch.
 x := 2*x + 2
 x := 1*x + -2
 x := 3*x + -2
 x := 2*x + -1
 x := 3*x + -3
 if -1 <= x <= 0 then
     x := 2*x + 2
 else
     x := 2*x + 3
 end
 x := 2*x + -1

We require the program's final value of x to satisfy the postcondition: 1 <= x <= +inf

The weakest precondition is the condition on the entry value of x that guarantees the postcondition holds. Computed backwards, an if-else turns into a disjunction: an input satisfies the precondition iff (the guard holds and the then-branch's requirement holds) or (the guard fails and the else-branch's requirement holds). Because the program is piecewise linear in one variable, this collapses to a union of integer intervals of x.

Answer on one line as the union of intervals of integer x, each written 'lo <= x <= hi' with '-inf'/'+inf' for an unbounded side, adjacent intervals merged, intervals joined with ' || ' meaning logical or. A single interval needs no ' || '. Example answer format: '-inf <= x <= 2 || 5 <= x <= +inf'.
```

**Answer**
```
1 <= x <= +inf
```
