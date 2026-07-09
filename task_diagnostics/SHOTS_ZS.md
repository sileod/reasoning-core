# Zero-shot task solvability

Real free-gen reward (`task.score_answer`) via litlm — hardest first. Low reward on a capable model = genuinely hard/unlearnable (teacher-forced token_acc inflates). `gen` = mean generator s/example. Per-example labels: zero_shot_preds.jsonl (local).

| task | llama-3.3-70b-instruct@3s ↑ | gen |
|---|---|---|
| lambda_reduction | 0.00 | 0.00s |
| program_synthesis | 0.00 | 0.34s |
| string_transduction | 0.00 | 0.00s |
| constrained_continuation | 0.01 | 0.63s |
| multistep_evidence_retrieval | 0.20 | 0.01s |
| parsing_derivation | 0.20 | 0.31s |
| rewrite_system | 0.30 | 0.00s |
| arithmetics | 0.32 | 0.00s |
| graph_dependencies | 0.40 | 0.00s |
| qualitative_reasoning | 0.40 | 0.10s |
| code_analysis | 0.60 | 0.00s |
| math_word_problem | 0.66 | 0.01s |
| sequential_induction | 0.67 | 0.05s |
| game_best_move | 0.70 | 0.08s |
| game_forced_win | 0.70 | 0.26s |
| logic_qa | 0.70 | 0.00s |
| multistep_nli | 0.70 | 0.00s |
| defeasible_nli | 0.70 | 0.00s |
| belief_tracking | 0.70 | 0.00s |
| mgu_implied_equality | 0.75 | 0.00s |
| constraint_satisfaction | 0.80 | 0.01s |
| logic_nli | 0.80 | 0.15s |
| qualitative_causal | 0.80 | 0.00s |
| regex_reasoning | 0.80 | 0.01s |
| set_expression | 0.80 | 0.00s |
| set_missing_element | 0.80 | 0.00s |
| table_qa | 0.80 | 0.03s |
| equation_system | 0.81 | 0.04s |
| code_execution | 0.90 | 1.16s |
| coreference | 0.90 | 0.00s |
| graph_successors | 0.90 | 0.00s |
| metamath_entailment | 0.90 | 0.01s |
| most_probable_evidence | 0.90 | 0.25s |
| most_probable_outcome | 0.90 | 0.19s |
| reference_tracking | 0.90 | 0.01s |
| table_equivalence | 0.90 | 0.01s |
| planning | 0.91 | 1.53s |
| regex_following | 0.93 | 0.00s |
| graph_pathfinding | 0.96 | 0.00s |
| code_runnability | 1.00 | 0.08s |
| metamath_core_select | 1.00 | 0.51s |
| multistep_abduction | 1.00 | 0.00s |
| table_statistics | 1.00 | 0.01s |
