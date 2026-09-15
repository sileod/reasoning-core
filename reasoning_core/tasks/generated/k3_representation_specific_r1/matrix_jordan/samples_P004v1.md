## Level 0
### Example 1
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 3
Matrix:
[1, 0]
[0, 2]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=1:blk=[1];eig=2:blk=[1]
```

### Example 2
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 3
Matrix:
[2, 1]
[0, 2]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=2:blk=[2]
```

## Level 2
### Example 1
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 11
Matrix:
[0, 0, 0, 0]
[0, 4, 0, 0]
[0, 0, 8, 0]
[0, 0, 0, 10]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=0:blk=[1];eig=4:blk=[1];eig=8:blk=[1];eig=10:blk=[1]
```

### Example 2
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 5
Matrix:
[4, 1, 0, 0]
[0, 4, 0, 0]
[0, 0, 4, 0]
[0, 0, 0, 4]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=4:blk=[2, 1, 1]
```

## Level 5
### Example 1
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 17
Matrix:
[2, 0, 0, 0, 0, 0, 0]
[0, 2, 0, 0, 0, 0, 0]
[0, 0, 3, 0, 0, 0, 0]
[0, 0, 0, 4, 0, 0, 0]
[0, 0, 0, 0, 8, 0, 0]
[0, 0, 0, 0, 0, 12, 0]
[0, 0, 0, 0, 0, 0, 13]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=2:blk=[1, 1];eig=3:blk=[1];eig=4:blk=[1];eig=8:blk=[1];eig=12:blk=[1];eig=13:blk=[1]
```

### Example 2
**Prompt:**
```
The following matrix over the field GF(p) has a characteristic polynomial that splits completely over GF(p).
p = 11
Matrix:
[2, 1, 0, 0, 0, 0, 0]
[0, 2, 0, 0, 0, 0, 0]
[0, 0, 4, 1, 0, 0, 0]
[0, 0, 0, 4, 0, 0, 0]
[0, 0, 0, 0, 5, 0, 0]
[0, 0, 0, 0, 0, 7, 0]
[0, 0, 0, 0, 0, 0, 7]

Give the Jordan normal form as a semicolon-separated list of per-eigenvalue entries, one per distinct eigenvalue, each of the form eig=<lambda>:blk=[<block sizes>], where eigenvalues are sorted ascending and the Jordan block sizes for each eigenvalue are listed in descending order. The answer is exactly that string.
```
**Answer:**
```
eig=2:blk=[2];eig=4:blk=[2];eig=5:blk=[1];eig=7:blk=[1, 1]
```

