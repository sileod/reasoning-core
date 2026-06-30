# Task Influence

Updated: 2026-06-30 09:25 UTC

Lower delta means the task reduced held-out loss versus the baseline. `influence_score` is the weighted mean of `-delta`, so positive means the task helped on the weighted targets. Default target weights: bbh=1, dolci=1, flan=0, fw=1

Profile: `dolci`.

Influence files: 2. Saturation files: 3. Contrastive influence files: 1. Local task checks: 12/12 ok.

Saturation accuracy is diagnostic and is not part of the score.

## Ranking

| # | task | influence_score | contrastive_score | flan_delta | bbh_delta | fw_delta | acc_start | acc_end | prompt_tok | answer_tok | modified | hash | issue |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | game_forced_win | +0.154 | +0.109 | -0.0681 | -0.4569 | -0.0013 | 0.000 | 0.738 | 127.5 | 1.0 | 2026-06-29 15:02 UTC | ebd1ce65f6b44ed5 |  |
| 2 | multistep_nli | +0.143 | +0.104 | -0.0696 | -0.4267 | +0.0015 | 0.000 | 0.731 | 168.8 | 13.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 3 | table_equivalence | +0.122 |  | -0.0323 | -0.3677 | -0.0019 | 0.000 | 0.762 | 178.5 | 1.0 | 2026-06-30 09:25 UTC | 830dbc7a45a4813d |  |
| 4 | game_best_move | +0.108 | +0.104 | -0.0495 | -0.3225 | +0.0004 | 0.029 | 0.817 | 126.0 | 2.0 | 2026-06-29 15:02 UTC | ebd1ce65f6b44ed5 |  |
| 5 | multistep_abduction | +0.102 | +0.093 | -0.0400 | -0.3008 | +0.0006 | 0.000 | 0.681 | 122.5 | 1.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 6 | logic_qa | +0.094 | +0.087 | -0.0387 | -0.2820 | +0.0021 | 0.130 | 0.805 | 148.5 | 54.8 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 7 | table_qa | +0.094 |  | -0.0283 | -0.2834 | +0.0004 | 0.351 | 0.649 | 140.0 | 12.2 | 2026-06-30 09:25 UTC | 830dbc7a45a4813d |  |
| 8 | analogical_case_retrieval | +0.072 | +0.086 | -0.0371 | -0.2188 | -0.0016 | 0.324 | 0.747 | 256.0 | 7.0 | 2026-06-29 09:34 UTC | 4b703eedcda1b4ca |  |
| 9 | lambda_reduction | +0.056 | +0.075 | -0.0214 | -0.1690 | -0.0001 | 0.284 | 0.714 | 111.2 | 12.2 | 2026-06-29 09:18 UTC | da074542ea9f5644 |  |
| 10 | multistep_evidence_retrieval | +0.054 | +0.095 | -0.0314 | -0.1576 | -0.0026 | 0.212 | 0.806 | 233.8 | 59.0 | 2026-06-29 09:54 UTC | 3cd7ee827f337ad5 |  |
| 11 | set_expression | +0.049 | +0.080 | -0.0181 | -0.1492 | -0.0025 | 0.346 | 0.755 | 68.8 | 10.2 | 2026-06-29 09:59 UTC | 657c1f4a98174d26 |  |
| 12 | table_statistics | +0.009 |  | -0.0016 | -0.0327 | -0.0047 | 0.214 | 0.214 | 403.8 | 2.0 | 2026-06-30 09:25 UTC | 830dbc7a45a4813d |  |

## Target Deltas

| task | bbh_delta | dolci_delta | flan_delta | fw_delta |
|---|---|---|---|---|
| game_forced_win | -0.4569 | -0.0027 | -0.0681 | -0.0013 |
| multistep_nli | -0.4267 | -0.0042 | -0.0696 | +0.0015 |
| table_equivalence | -0.3677 | +0.0048 | -0.0323 | -0.0019 |
| game_best_move | -0.3225 | -0.0031 | -0.0495 | +0.0004 |
| multistep_abduction | -0.3008 | -0.0043 | -0.0400 | +0.0006 |
| logic_qa | -0.2820 | -0.0023 | -0.0387 | +0.0021 |
| table_qa | -0.2834 | +0.0015 | -0.0283 | +0.0004 |
| analogical_case_retrieval | -0.2188 | +0.0043 | -0.0371 | -0.0016 |
| lambda_reduction | -0.1690 | +0.0006 | -0.0214 | -0.0001 |
| multistep_evidence_retrieval | -0.1576 | -0.0013 | -0.0314 | -0.0026 |
| set_expression | -0.1492 | +0.0050 | -0.0181 | -0.0025 |
| table_statistics | -0.0327 | +0.0116 | -0.0016 | -0.0047 |

## Inputs

Influence runs:
- `influence_TABLETASKS0630_S43_T300_M20_dolci_pretrained.json`
- `influence_TASKQUALITY_S43_T300_M20_dolci_pretrained.json`

Saturation runs:
- `sat_TABLETASKS0630_S43_T300_M20_dolci_pretrained.json`
- `sat_TASKQUALITY_CONTRAST_S43_T300_M20_dolci_pretrained.json`
- `sat_TASKQUALITY_S43_T300_M20_dolci_pretrained.json`

Contrastive influence runs:
- `influence_TASKQUALITY_CONTRAST_S43_T300_M20_dolci_pretrained.json`

