## Level 0

Prompt:
```
Let S = {0,1,2,3,4} and let F = {{1,2} {0,1,2} {0,1,3} {3,4} {0,1,3,4} {0,2,3,4}} be a set family on S. Does F shatter the subset T = {1} of S? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
shatter
```

Prompt:
```
Let S = {0,1,2,3,4} and let F = {{0} {1,2} {3} {2,3} {0,4} {0,1,2,4}} be a set family on S. Does F shatter the ground set S = {0,1,2,3,4}? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
not-shatter
```


## Level 2

Prompt:
```
Let S = {0,1,2,3,4,5,6,7,8} and let F = {{2,4,5} {6,7} {5,6,7} {1,5,7,8} {1,2,3,6,7,8} {4,6,7,8} {1,2,3,5,6,7,8} {0,3,4,5,6,7,8}} be a set family on S. Does F strongly shatter the set T = {0,4,6}? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
not-strong-shatter
```

Prompt:
```
Let S = {0,1,2,3,4,5,6,7,8} and let F = {{0,1,3,4,5,6} {1,3,5,7} {2,3,5,6,7} {2,7,8} {0,1,5,7,8} {0,1,2,5,7,8} {1,3,5,7,8} {1,2,3,4,5,7,8}} be a set family on S. Does F shatter the subset T = {2,3} of S? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
shatter
```


## Level 5

Prompt:
```
Let S = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14} and let F = {{8,10} {0,1,2,3,4,5,6,7,8,9,10,11,12} {0,1,2,3,7,8,13} {2,3,4,6,7,8,13} {0,1,2,4,7,12,13} {0,3,7,8,9,12,13} {7,10,11,12,14} {0,2,3,4,5,7,13,14} {0,4,5,6,8,11,13,14} {4,5,8,9,11,13,14} {0,2,3,5,6,7,12,13,14}} be a set family on S. Does F shatter the subset T = {1,4,9,11} of S? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
missing-trace
```

Prompt:
```
Let S = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14} and let F = {{5,6,8,11} {2,4,5,8,9,11} {5,7,8,10,11} {2,3,5,10,11,12} {3,13} {1,5,7,10,11,13} {0,1,2,3,4,8,10,11,13} {0,1,4,5,8,12,13} {2,3,5,6,7,9,11,14} {1,3,4,5,7,8,11,12,14} {1,2,3,4,5,6,10,11,12,14}} be a set family on S. Does F shatter the subset T = {0,2,8} of S? Answer with exactly one token from {{shatter, not-shatter, strong-shatter, not-strong-shatter, missing-trace}}. For a shatter query answer shatter or not-shatter. For a strong shatter query answer strong-shatter or not-strong-shatter. If the family fails to shatter the queried set, answer missing-trace only when asked to name a missing trace; otherwise use not-shatter. A set family F shatters a set T if for every subset A of T there is a member Fw of F whose intersection with T equals A. F strongly shatters T if those witnesses can be chosen monotonically: for subsets A subset B of T the witness for A is a subset of the witness for B (A and B may be empty).
```
Answer:
```
missing-trace
```

