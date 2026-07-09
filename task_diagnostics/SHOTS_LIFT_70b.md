# In-context learnability (ICL lift) — llama-3.3-70b-instruct

Reward = free-gen `score_answer` on the frozen model. **lift@K = reward@K − reward@0** — how much the model picks the task up from K worked examples (in-context learnability). Sorted by lift@3 (most ICL-learnable first).

| task | 0-shot | 1-shot | 3-shot | lift@1 | lift@3 | infl% |
|---|---|---|---|---|---|---|
| code_runnability | 0.40 | 1.00 | 1.00 | +0.60 | +0.60 | +3.7 |
| sequential_induction | 0.10 | 0.30 | 0.67 | +0.20 | +0.57 | +5.8 |
| qualitative_causal | 0.30 | 0.60 | 0.80 | +0.30 | +0.50 | +11.8 |
| multistep_abduction | 0.50 | 0.70 | 1.00 | +0.20 | +0.50 | +8.4 |
| most_probable_evidence | 0.50 | 0.90 | 0.90 | +0.40 | +0.40 | +9.7 |
| metamath_core_select | 0.60 | 0.80 | 1.00 | +0.20 | +0.40 | +17.0 |
| constraint_satisfaction | 0.40 | 0.80 | 0.80 | +0.40 | +0.40 | +10.8 |
| graph_pathfinding | 0.70 | 0.75 | 0.96 | +0.05 | +0.26 | +5.2 |
| equation_system | 0.58 | 0.70 | 0.81 | +0.12 | +0.22 | +7.5 |
| arithmetics | 0.10 | 0.66 | 0.32 | +0.56 | +0.22 | +5.5 |
| reference_tracking | 0.70 | 0.80 | 0.90 | +0.10 | +0.20 | +7.0 |
| graph_dependencies | 0.20 | 0.20 | 0.40 | +0.00 | +0.20 | +7.5 |
| rewrite_system | 0.10 | 0.10 | 0.30 | +0.00 | +0.20 | +6.9 |
| game_forced_win | 0.50 | 0.70 | 0.70 | +0.20 | +0.20 | +10.3 |
| defeasible_nli | 0.50 | 0.50 | 0.70 | +0.00 | +0.20 | — |
| set_expression | 0.65 | 0.34 | 0.80 | -0.31 | +0.15 | +3.3 |
| regex_reasoning | 0.70 | 0.81 | 0.80 | +0.11 | +0.10 | +7.8 |
| logic_nli | 0.70 | 0.70 | 0.80 | +0.00 | +0.10 | +10.1 |
| table_statistics | 0.90 | 1.00 | 1.00 | +0.10 | +0.10 | +5.3 |
| table_equivalence | 0.80 | 1.00 | 0.90 | +0.20 | +0.10 | +3.9 |
| most_probable_outcome | 0.80 | 0.80 | 0.90 | +0.00 | +0.10 | +12.8 |
| graph_successors | 0.80 | 0.80 | 0.90 | +0.00 | +0.10 | +6.5 |
| coreference | 0.80 | 0.90 | 0.90 | +0.10 | +0.10 | +10.5 |
| regex_following | 0.87 | 0.72 | 0.93 | -0.14 | +0.07 | +4.1 |
| set_missing_element | 0.77 | 0.49 | 0.80 | -0.28 | +0.03 | +4.6 |
| table_qa | 0.80 | 0.91 | 0.80 | +0.11 | +0.00 | +5.3 |
| qualitative_reasoning | 0.40 | 0.20 | 0.40 | -0.20 | +0.00 | +12.5 |
| program_synthesis | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +0.6 |
| planning | 0.91 | 0.82 | 0.91 | -0.09 | +0.00 | +2.9 |
| metamath_entailment | 0.90 | 0.60 | 0.90 | -0.30 | +0.00 | +5.2 |
| lambda_reduction | 0.00 | 0.00 | 0.00 | +0.00 | +0.00 | +4.9 |
| constrained_continuation | 0.11 | 0.30 | 0.01 | +0.19 | -0.09 | +5.9 |
| parsing_derivation | 0.30 | 0.40 | 0.20 | +0.10 | -0.10 | +8.0 |
| code_execution | 1.00 | 1.00 | 0.90 | +0.00 | -0.10 | +4.4 |
| string_transduction | 0.10 | 0.00 | 0.00 | -0.10 | -0.10 | +5.6 |
| multistep_nli | 0.80 | 0.40 | 0.70 | -0.40 | -0.10 | +9.7 |
| logic_qa | 0.80 | 0.70 | 0.70 | -0.10 | -0.10 | +7.3 |
| belief_tracking | 0.80 | 0.60 | 0.70 | -0.20 | -0.10 | — |
| math_word_problem | 0.81 | 0.81 | 0.66 | +0.00 | -0.15 | +7.0 |
| mgu_implied_equality | 0.90 | 1.00 | 0.75 | +0.10 | -0.15 | — |
| multistep_evidence_retrieval | 0.40 | 0.10 | 0.20 | -0.30 | -0.20 | +5.9 |
| game_best_move | 0.90 | 0.80 | 0.70 | -0.10 | -0.20 | +9.3 |
| code_analysis | 0.80 | 0.50 | 0.60 | -0.30 | -0.20 | — |

- **Spearman(zero-shot reward, lift@3) = -0.41** (p=0.006, n=43) — negative ⇒ ICL helps most where zero-shot is weakest (headroom effect).
- **Spearman(train-time influence global%, lift@3) = +0.18** (p=0.274, n=39) — positive ⇒ tasks that are learnable *in context* are also the ones useful when *trained on* (two learnability probes agree).
