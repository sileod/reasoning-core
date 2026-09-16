## Level 0

### Example 1

Let f = (ln,[x]). This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: (div,[1, x])

### Example 2

Let f = (ln,[x]). This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: (div,[1, x])

## Level 2

### Example 1

Let f = (pow,[(add,[(cos,[x]), (sin,[6])]), 5]). This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: (mul,[(mul,[5, (pow,[(add,[(cos,[x]), (sin,[6])]), (sub,[5, 1])])]), (add,[(mul,[(mul,[-1, (sin,[x])]), 1]), (mul,[(cos,[6]), 0])])])

### Example 2

Let f = 2. This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: 0

## Level 5

### Example 1

Let f = x. This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: 1

### Example 2

Let f = (div,[(div,[(add,[(add,[(pow,[(div,[2, 8]), 4]), (ln,[(pow,[x, 5])])]), (sin,[(mul,[(ln,[x]), (sub,[x, x])])])]), (pow,[x, 3])]), (ln,[(add,[(exp,[(add,[(sin,[2]), x])]), 7])])]). This convex nested tuple encodes an expression tree: each node is (operator, [children]) where 'x' and integers are leaves. Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product rule, quotient rule, and chain rule recursively, compute the derivative f' and encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or combining any subexpressions. Preserve the rule order of the derivative. Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is (add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.


Answer: (div,[(sub,[(mul,[(div,[(sub,[(mul,[(add,[(add,[(mul,[(mul,[4, (pow,[(div,[2, 8]), (sub,[4, 1])])]), (div,[(sub,[(mul,[0, 8]), (mul,[2, 0])]), (pow,[8, 2])])]), (div,[(mul,[(mul,[5, (pow,[x, (sub,[5, 1])])]), 1]), (pow,[x, 5])])]), (mul,[(cos,[(mul,[(ln,[x]), (sub,[x, x])])]), (add,[(mul,[(div,[1, x]), (sub,[x, x])]), (mul,[(ln,[x]), (sub,[1, 1])])])])]), (pow,[x, 3])]), (mul,[(add,[(add,[(pow,[(div,[2, 8]), 4]), (ln,[(pow,[x, 5])])]), (sin,[(mul,[(ln,[x]), (sub,[x, x])])])]), (mul,[(mul,[3, (pow,[x, (sub,[3, 1])])]), 1])])]), (pow,[(pow,[x, 3]), 2])]), (ln,[(add,[(exp,[(add,[(sin,[2]), x])]), 7])])]), (mul,[(div,[(add,[(add,[(pow,[(div,[2, 8]), 4]), (ln,[(pow,[x, 5])])]), (sin,[(mul,[(ln,[x]), (sub,[x, x])])])]), (pow,[x, 3])]), (div,[(add,[(mul,[(exp,[(add,[(sin,[2]), x])]), (add,[(mul,[(cos,[2]), 0]), 1])]), 0]), (add,[(exp,[(add,[(sin,[2]), x])]), 7])])])]), (pow,[(ln,[(add,[(exp,[(add,[(sin,[2]), x])]), 7])]), 2])])

