# Level 0

### Example 1

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: sum = +.

Program: 0 dup drop sum 5 -2

Executing left to right, some word call may underflow (reach for values the stack does not hold). Which word is the FIRST to underflow? Answer with the word name.

**Answer**: sum

### Example 2

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: diff = -.

Program: -5 diff -2

Executing left to right, some word call may underflow (reach for values the stack does not hold). Which word is the FIRST to underflow? Answer with the word name.

**Answer**: diff

# Level 2

### Example 1

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: sumsq = square square +.

Program: 2 4 14 * sumsq -1 3

Evaluate the whole program. Give the final stack as space-separated integers from TOP (first) to BOTTOM (last); the answer is exactly that space-separated list.

**Answer**: 3 -1 2

### Example 2

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: dec = 1 -.

Program: -10 -4 dec -12 + * 11

After the word 'dec' finishes executing at its call site, what is the top value of the stack? Answer with the single integer.

**Answer**: -4

# Level 5

### Example 1

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: quad = double double.

Program: 5 drop 19 quad dup 16 -7 swap

After the word 'quad' finishes executing at its call site, what is the top value of the stack? Answer with the single integer.

**Answer**: 19

### Example 2

**Prompt**

A concatenative (Forth-style) machine runs over an integer stack; the stack top is the last value pushed. Literals push themselves. Primitives operate on the top values: dup: a -> a a; drop: a -> ; swap: a b -> b a; over: a b -> a b a; rot: a b c -> b c a; '+': a b -> a+b; '-': a b -> a-b; '*': a b -> a*b (rightmost is the top value). A word is a named block of tokens that expands, in place, to its definition every time it is called. Definitions: diff = - | negate = 0 swap - | prod = * | quad = double double.

Program: -5 24 1 - prod 22 quad diff negate 13

Evaluate the whole program. Give the final stack as space-separated integers from TOP (first) to BOTTOM (last); the answer is exactly that space-separated list.

**Answer**: 13 -5
