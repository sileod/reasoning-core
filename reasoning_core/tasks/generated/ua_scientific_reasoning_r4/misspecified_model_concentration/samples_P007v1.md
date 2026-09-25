# Level 0

## Example 1

We observe data drawn from a true law g over the support ({0, 1, 2, 3}) with probabilities (0.1741, 0.2458, 0.2701, 0.3100). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.240, 0.357, 0.403) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Rising

## Example 2

We observe data drawn from a true law g over the support ({0, 1, 2, 3}) with probabilities (0.3156, 0.3959, 0.2067, 0.0818). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.181, 0.362, 0.457) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Poisson

# Level 2

## Example 1

We observe data drawn from a true law g over the support ({0, 1, 2, 3, 4, 5}) with probabilities (0.8470, 0.1164, 0.0271, 0.0079, 0.0015, 0.0001). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.165, 0.343, 0.492) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Geometric

## Example 2

We observe data drawn from a true law g over the support ({0, 1, 2, 3, 4, 5}) with probabilities (0.0736, 0.1025, 0.4681, 0.2393, 0.0871, 0.0294). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.268, 0.281, 0.450) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Poisson

# Level 5

## Example 1

We observe data drawn from a true law g over the support ({0, 1, 2, 3, 4, 5, 6, 7, 8}) with probabilities (0.0063, 0.0921, 0.1873, 0.0497, 0.0661, 0.3241, 0.0221, 0.2360, 0.0162). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.159, 0.362, 0.479) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Poisson

## Example 2

We observe data drawn from a true law g over the support ({0, 1, 2, 3, 4, 5, 6, 7, 8}) with probabilities (0.8858, 0.0798, 0.0206, 0.0064, 0.0067, 0.0006, 0.0000, 0.0000, 0.0000). The true law lies outside all candidate families below. Rival predictive models are the following parametric families over that support (each fitted freely within its family; prior masses are (0.260, 0.354, 0.386) and do not affect which families win asymptotically):
- Geometric: p(i) = (1-a) a^i, 0<a<1.
- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.
- Rising: p(i) proportional to a^(K-1-i), 0<a<1.
For each family compute its maximized expected log likelihood ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log evidence). Asymptotically the posterior concentrates on the family or families whose ELBO is maximal (K-L projection closest to g). Report the families tied for the maximum as a comma-separated list sorted alphabetically; a single surviving family is reported alone, e.g. "Poisson"; a tie of two is "Geometric,Poisson".

Answer:

Geometric
