## Level 0
### Example
**Prompt:**

We have a word equation over the alphabet {ab}. The variables are (z, y); each would be replaced by a string of length at most 2 (possibly empty) over {ab}. Determine whether any substitution of the variables makes bbzb = a hold as concatenated strings. If none works, answer unsat; otherwise answer satisfiable.

**Answer:**

unsat

### Example
**Prompt:**

We have a word equation over the alphabet {ab}. The variables are (z, y); each is to be replaced by a string of length at most 2 (possibly empty) over {ab}. How many distinct substitutions make zy = ba hold as concatenated strings? Answer with that count, a single non-negative integer.

**Answer:**

3

## Level 2
### Example
**Prompt:**

We have a word equation over the alphabet {abc}. The variables are (z, y, x); each is to be replaced by a string of length at most 3 (possibly empty) over {abc}. How many distinct substitutions make zyx = c hold as concatenated strings? Answer with that count, a single non-negative integer.

**Answer:**

3

### Example
**Prompt:**

We have a word equation over the alphabet {abc}. The variables are (z, y, x); each is to be replaced by a string of length at most 3 (possibly empty) over {abc}. How many distinct substitutions make zyx = cacaa hold as concatenated strings? Answer with that count, a single non-negative integer.

**Answer:**

12

## Level 5
### Example
**Prompt:**

We have a word equation over the alphabet {abc}. The variables are (z, y, x); each would be replaced by a string of length at most 3 (possibly empty) over {abc}. Determine whether any substitution of the variables makes bxacx = caxzazb hold as concatenated strings. If none works, answer unsat; otherwise answer satisfiable.

**Answer:**

unsat

### Example
**Prompt:**

We have a word equation over the alphabet {abc}. The variables are (z, y, x); each is to be replaced by a string of length at most 3 (possibly empty) over {abc}. There is exactly one substitution that makes xyyzaxbycc = accbccbaaabccbcc hold as concatenated strings. Find it and give each binding as var=string in alphabetical order of the variable names, entries separated by commas; the empty string is written as var= with nothing after the equals sign. Example: a=,b=ba would bind a to the empty string and b to ba.

**Answer:**

x=a,y=ccb,z=a

