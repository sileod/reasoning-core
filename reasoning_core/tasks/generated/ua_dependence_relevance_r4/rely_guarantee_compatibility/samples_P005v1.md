## Level 0

### Prompt 1

We have a compositional system of finite-state components sharing variables.
The shared variables are: u, x.
Component C0 guarantees variables: u; the variables it assumes its environment (the other components, not itself) maintains are: u, x.
Component C1 guarantees variables: none; the variables it assumes its environment (the other components, not itself) maintains are: u.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** u

### Prompt 2

We have a compositional system of finite-state components sharing variables.
The shared variables are: y, z.
Component C0 guarantees variables: none; the variables it assumes its environment (the other components, not itself) maintains are: z.
Component C1 guarantees variables: y; the variables it assumes its environment (the other components, not itself) maintains are: y, z.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** z



## Level 2

### Prompt 1

We have a compositional system of finite-state components sharing variables.
The shared variables are: u, v, y.
Component C0 guarantees variables: u, y; the variables it assumes its environment (the other components, not itself) maintains are: u, v, y.
Component C1 guarantees variables: v, y; the variables it assumes its environment (the other components, not itself) maintains are: u, v.
Component C2 guarantees variables: y; the variables it assumes its environment (the other components, not itself) maintains are: v, y.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** u

### Prompt 2

We have a compositional system of finite-state components sharing variables.
The shared variables are: v, x, y.
Component C0 guarantees variables: v, y; the variables it assumes its environment (the other components, not itself) maintains are: v, y.
Component C1 guarantees variables: v, y; the variables it assumes its environment (the other components, not itself) maintains are: x, y.
Component C2 guarantees variables: v, x; the variables it assumes its environment (the other components, not itself) maintains are: v, y.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** none



## Level 5

### Prompt 1

We have a compositional system of finite-state components sharing variables.
The shared variables are: p, v, w, x, z.
Component C0 guarantees variables: w, x, z; the variables it assumes its environment (the other components, not itself) maintains are: p, v, z.
Component C1 guarantees variables: v, x; the variables it assumes its environment (the other components, not itself) maintains are: p, w, z.
Component C2 guarantees variables: p, w, x; the variables it assumes its environment (the other components, not itself) maintains are: p, w, z.
Component C3 guarantees variables: p, x; the variables it assumes its environment (the other components, not itself) maintains are: p, v, x.
Component C4 guarantees variables: p, v, x; the variables it assumes its environment (the other components, not itself) maintains are: v, w, z.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** z

### Prompt 2

We have a compositional system of finite-state components sharing variables.
The shared variables are: p, u, v, x, z.
Component C0 guarantees variables: v, x; the variables it assumes its environment (the other components, not itself) maintains are: p, u, v, z.
Component C1 guarantees variables: u, v, x; the variables it assumes its environment (the other components, not itself) maintains are: p, u, v, z.
Component C2 guarantees variables: p, u, v; the variables it assumes its environment (the other components, not itself) maintains are: u, v, x, z.
Component C3 guarantees variables: u, x, z; the variables it assumes its environment (the other components, not itself) maintains are: p, u, v, z.
Component C4 guarantees variables: u, v; the variables it assumes its environment (the other components, not itself) maintains are: p, u, x, z.
A component's assumption is satisfied only if the variable it assumes is guaranteed by at least one other component. An assumption of a shared variable that no peer guarantees is a failed compatibility obligation.
Identify the first failed compatibility obligation: among every component/assumed-variable pair that is not guaranteed by any peer, name the variable v of the pair with the smallest component index (ties broken by lexicographically smallest variable). If no assumption is violated, answer 'none'.
Answer with exactly one variable name (e.g. 'x') or the word 'none'.


**Answer:** z


