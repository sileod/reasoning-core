# RC Taskmix Ablation

Estimates RC task usefulness while keeping the RC auxiliary budget fixed. Dropped RC examples are replaced by later RC examples, so each task is compared to the rest of RC at fixed `aux_ratio`.

## Run

```bash
PYTHONPATH=$PWD python reasoning_core/training/run_sft.py \
  --main_data fw \
  --aux_data rc \
  --aux_ratio 0.4 \
  --token_budget 200M \
  --iterable_mode True \
  --ablation_log_path run_logs/mix_ablation.jsonl \
  --n_eval 20
```

Task-level ablation and W&B ratio logging are enabled by default. Defaults use task odds multipliers `0,1,5`: remove the task, keep the natural RC mix, or make the task about 5x more likely relative to the rest of RC. Each treatment window tests up to `--ablation_tasks_per_window 4` task ratios, so a run gets more repeated measurements without making each intervention huge. Window length is chosen from the expected step budget, bounded by `--ablation_min_window_steps` and `--ablation_max_window_steps`.

## Analyze

```bash
PYTHONPATH=$PWD python reasoning_core/training/analyze_mix_ablation.py \
  run_logs/mix_ablation.jsonl
```

Output:

```text
task | ratio | effect | stderr | z | p | n
```

Rows are sorted by statistical strength. Negative `effect` means the intervention improved FineWeb loss versus the fitted loss curve; positive means it hurt. `ratio=0` suppresses the task, `ratio=5` upweights it.

The analyzer subtracts a fitted `c + a*t^-b` loss curve, then regresses residual deltas on current and lagged task-ratio interventions. A 50M smoke run favored this power baseline over naive, AutoETS, MMF, and higher-degree polynomial baselines.
