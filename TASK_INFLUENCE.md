# Task Influence

Updated: 2026-06-30 07:44 UTC

Lower delta means the task reduced held-out loss versus the baseline. `influence_score` is the weighted mean of `-delta`, so positive means the task helped on the weighted targets. Default target weights: bbh=1, dolci=1, flan=0, fw=1

Profile: `dolci`.

Influence files: 1. Saturation files: 2. Contrastive influence files: 1. Local task checks: 10/10 ok.

Saturation accuracy is diagnostic and is not part of the score.

## Ranking

| # | task | influence_score | contrastive_score | flan_delta | bbh_delta | fw_delta | acc_start | acc_end | prompt_tok | answer_tok | modified | hash | issue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | game_forced_win | +0.154 | +0.109 | -0.0681 | -0.4569 | -0.0013 | 0.000 | 0.738 | 125.2 | 1.0 | 2026-06-29 15:02 UTC | ebd1ce65f6b44ed5 |  |
| 2 | multistep_nli | +0.143 | +0.104 | -0.0696 | -0.4267 | +0.0015 | 0.000 | 0.731 | 194.2 | 14.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 3 | game_best_move | +0.108 | +0.104 | -0.0495 | -0.3225 | +0.0004 | 0.029 | 0.817 | 128.8 | 2.0 | 2026-06-29 15:02 UTC | ebd1ce65f6b44ed5 |  |
| 4 | multistep_abduction | +0.102 | +0.093 | -0.0400 | -0.3008 | +0.0006 | 0.000 | 0.681 | 126.8 | 1.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 5 | logic_qa | +0.094 | +0.087 | -0.0387 | -0.2820 | +0.0021 | 0.130 | 0.805 | 169.5 | 75.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 6 | stress_constrained_continuation | +0.080 | +0.080 | -0.0370 | -0.2402 | +0.0007 | 0.179 | 0.704 | 186.8 | 8.2 | 2026-06-29 09:41 UTC | 169a9ebe536d45fc |  |
| 7 | analogical_case_retrieval | +0.072 | +0.086 | -0.0371 | -0.2188 | -0.0016 | 0.324 | 0.747 | 256.0 | 7.0 | 2026-06-29 09:34 UTC | 4b703eedcda1b4ca |  |
| 8 | lambda_reduction | +0.056 | +0.075 | -0.0214 | -0.1690 | -0.0001 | 0.284 | 0.714 | 125.2 | 20.8 | 2026-06-29 09:18 UTC | da074542ea9f5644 |  |
| 9 | multistep_evidence_retrieval | +0.054 | +0.095 | -0.0314 | -0.1576 | -0.0026 | 0.212 | 0.806 | 227.2 | 58.2 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 10 | set_expression | +0.049 | +0.080 | -0.0181 | -0.1492 | -0.0025 | 0.346 | 0.755 | 88.5 | 11.8 | 2026-06-29 09:59 UTC | 657c1f4a98174d26 |  |

## Target Deltas

| task | bbh_delta | dolci_delta | flan_delta | fw_delta |
|---|---|---|---|---|
| game_forced_win | -0.4569 | -0.0027 | -0.0681 | -0.0013 |
| multistep_nli | -0.4267 | -0.0042 | -0.0696 | +0.0015 |
| game_best_move | -0.3225 | -0.0031 | -0.0495 | +0.0004 |
| multistep_abduction | -0.3008 | -0.0043 | -0.0400 | +0.0006 |
| logic_qa | -0.2820 | -0.0023 | -0.0387 | +0.0021 |
| stress_constrained_continuation | -0.2402 | +0.0005 | -0.0370 | +0.0007 |
| analogical_case_retrieval | -0.2188 | +0.0043 | -0.0371 | -0.0016 |
| lambda_reduction | -0.1690 | +0.0006 | -0.0214 | -0.0001 |
| multistep_evidence_retrieval | -0.1576 | -0.0013 | -0.0314 | -0.0026 |
| set_expression | -0.1492 | +0.0050 | -0.0181 | -0.0025 |

## Inputs

Influence runs:
- `influence_TASKQUALITY_S43_T300_M20_dolci_pretrained.json`

Saturation runs:
- `sat_TASKQUALITY_CONTRAST_S43_T300_M20_dolci_pretrained.json`
- `sat_TASKQUALITY_S43_T300_M20_dolci_pretrained.json`

Contrastive influence runs:
- `influence_TASKQUALITY_CONTRAST_S43_T300_M20_dolci_pretrained.json`

