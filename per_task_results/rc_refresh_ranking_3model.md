# RC refresh — 3-model cloze-mmlu ranking (staging cache e2215ebf05f6)

Source: `reasoning-core/staging` @8aa8748 (50 renamed tasks, deduped, L0-4, 48/level).
Influence: 80% fwdolci + 20% aux, answer-only, S43 T300 M20. `global%` = mean 6-leg NLL reduction with **cloze** mmlu (bbh, mmlu_math_cloze, mmlu_logic_cloze, mbpp, fw, dolci). **Positive = helps.** Ranked by mean of the 3 models.

| # | task | mean3 | SmolLM2 | Pleias | OLMo-1B | bbh(OLMo) |
|--:|:--|--:|--:|--:|--:|--:|
| 1 | regex_reasoning | **+3.88** | +3.21 | +3.11 | +5.34 | +14.76 |
| 2 | arithmetics | **+3.68** | +3.47 | +2.94 | +4.62 | +5.50 |
| 3 | planar_geometry_relations | **+3.32** | +4.30 | +2.44 | +3.21 | +10.63 |
| 4 | math_word_problem | **+3.25** | +4.05 | +3.23 | +2.46 | +6.59 |
| 5 | equation_system | **+2.90** | +3.61 | +2.76 | +2.32 | +4.06 |
| 6 | constraint_satisfaction | **+2.82** | +3.99 | +2.49 | +1.98 | +4.97 |
| 7 | logic_qa | **+2.63** | +4.21 | +2.02 | +1.65 | -5.99 |
| 8 | defeasible_nli | **+2.50** | +3.60 | +2.64 | +1.27 | +2.56 |
| 9 | most_probable_outcome | **+2.32** | +2.88 | +1.78 | +2.31 | +8.44 |
| 10 | qualitative_causal_reasoning | **+2.31** | +3.48 | +1.68 | +1.76 | +4.59 |
| 11 | code_analysis | **+2.27** | +2.77 | +2.16 | +1.88 | +4.29 |
| 12 | qualitative_reasoning | **+2.26** | +3.71 | +2.26 | +0.81 | +1.48 |
| 13 | multistep_abduction | **+2.25** | +3.22 | +1.98 | +1.55 | +2.46 |
| 14 | game_forced_win | **+2.17** | +3.28 | +1.05 | +2.17 | +6.23 |
| 15 | belief_tracking | **+2.12** | +2.91 | +2.84 | +0.62 | -0.11 |
| 16 | grid_navigation | **+2.11** | +3.03 | +2.41 | +0.88 | +1.68 |
| 17 | coreference | **+2.05** | +2.97 | +1.88 | +1.31 | +0.45 |
| 18 | string_transduction | **+2.00** | +2.46 | +2.56 | +0.99 | -0.04 |
| 19 | metamath_core_select | **+1.94** | +2.49 | +1.67 | +1.67 | +10.49 |
| 20 | multistep_nli | **+1.90** | +3.15 | +2.21 | +0.34 | -3.59 |
| 21 | graph_successors | **+1.87** | +2.81 | +1.92 | +0.87 | +1.72 |
| 22 | logic_formalization | **+1.82** | +1.80 | +1.58 | +2.08 | +12.61 |
| 23 | lean_candidate_compilation | **+1.77** | +2.60 | +1.93 | +0.78 | +5.75 |
| 24 | unification_entailment | **+1.76** | +3.40 | +1.55 | +0.33 | +2.15 |
| 25 | reference_tracking | **+1.76** | +2.58 | +1.92 | +0.77 | +1.85 |
| 26 | sequential_induction | **+1.72** | +2.93 | +1.67 | +0.56 | -0.85 |
| 27 | analogical_case_matching | **+1.67** | +2.76 | +1.01 | +1.24 | +9.76 |
| 28 | game_best_move | **+1.43** | +2.93 | +1.52 | -0.15 | -1.27 |
| 29 | regex_following | **+1.42** | +1.79 | +2.22 | +0.25 | +1.59 |
| 30 | rewrite_system | **+1.42** | +2.58 | +1.58 | +0.10 | -3.31 |
| 31 | set_expression | **+1.42** | +1.00 | +1.38 | +1.88 | +6.08 |
| 32 | multistep_evidence_retrieval | **+1.40** | +2.56 | +2.18 | -0.54 | -6.37 |
| 33 | logic_nli | **+1.36** | +2.60 | +2.14 | -0.65 | +2.69 |
| 34 | graph_dependencies | **+1.34** | +3.32 | +1.59 | -0.89 | -3.16 |
| 35 | metamath_entailment | **+1.25** | +2.23 | +1.46 | +0.07 | +2.38 |
| 36 | most_probable_evidence | **+1.23** | +2.94 | +0.25 | +0.50 | +0.92 |
| 37 | table_statistics | **+1.15** | +0.60 | +1.00 | +1.86 | +2.16 |
| 38 | syntax_error_detection | **+1.12** | +1.61 | +1.78 | -0.01 | +4.63 |
| 39 | constrained_continuation | **+1.11** | +2.52 | +1.67 | -0.87 | -2.28 |
| 40 | code_execution | **+1.09** | +2.21 | +1.47 | -0.39 | -1.69 |
| 41 | lambda_reduction | **+1.08** | +2.19 | +1.26 | -0.23 | -2.71 |
| 42 | code_runnability | **+0.92** | +1.65 | +0.71 | +0.40 | +2.00 |
| 43 | graph_pathfinding | **+0.81** | +1.81 | +1.15 | -0.55 | +3.22 |
| 44 | table_equivalence | **+0.74** | +0.41 | +0.71 | +1.09 | +4.41 |
| 45 | parsing_derivation | **+0.72** | +2.38 | +0.78 | -1.02 | -2.13 |
| 46 | lean_missing_line | **+0.57** | +2.04 | +0.82 | -1.16 | -3.61 |
| 47 | set_missing_element | **+0.44** | +1.33 | +0.33 | -0.34 | +3.56 |
| 48 | program_synthesis | **+0.44** | +0.85 | +0.55 | -0.09 | +0.11 |
| 49 | planning | **+0.43** | +1.12 | -0.04 | +0.21 | +2.60 |
| 50 | table_qa | **+0.00** | +1.09 | +0.97 | -2.06 | -2.34 |

## Cross-model agreement (Spearman on cloze-global%)
- SmolLM2-135M vs Pleias-350m: **ρ=+0.657** (p=0.000, n=50)
- SmolLM2-135M vs OLMo-1B: **ρ=+0.480** (p=0.000, n=50)
- Pleias-350m vs OLMo-1B: **ρ=+0.486** (p=0.000, n=50)

## Hurters (global% < 0) by model
- **SmolLM2-135M**: none
- **Pleias-350m**: planning -0.04
- **OLMo-1B**: table_qa -2.06, lean_missing_line -1.16, parsing_derivation -1.02, graph_dependencies -0.89, constrained_continuation -0.87, logic_nli -0.65, graph_pathfinding -0.55, multistep_evidence_retrieval -0.54, code_execution -0.39, set_missing_element -0.34, lambda_reduction -0.23, game_best_move -0.15, program_synthesis -0.09, syntax_error_detection -0.01

## Robust helpers (top-10 on ALL three models)
- arithmetics, planar_geometry_relations, math_word_problem, equation_system, constraint_satisfaction
