# Samples for `selective_evidence_conditioning` (P005v1)

## Level 0

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..4: under A, P(X=v) is proportional to the weight list [1, 4, 12, 8]; under B, proportional to [4, 6, 8, 2].
> There are 2 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=2. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=3. That winner was selected because it was the maximum among the screened findings.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `12/25`

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..4: under A, P(X=v) is proportional to the weight list [16, 3, 4, 3]; under B, proportional to [4, 2, 6, 12].
> There are 2 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=2. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=3. That winner was selected because it was the maximum among the screened findings.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `304/169`

## Level 2

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..6: under A, P(X=v) is proportional to the weight list [6, 5, 4, 6, 6, 4]; under B, proportional to [1, 2, 3, 8, 15, 24].
> There are 4 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=4. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=5. In selective follow-up, the winner alone was remeasured, giving an independent replicate statistic r=2.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `11291278311/229033208`

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..6: under A, P(X=v) is proportional to the weight list [12, 20, 16, 6, 2, 4]; under B, proportional to [2, 8, 12, 8, 5, 24].
> There are 4 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=4. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=5. In selective follow-up, the winner alone was remeasured, giving an independent replicate statistic r=2.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `2144772897/400000000`

## Level 5

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..9: under A, P(X=v) is proportional to the weight list [36, 8, 14, 12, 20, 4, 12, 4, 4]; under B, proportional to [4, 2, 6, 8, 20, 6, 28, 16, 36].
> There are 7 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=7. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=7. In selective follow-up, the winner alone was remeasured, giving an independent replicate statistic r=5.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `174728890890301004901/2514176853161978449`

**Prompt:**

> A candidate finding produces an integer test statistic X drawn from one of two models, hypothesis A or hypothesis B, with equal prior odds. The statistic ranges over values 1..9: under A, P(X=v) is proportional to the weight list [4, 8, 9, 8, 15, 6, 28, 32, 9]; under B, proportional to [36, 32, 21, 12, 15, 4, 12, 8, 1].
> There are 7 independent findings. A finding is screened for inspection only if its statistic is at least the threshold t=7. Among the inspected findings, the one with the largest statistic is selected as the winner for follow-up.
> The winner's statistic was recorded as w=7. In selective follow-up, the winner alone was remeasured, giving an independent replicate statistic r=7.
> Conditioning all evidence on the selection rule (the threshold screening and the winner being the maximum; note the other findings were each strictly below w), report the conditional likelihood ratio favoring hypothesis A over hypothesis B, P(data | A) / P(data | B).
> Answer as a reduced fraction p/q, e.g. 7/3, or a single integer if it is whole.

**Answer:** `372051354090015625/3361549873873752064`
