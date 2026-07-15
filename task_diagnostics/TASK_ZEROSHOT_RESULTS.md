# Zero-shot task solvability

Real free-gen reward (`task.score_answer`) via litlm — hardest first. Low reward on a capable model = genuinely hard/unlearnable (teacher-forced token_acc inflates). `gen` = mean generator s/example. Per-example labels: zero_shot_preds.jsonl (local).

| task | llama-3.3-70b-instruct ↑ | gen |
|---|---|---|
| analogical_case_matching | 0.00 | — |
| lambda_reduction | 0.00 | — |
| constrained_continuation | 0.01 | — |
| equation_system | 0.10 | — |
| game_forced_win | 0.20 | — |
| arithmetics | 0.21 | — |
| graph_dependencies | 0.30 | — |
| defeasible_nli | 0.40 | — |
| logic_formalization | 0.40 | — |
| constraint_satisfaction | 0.50 | — |
| belief_tracking | 0.60 | — |
| code_runnability | 0.60 | — |
| game_best_move | 0.60 | — |
| grid_navigation | 0.60 | — |
| code_execution | 0.70 | — |
| graph_successors | 0.70 | — |
| code_analysis | 0.76 | — |
| lean_missing_line | 0.80 | — |
| logic_nli | 0.80 | — |
| lean_candidate_compilation | 0.90 | — |
| graph_pathfinding | 0.92 | — |
