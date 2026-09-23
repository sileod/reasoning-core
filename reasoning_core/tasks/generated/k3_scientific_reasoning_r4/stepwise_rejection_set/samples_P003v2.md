## Level 0
### Example
**Prompt:**

At significance level alpha = 0.01, apply the Holm step-down procedure (sort ascending; at step k reject the k-th smallest while p_(k) <= alpha/(n-k+1), stopping at the first violation) to the following 4 hypotheses and their p-values: H1: p=0.0020, H2: p=0.0027, H3: p=0.8070, H4: p=0.9706. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[1, 2]

### Example
**Prompt:**

At significance level alpha = 0.01, apply the Benjamini-Hochberg procedure (sort ascending; reject the k smallest where k is the largest value with p_(k) <= (k/n)*alpha) to the following 4 hypotheses and their p-values: H1: p=0.3899, H2: p=0.7716, H3: p=0.4203, H4: p=0.0021. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[4]

## Level 2
### Example
**Prompt:**

At significance level alpha = 0.01, apply the Benjamini-Hochberg procedure (sort ascending; reject the k smallest where k is the largest value with p_(k) <= (k/n)*alpha) to the following 8 hypotheses and their p-values: H1: p=0.6197, H2: p=0.0003, H3: p=0.0016, H4: p=0.0207, H5: p=0.0629, H6: p=0.0005, H7: p=0.0015, H8: p=0.0014. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[2, 3, 6, 7, 8]

### Example
**Prompt:**

At significance level alpha = 0.05, apply the Bonferroni correction (reject i when p_i <= alpha/n) to the following 8 hypotheses and their p-values: H1: p=0.3501, H2: p=0.3441, H3: p=0.0086, H4: p=0.0080, H5: p=0.0048, H6: p=0.4148, H7: p=0.7077, H8: p=0.3313. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[5]

## Level 5
### Example
**Prompt:**

At significance level alpha = 0.05, apply the Benjamini-Hochberg procedure (sort ascending; reject the k smallest where k is the largest value with p_(k) <= (k/n)*alpha) to the following 14 hypotheses and their p-values: H1: p=0.0053, H2: p=0.8427, H3: p=0.6839, H4: p=0.3713, H5: p=0.9629, H6: p=0.2893, H7: p=0.4054, H8: p=0.9309, H9: p=0.0035, H10: p=0.7582, H11: p=0.8889, H12: p=0.0005, H13: p=0.2347, H14: p=0.0748. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[1, 9, 12]

### Example
**Prompt:**

At significance level alpha = 0.01, apply the Benjamini-Hochberg procedure (sort ascending; reject the k smallest where k is the largest value with p_(k) <= (k/n)*alpha) to the following 14 hypotheses and their p-values: H1: p=0.6842, H2: p=0.4752, H3: p=0.6175, H4: p=0.2232, H5: p=0.0270, H6: p=0.6584, H7: p=0.8918, H8: p=0.0010, H9: p=0.0009, H10: p=0.6189, H11: p=0.0851, H12: p=0.3839, H13: p=0.6383, H14: p=0.8387. Give the exact set of rejected hypotheses as a sorted list of 1-based indices in ascending order, for example [2, 5]; if none are rejected answer []. Report only that list, nothing else.

**Answer:**

[8, 9]

