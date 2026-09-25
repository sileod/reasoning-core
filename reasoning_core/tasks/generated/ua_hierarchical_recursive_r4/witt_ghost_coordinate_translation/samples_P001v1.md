# Level 0
## Example 1 (big, mode to_ghost)
Prompt:
```
You are given a truncated big Witt vector with coordinates a_1..a_3 with integer Witt coordinates (a_1, ..., a_3) = (-1,1,0). Its ghost components are w_m = sum_{(d | m)} d * a_d^(m/d) for m = 1..3. Compute the ghost component vector (w_1, ..., w_3). Answer as a comma-separated list of integers in order, e.g. '3,-5,10'.
```
Answer:
```
-1,3,-1
```

## Example 2 (big, mode to_ghost)
Prompt:
```
You are given a truncated big Witt vector with coordinates a_1..a_3 with integer Witt coordinates (a_1, ..., a_3) = (1,1,-1). Its ghost components are w_m = sum_{(d | m)} d * a_d^(m/d) for m = 1..3. Compute the ghost component vector (w_1, ..., w_3). Answer as a comma-separated list of integers in order, e.g. '3,-5,10'.
```
Answer:
```
1,3,-2
```

# Level 2
## Example 1 (big, mode to_ghost)
Prompt:
```
You are given a truncated big Witt vector with coordinates a_1..a_3 with integer Witt coordinates (a_1, ..., a_3) = (1,1,1). Its ghost components are w_m = sum_{(d | m)} d * a_d^(m/d) for m = 1..3. Compute the ghost component vector (w_1, ..., w_3). Answer as a comma-separated list of integers in order, e.g. '3,-5,10'.
```
Answer:
```
1,3,4
```

## Example 2 (big, mode to_ghost)
Prompt:
```
You are given a truncated big Witt vector with coordinates a_1..a_3 with integer Witt coordinates (a_1, ..., a_3) = (-1,1,3). Its ghost components are w_m = sum_{(d | m)} d * a_d^(m/d) for m = 1..3. Compute the ghost component vector (w_1, ..., w_3). Answer as a comma-separated list of integers in order, e.g. '3,-5,10'.
```
Answer:
```
-1,3,8
```

# Level 5
## Example 1 (p_typical, mode obstruction)
Prompt:
```
You are given ghost components (w_0, ..., w_5) = (1,4,3,11,27,-197) of a truncated p-typical Witt vector with p=2, truncated to 6 coordinates, and the integer Witt coordinates (a_0, ..., a_5) below them must satisfy w_i = sum_{(j=0)}^i p^j * a_j^(p^(i-j)). For each i the coordinate a_i is obtained as (w_i - sum_{(j<i)} p^j * a_j^(p^(i-j))) / p^i and is an integer only if that division by p^i is exact. Identify the FIRST index (counting a_0 as index 1) at which this required divisibility by p^i fails. Answer with that single 1-based integer index.
```
Answer:
```
2
```

## Example 2 (big, mode obstruction)
Prompt:
```
You are given ghost components (w_1, ..., w_3) = (1,2,22) of a truncated big Witt vector with coordinates a_1..a_3, and the integer Witt coordinates (a_1, ..., a_3) below them must satisfy w_m = sum_{(d | m)} d * a_d^(m/d). For each m the coordinate a_m is obtained as (w_m - sum_{(d | m, d<m)} d * a_d^(m/d)) / m and is an integer only if that division by m is exact. Identify the FIRST index m at which this required divisibility by m fails. Answer with that single 1-based integer index.
```
Answer:
```
2
```
