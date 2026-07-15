# Zero-shot task solvability

Real free-gen reward (`task.score_answer`) via litlm — hardest first. Low reward on a capable model = genuinely hard/unlearnable (teacher-forced token_acc inflates). `gen` = mean generator s/example. Per-example labels: zero_shot_preds.jsonl (local).

| task | Mistral-Small-3.2-24B-Instruct-2506 ↑ | gen |
|---|---|---|
| rewrite_system | 0.12 | — |
| arithmetics | 0.13 | — |
| analogical_case_matching | 0.28 | — |
| logic_nli | 0.40 | — |
| belief_tracking | 0.44 | — |
| code_analysis | 0.48 | — |
| game_forced_win | 0.48 | — |
| logic_qa | 0.56 | — |
| unification_entailment | 0.56 | — |
| parsing_derivation | 0.59 | — |
| code_execution | 0.72 | — |
| coreference | 1.00 | — |
