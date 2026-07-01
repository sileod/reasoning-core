# Zero-shot task solvability

Real free-gen reward (`task.score_answer`) via litlm — hardest first. Low reward on a capable model = genuinely hard/unlearnable (teacher-forced token_acc inflates). `gen` = mean generator s/example. Per-example labels: zero_shot_preds.jsonl (local).

| task | llama-3.1-8b-instruct ↑ | gen |
|---|---|---|
| code_input_deduction | 0.00 | 1.03s |
| analogical_case_retrieval | 0.04 | 0.01s |
| table_statistics | 0.08 | 0.01s |
| parsing_derivation | 0.17 | 0.92s |
| planar_geometry_relations | 0.20 | 0.04s |
| logic_nli | 0.28 | 0.13s |
| planning | 0.29 | 0.13s |
| math_word_problem | 0.29 | 0.01s |
| multistep_nli | 0.36 | 0.00s |
| set_expression | 0.37 | 0.00s |
| game_forced_win | 0.40 | 0.30s |
| table_equivalence | 0.44 | 0.01s |
| graph_pathfinding | 0.44 | 0.00s |
| count_elements | 1.00 | 0.00s |
