# samples_P003v1

## Level 0

### Example 1

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 9]. A quantizer processes each input as follows: first compute f(x) = clip(1/1*x + 0, 0, 3) (clip below and above), then wrap z = f(x) mod 3 into [0, 3), then assign code = floor(z / 1/1) where the step 1/1 = P / 3, giving codes 3 per wrap. What fraction of the input interval [0, 9] yields output code 1? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 1/9

### Example 2

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 14]. A quantizer processes each input as follows: first compute f(x) = clip(1/2*x + 1, 0, 2) (clip below and above), then wrap z = f(x) mod 2 into [0, 2), then assign code = floor(z / 2/3) where the step 2/3 = P / 3, giving codes 3 per wrap. What fraction of the input interval [0, 14] yields output code 1? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 1/21

## Level 2

### Example 1

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 19]. A quantizer processes each input as follows: first compute f(x) = clip(1/3*x + 7, 0, 15) (clip below and above), then wrap z = f(x) mod 5 into [0, 5), then assign code = floor(z / 1/1) where the step 1/1 = P / 5, giving codes 5 per wrap. What fraction of the input interval [0, 19] yields output code 1? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 3/19

### Example 2

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 25]. A quantizer processes each input as follows: first compute f(x) = clip(1/1*x + 6, 0, 18) (clip below and above), then wrap z = f(x) mod 6 into [0, 6), then assign code = floor(z / 6/5) where the step 6/5 = P / 5, giving codes 5 per wrap. What fraction of the input interval [0, 25] yields output code 1? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 12/125

## Level 5

### Example 1

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 41]. A quantizer processes each input as follows: first compute f(x) = clip(3/2*x + 7, 0, 42) (clip below and above), then wrap z = f(x) mod 7 into [0, 7), then assign code = floor(z / 7/8) where the step 7/8 = P / 8, giving codes 8 per wrap. What fraction of the input interval [0, 41] yields output code 0? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 35/492

### Example 2

**Prompt:**

Inputs x are chosen uniformly in the interval [0, 35]. A quantizer processes each input as follows: first compute f(x) = clip(7/6*x + -11, 0, 54) (clip below and above), then wrap z = f(x) mod 9 into [0, 9), then assign code = floor(z / 9/8) where the step 9/8 = P / 8, giving codes 8 per wrap. What fraction of the input interval [0, 35] yields output code 3? Give your answer as a reduced fraction of the total interval length, e.g. 3/4.

**Answer:** 81/980
