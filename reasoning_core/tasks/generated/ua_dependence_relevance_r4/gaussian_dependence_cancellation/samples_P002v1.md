# Level 0

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1. Its covariance matrix is
\begin{pmatrix}
1/9 & -2/9 & -1/9 \\
-2/9 & 13/9 & 20/9 \\
-1/9 & 20/9 & 38/9 \\
\end{pmatrix}
No variables are latent, so nothing is marginalized out; the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z1? Answer exactly with the single word 'yes' or 'no'.

Answer:
no

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1. Its covariance matrix is
\begin{pmatrix}
10/9 & -1/6 & 1/3 \\
-1/6 & 13/4 & -1/2 \\
1/3 & -1/2 & 1 \\
\end{pmatrix}
No variables are latent, so nothing is marginalized out; the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z1? Answer exactly with the single word 'yes' or 'no'.

Answer:
yes

# Level 2

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1, Z2, Z3. Its covariance matrix is
\begin{pmatrix}
23/8 & 1/6 & 0 & 0 & -1/2 \\
1/6 & 83/27 & 0 & 0 & -2/9 \\
0 & 0 & 2/3 & 0 & 0 \\
0 & 0 & 0 & 5/2 & 0 \\
-1/2 & -2/9 & 0 & 0 & 2/3 \\
\end{pmatrix}
The latent variables Z2, Z3 are marginalized out (integrated over); the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z1? Answer exactly with the single word 'yes' or 'no'.

Answer:
no

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1, Z2, Z3. Its covariance matrix is
\begin{pmatrix}
128/375 & 3/25 & 0 & 1/25 & 0 \\
3/25 & 11/5 & 0 & 3/5 & 0 \\
0 & 0 & 3/5 & 0 & 0 \\
1/25 & 3/5 & 0 & 1/5 & 0 \\
0 & 0 & 0 & 0 & 1 \\
\end{pmatrix}
The latent variable Z2 is marginalized out (integrated over); the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z1, Z3? Answer exactly with the single word 'yes' or 'no'.

Answer:
no

# Level 5

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1, Z2, Z3, Z4, Z5, Z6. Its covariance matrix is
\begin{pmatrix}
53/96 & -7/4 & 0 & 0 & -7/8 & 0 & 0 & 0 \\
-7/4 & 18 & 0 & 0 & 7 & 0 & 0 & 0 \\
0 & 0 & 7/2 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
-7/8 & 7 & 0 & 0 & 7/2 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 7/3 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 3/7 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 3/4 \\
\end{pmatrix}
The latent variable Z6 is marginalized out (integrated over); the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z2, Z3? Answer exactly with the single word 'yes' or 'no'.

Answer:
yes

Prompt:
Consider a zero-mean multivariate Gaussian over variables X, Y, Z1, Z2, Z3, Z4, Z5, Z6. Its covariance matrix is
\begin{pmatrix}
195/16 & -49/4 & 0 & 0 & 0 & 0 & 21/4 & 0 \\
-49/4 & 257/15 & 0 & 0 & 0 & 0 & -7 & 0 \\
0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 2/5 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 6 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 4 & 0 & 0 \\
21/4 & -7 & 0 & 0 & 0 & 0 & 3 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 1/2 \\
\end{pmatrix}
The latent variables Z1, Z2, Z4, Z5 are marginalized out (integrated over); the other variables are observed. Decide whether the queried conditional independence holds exactly, under rational arithmetic.
Is X independent of Y given Z3, Z6? Answer exactly with the single word 'yes' or 'no'.

Answer:
no
