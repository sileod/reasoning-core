# Level 0

## Example 1

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 2 levels (z_0..z_{1}) and W has 3 levels (w_0..w_{2}).
For the queried treatment arm a=1, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 2; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.4894, 0.5106
For arm a=1:
   E[Y|A=1,W=w] = [ 0.8029, 0.6526, 0.7661 ]
   P(Z=z|A=1,W=w), rows w_0..w_{2}, columns z_0..z_{1}:
   [0.4556, 0.5444]
   [0.3779, 0.6221]
   [0.4366, 0.5634]
Report E[Y(1)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

0.868

## Example 2

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 2 levels (z_0..z_{1}) and W has 3 levels (w_0..w_{2}).
For the queried treatment arm a=1, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 2; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.6654, 0.3346
For arm a=1:
   E[Y|A=1,W=w] = [ -0.1072, 1.5408, -1.9442 ]
   P(Z=z|A=1,W=w), rows w_0..w_{2}, columns z_0..z_{1}:
   [0.6672, 0.3328]
   [0.6790, 0.3210]
   [0.6541, 0.3459]
Report E[Y(1)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

-0.361

# Level 2

## Example 1

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 2 levels (z_0..z_{1}) and W has 3 levels (w_0..w_{2}).
For the queried treatment arm a=0, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 2; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.7776, 0.2224
For arm a=0:
   E[Y|A=0,W=w] = [ 0.1108, 1.3200, 0.3864 ]
   P(Z=z|A=0,W=w), rows w_0..w_{2}, columns z_0..z_{1}:
   [0.7454, 0.2546]
   [0.7802, 0.2198]
   [0.7533, 0.2467]
Report E[Y(0)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

1.230

## Example 2

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 2 levels (z_0..z_{1}) and W has 1 levels (w_0..w_{0}).
For the queried treatment arm a=1, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 2; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.3826, 0.6174
For arm a=1:
   E[Y|A=1,W=w] = [ -2.9845 ]
   P(Z=z|A=1,W=w), rows w_0..w_{0}, columns z_0..z_{1}:
   [0.3458, 0.6542]
Report E[Y(1)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

nonidentifiable

# Level 5

## Example 1

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 3 levels (z_0..z_{2}) and W has 3 levels (w_0..w_{2}).
For the queried treatment arm a=1, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 3; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.4595, 0.3915, 0.1490
For arm a=1:
   E[Y|A=1,W=w] = [ -1.5237, -2.5290, -2.6194 ]
   P(Z=z|A=1,W=w), rows w_0..w_{2}, columns z_0..z_{2}:
   [0.4954, 0.3843, 0.1202]
   [0.4457, 0.4117, 0.1425]
   [0.4331, 0.4107, 0.1562]
Report E[Y(1)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

-1.989

## Example 2

In an observational study a real-valued outcome Y is treated by a binary treatment A in {0,1}. An unmeasured categorical confounder U confounds A and Y. Two negative-control proxies are observed: an exposure proxy Z whose distribution depends only on U (so Z has no direct effect on Y), and an outcome proxy W whose distribution depends on U and A. Z has 3 levels (z_0..z_{2}) and W has 3 levels (w_0..w_{2}).
For the queried treatment arm a=0, the causal mean E[Y(a)] is recovered through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has full column rank 3; if so compute the bridge and the mean, otherwise E[Y(a)] is nonidentifiable.
Marginal distribution of Z over the population, P(Z=z):
   0.4577, 0.3757, 0.1666
For arm a=0:
   E[Y|A=0,W=w] = [ -0.6548, -0.3977, -0.0575 ]
   P(Z=z|A=0,W=w), rows w_0..w_{2}, columns z_0..z_{2}:
   [0.4577, 0.3757, 0.1666]
   [0.4577, 0.3757, 0.1666]
   [0.4577, 0.3757, 0.1666]
Report E[Y(0)] to three decimals, or the single word 'nonidentifiable' if the full-column-rank condition fails.

Answer:

nonidentifiable
