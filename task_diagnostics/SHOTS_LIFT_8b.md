# In-context learnability (ICL lift) — llama-3.1-8b-instruct

Reward = free-gen `score_answer` on the frozen model. **lift@K = reward@K − reward@0** — how much the model picks the task up from K worked examples (in-context learnability). Sorted by lift@3 (most ICL-learnable first).

| task | 0-shot | 1-shot | 3-shot | lift@1 | lift@3 | infl% |
|---|---|---|---|---|---|---|
| table_statistics | 0.11 | 0.28 | 0.83 | +0.17 | +0.72 | +5.3 |
| most_probable_evidence | 0.17 | 0.56 | 0.61 | +0.39 | +0.44 | +9.7 |
| graph_pathfinding | 0.18 | 0.52 | 0.54 | +0.34 | +0.37 | +5.2 |
| planning | 0.30 | 0.58 | 0.64 | +0.28 | +0.34 | +2.9 |
| table_equivalence | 0.44 | 0.56 | 0.78 | +0.11 | +0.33 | +3.9 |
| multistep_evidence_retrieval | 0.06 | 0.00 | 0.39 | -0.06 | +0.33 | +5.9 |
| logic_qa | 0.11 | 0.22 | 0.44 | +0.11 | +0.33 | +7.3 |
| analogical_case_matching | 0.00 | 0.20 | 0.33 | +0.20 | +0.33 | — |
| mgu_implied_equality | 0.33 | 0.40 | 0.64 | +0.07 | +0.31 | — |
| metamath_entailment | 0.44 | 0.67 | 0.72 | +0.22 | +0.28 | +5.2 |
| game_best_move | 0.17 | 0.39 | 0.44 | +0.22 | +0.28 | +9.3 |
| coreference | 0.67 | 0.67 | 0.94 | +0.00 | +0.28 | +10.5 |
| qualitative_causal | 0.39 | 0.22 | 0.61 | -0.17 | +0.22 | +11.8 |
| multistep_nli | 0.45 | 0.42 | 0.67 | -0.03 | +0.21 | +9.7 |
| regex_reasoning | 0.28 | 0.53 | 0.47 | +0.25 | +0.19 | +7.8 |
| code_analysis | 0.18 | 0.19 | 0.38 | +0.01 | +0.19 | — |
| equation_system | 0.20 | 0.28 | 0.39 | +0.08 | +0.19 | +7.5 |
| sequential_induction | 0.12 | 0.28 | 0.29 | +0.15 | +0.17 | +5.8 |
| logic_nli | 0.22 | 0.44 | 0.39 | +0.22 | +0.17 | +10.1 |
| code_input_deduction | 0.00 | 0.07 | 0.13 | +0.07 | +0.13 | +3.0 |
| constrained_continuation | 0.01 | 0.00 | 0.12 | -0.01 | +0.11 | +5.9 |
| multistep_abduction | 0.00 | 0.06 | 0.11 | +0.06 | +0.11 | +8.4 |
| game_forced_win | 0.39 | 0.42 | 0.45 | +0.03 | +0.06 | +10.3 |
| defeasible_nli | 0.36 | 0.48 | 0.42 | +0.12 | +0.06 | — |
| metamath_core_select | 0.50 | 0.44 | 0.56 | -0.06 | +0.06 | +17.0 |
| graph_successors | 0.33 | 0.33 | 0.39 | +0.00 | +0.06 | +6.5 |
| code_execution | 0.57 | 0.29 | 0.63 | -0.29 | +0.06 | +4.4 |
| string_transduction | 0.00 | 0.00 | 0.06 | +0.00 | +0.06 | +5.6 |
| graph_dependencies | 0.11 | 0.00 | 0.17 | -0.11 | +0.06 | +7.5 |
| math_word_problem | 0.42 | 0.33 | 0.47 | -0.09 | +0.05 | +7.0 |
| count_elements | 0.97 | 1.00 | 1.00 | +0.03 | +0.03 | +7.5 |
| belief_tracking | 0.52 | 0.61 | 0.55 | +0.09 | +0.03 | — |
| set_expression | 0.48 | 0.37 | 0.50 | -0.10 | +0.03 | +3.3 |
| set_missing_element | 0.35 | 0.32 | 0.37 | -0.03 | +0.02 | +4.6 |
| regex_following | 0.53 | 0.68 | 0.55 | +0.15 | +0.01 | +4.1 |
| program_synthesis | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +0.6 |
| lambda_reduction | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +4.9 |
| table_qa | 0.51 | 0.41 | 0.48 | -0.10 | -0.03 | +5.3 |
| most_probable_outcome | 0.44 | 0.33 | 0.39 | -0.11 | -0.06 | +12.8 |
| rewrite_system | 0.06 | 0.17 | 0.00 | +0.11 | -0.06 | +6.9 |
| code_runnability | 0.28 | 0.17 | 0.22 | -0.11 | -0.06 | +3.7 |
| arithmetics | 0.33 | 0.15 | 0.24 | -0.17 | -0.08 | +5.5 |
| qualitative_reasoning | 0.11 | 0.06 | 0.00 | -0.06 | -0.11 | +12.5 |
| parsing_derivation | 0.11 | 0.00 | 0.00 | -0.11 | -0.11 | +8.0 |
| constraint_satisfaction | 0.61 | 0.61 | 0.44 | +0.00 | -0.17 | +10.8 |
| reference_tracking | 0.72 | 0.50 | 0.50 | -0.22 | -0.22 | +7.0 |

- **Spearman(zero-shot reward, lift@3) = -0.20** (p=0.194, n=46) — negative ⇒ ICL helps most where zero-shot is weakest (headroom effect).
- **Spearman(train-time influence global%, lift@3) = -0.02** (p=0.921, n=41) — positive ⇒ tasks that are learnable *in context* are also the ones useful when *trained on* (two learnability probes agree).
