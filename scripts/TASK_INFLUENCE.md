# Task Influence

Updated: 2026-07-01 04:01 UTC

Lower delta means the task reduced held-out loss versus the baseline. `influence_score` is the weighted mean of `-delta`, so positive means the task helped on the weighted targets. Default target weights: bbh=1, dolci=1, flan=0, fw=1

Profile: `dolci`.

Influence files: 1. Saturation files: 1. Contrastive influence files: 0. Local task checks: 0/50 ok.

Saturation accuracy is diagnostic and is not part of the score.

## Ranking

Lower delta = helped. `score` higher = better helper. `tok` = prompt/answer tokens, `acc` = start→end (both diagnostic). flan delta is in the JSON sidecar.

| # | task | score | dolci | bbh | fw | tok | acc | hash |
|---|---|---|---|---|---|---|---|---|
| 1 | game_forced_win | +0.15 | -0.0017 | -0.460 | -0.0019 |  | 0.00→0.78 | ebd1ce6 |
| 2 | planar_geometry_relations | +0.14 | -0.0028 | -0.422 | -0.0003 |  | 0.29→0.71 | f8127b7 |
| 3 | multistep_nli | +0.14 | -0.0032 | -0.410 | +0.0016 |  | 0.00→0.70 | 3cd7ee8 |
| 4 | logic_nli | +0.13 | -0.0005 | -0.401 | +0.0023 |  | 0.00→0.56 | 4b77c86 |
| 5 | metamath_core_select | +0.13 | -0.0002 | -0.389 | -0.0021 |  | 0.00→0.64 | 3ceb928 |
| 6 | tptp_consistency_repair | +0.12 | -0.0004 | -0.355 | +0.0002 |  | 0.06→0.62 | fec294d |
| 7 | qualitative_reasoning | +0.11 | -0.0026 | -0.340 | +0.0009 |  | 0.20→0.69 | dfb4735 |
| 8 | regex_reasoning | +0.11 | -0.0006 | -0.323 | +0.0012 |  | 0.01→0.21 | 6230448 |
| 9 | game_best_move | +0.11 | -0.0025 | -0.313 | +0.0002 |  | 0.01→0.86 | ebd1ce6 |
| 10 | count_elements | +0.10 | -0.0018 | -0.314 | +0.0029 |  | 0.00→0.59 | 657c1f4 |
| 11 | math_word_problem | +0.10 | -0.0015 | -0.310 | +0.0009 |  | 0.02→0.27 | 598d63b |
| 12 | tptp_entailment | +0.10 | -0.0027 | -0.302 | +0.0022 |  | 0.00→0.66 | fec294d |
| 13 | multistep_abduction | +0.10 | -0.0035 | -0.297 | +0.0010 |  | 0.00→0.55 | 3cd7ee8 |
| 14 | coreference | +0.10 | -0.0022 | -0.300 | +0.0027 |  | 0.21→0.73 | 0041bfe |
| 15 | reference_tracking | +0.10 | -0.0013 | -0.290 | -0.0023 |  | 0.11→0.78 | a9e1b0e |
| 16 | logic_formalization | +0.10 | +0.0030 | -0.296 | +0.0002 |  | 0.00→0.75 | 4b77c86 |
| 17 | navigation | +0.09 | -0.0014 | -0.284 | +0.0018 |  | 0.30→0.78 | 0dc49fa |
| 18 | metamath_entailment | +0.09 | -0.0014 | -0.275 | +0.0007 |  | 0.00→0.80 | 3ceb928 |
| 19 | logic_qa | +0.09 | -0.0020 | -0.274 | +0.0014 |  | 0.28→0.81 | 3cd7ee8 |
| 20 | graph_successors | +0.09 | -0.0004 | -0.270 | -0.0008 |  | 0.00→0.59 | 9b2bff9 |
| 21 | constrained_continuation | +0.09 | -0.0014 | -0.264 | -0.0010 |  | 0.21→0.47 | efadf80 |
| 22 | most_probable_outcome | +0.09 | -0.0002 | -0.260 | -0.0015 |  | 0.00→0.20 | 5cbfb53 |
| 23 | constraint_satisfaction | +0.09 | -0.0015 | -0.260 | +0.0027 |  | 0.42→0.59 | c7a3b3f |
| 24 | evidence_retrieval | +0.08 | -0.0006 | -0.255 | +0.0012 |  | 0.06→0.54 | 4b77c86 |
| 25 | most_probable_evidence | +0.08 | +0.0001 | -0.253 | -0.0007 |  | 0.17→0.75 | 5cbfb53 |
| 26 | equation_system | +0.08 | -0.0016 | -0.250 | -0.0002 |  | 0.14→0.50 | 78d5fb6 |
| 27 | lean_candidate_compilation | +0.08 | +0.0005 | -0.248 | +0.0025 |  | 0.00→0.78 | 58e7849 |
| 28 | graph_dependencies | +0.08 | -0.0001 | -0.245 | +0.0003 |  | 0.25→0.45 | 9b2bff9 |
| 29 | lean_missing_proof_line_selection | +0.08 | -0.0017 | -0.227 | -0.0006 |  | 0.00→0.54 | 58e7849 |
| 30 | rewrite_system | +0.08 | -0.0035 | -0.226 | +0.0005 |  | 0.59→0.76 | da07454 |
| 31 | regex_induction | +0.07 | -0.0014 | -0.216 | -0.0022 |  | 0.07→0.46 | 6230448 |
| 32 | regex_following | +0.07 | -0.0004 | -0.219 | +0.0013 |  | 0.03→0.05 | 6230448 |
| 33 | table_equivalence | +0.07 | +0.0050 | -0.222 | -0.0011 |  | 0.00→0.72 | 830dbc7 |
| 34 | locate_error | +0.07 | -0.0032 | -0.213 | +0.0028 |  | 0.09→0.44 | efadf80 |
| 35 | parsing_derivation | +0.07 | +0.0002 | -0.212 | +0.0008 |  | 0.51→0.66 | efadf80 |
| 36 | code_runnability | +0.07 | -0.0010 | -0.208 | +0.0009 |  | 0.10→0.72 | 83ade9e |
| 37 | analogical_case_retrieval | +0.07 | +0.0056 | -0.207 | -0.0032 |  | 0.63→0.78 | 4b703ee |
| 38 | arithmetics | +0.07 | -0.0013 | -0.202 | +0.0015 |  | 0.15→0.32 | 598d63b |
| 39 | graph_pathfinding | +0.07 | +0.0021 | -0.203 | -0.0001 |  | 0.22→0.68 | 9b2bff9 |
| 40 | lambda_reduction | +0.06 | -0.0007 | -0.194 | +0.0022 |  | 0.51→0.63 | da07454 |
| 41 | code_execution | +0.06 | -0.0013 | -0.182 | -0.0009 |  | 0.19→0.56 | 83ade9e |
| 42 | set_expression | +0.06 | +0.0022 | -0.184 | -0.0008 |  | 0.63→0.74 | 657c1f4 |
| 43 | table_qa | +0.06 | +0.0009 | -0.183 | +0.0003 |  | 0.42→0.65 | 830dbc7 |
| 44 | string_transduction | +0.05 | -0.0002 | -0.160 | +0.0002 |  | 0.09→0.19 | 5dcd3d2 |
| 45 | sequential_induction | +0.05 | -0.0014 | -0.149 | -0.0019 |  | 0.42→0.65 | a679ad1 |
| 46 | table_statistics | +0.05 | +0.0058 | -0.153 | -0.0043 |  | 0.20→0.41 | 830dbc7 |
| 47 | planning | +0.05 | -0.0005 | -0.149 | -0.0014 |  | 0.61→0.83 | 605ba89 |
| 48 | set_missing_element | +0.05 | +0.0007 | -0.148 | -0.0016 |  | 0.58→0.77 | 657c1f4 |
| 49 | multistep_evidence_retrieval | +0.04 | -0.0005 | -0.132 | -0.0020 |  | 0.42→0.88 | 3cd7ee8 |
| 50 | code_input_deduction | +0.02 | +0.0005 | -0.075 | +0.0003 |  | 0.00→0.71 | 83ade9e |

_Inputs: 1 influence + 1 saturation result file(s). Full per-target detail and diagnostics in the JSON sidecar._

