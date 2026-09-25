## Level 0

### Example 1

Prompt:

An oversized strip that is 4 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [1, 3, 3, 2]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 1 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 1 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 2

### Example 2

Prompt:

An oversized strip that is 4 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [2, 3, 3, 2]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 2 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 2 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 0

## Level 2

### Example 1

Prompt:

An oversized strip that is 16 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [4, 2, 1, 4, 1, 5, 3, 4, 5, 1, 4, 1, 5, 3, 3, 1]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 2 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 2 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 7

### Example 2

Prompt:

An oversized strip that is 16 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [1, 1, 5, 5, 4, 2, 4, 2, 1, 3, 5, 1, 2, 1, 1, 1]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 1 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 1 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 12

## Level 5

### Example 1

Prompt:

An oversized strip that is 128 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [6, 1, 2, 5, 3, 6, 6, 4, 5, 2, 3, 2, 5, 7, 6, 7, 4, 6, 4, 5, 1, 4, 3, 5, 2, 5, 6, 4, 2, 7, 1, 7, 5, 7, 4, 8, 6, 6, 4, 5, 1, 3, 7, 1, 2, 3, 4, 2, 8, 1, 8, 1, 7, 7, 1, 8, 8, 1, 1, 7, 5, 5, 8, 8, 8, 5, 4, 8, 7, 5, 5, 1, 2, 3, 6, 7, 3, 6, 4, 7, 1, 6, 4, 4, 2, 7, 8, 7, 7, 3, 7, 3, 5, 3, 8, 8, 2, 1, 4, 3, 7, 5, 8, 7, 4, 3, 2, 5, 7, 3, 3, 8, 1, 3, 4, 7, 2, 4, 2, 6, 7, 7, 7, 6, 6, 8, 8, 2]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 1 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 1 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 69

### Example 2

Prompt:

An oversized strip that is 128 columns wide sits on top of a row of neighbor cells. Reading left to right the neighbor cell areas directly below the strip are [2, 8, 5, 6, 4, 8, 1, 5, 2, 7, 7, 7, 8, 4, 5, 6, 4, 3, 5, 4, 6, 3, 6, 5, 4, 7, 8, 2, 5, 7, 1, 5, 3, 5, 7, 2, 8, 2, 5, 8, 8, 2, 8, 8, 8, 6, 4, 3, 4, 6, 3, 7, 4, 6, 3, 3, 2, 8, 1, 6, 7, 2, 5, 8, 6, 4, 3, 2, 4, 2, 1, 3, 8, 3, 4, 1, 1, 5, 6, 1, 3, 2, 1, 3, 6, 2, 8, 1, 3, 3, 6, 3, 1, 2, 2, 5, 5, 4, 1, 1, 6, 7, 3, 2, 5, 6, 8, 5, 5, 7, 3, 1, 6, 2, 4, 3, 4, 1, 3, 4, 7, 6, 6, 6, 3, 5, 1, 5]. The strip may be refined only with balanced dyadic bisection: repeatedly pick a current strip interval and cut it exactly in half at its midpoint, producing two pieces each of half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed exactly when its length is at most 3 times the smallest neighbor cell area beneath it, i.e. (b-a) <= 3 * (minimum of the listed areas from column a to column b-1). Every column must end up in exactly one piece. What is the minimum number of bisection cuts needed so that every final strip piece satisfies this neighbor size-ratio limit? Answer with the non-negative integer number of cuts only, nothing else.

Answer: 42

