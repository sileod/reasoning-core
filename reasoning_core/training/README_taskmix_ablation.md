# RC Taskmix Ablation

Estimates which RC task groups help FineWeb LM loss more or less, while keeping the RC auxiliary budget fixed. Dropped RC examples are replaced by later RC examples, so the estimand is:

```text
task group vs the rest of RC, conditional on fixed aux_ratio
```

Use separate `aux_ratio` sweeps to estimate total RC usefulness.

## Run

```bash
PYTHONPATH=$PWD python reasoning_core/training/run_sft.py \
  --main_data fw \
  --aux_data rc \
  --aux_ratio 0.4 \
  --token_budget 200M \
  --iterable_mode True \
  --ablation_group_map configs/task_groups_v1.json \
  --ablation_unit task \
  --ablation_control_frac 0.2 \
  --ablation_log_path run_logs/mix_ablation.jsonl \
  --n_eval 20
```

Task-level ablation is the default, with rates `0,0.25,0.5,1`. Window length is chosen from the expected step budget to target repeated schedule coverage, bounded by `--ablation_min_window_steps` and `--ablation_max_window_steps`. Use `--ablation_unit group` for faster group-level smoke tests.

## Analyze

```bash
PYTHONPATH=$PWD python reasoning_core/training/analyze_mix_ablation.py \
  run_logs/mix_ablation.jsonl
```

Output:

```text
unit | best_drop_rate | recommended_keep_ratio | stderr
```

Interpretation:

- Higher `best_drop_rate`: dropping this unit improved FineWeb loss, so keep less of it.
- Lower `best_drop_rate`: dropping this unit did not help, or hurt, so keep more of it.
- `recommended_keep_ratio = 1 - best_drop_rate`.

The analyzer regresses local loss deltas on previous loss, a quadratic step trend, and current/lagged ablation terms. On the 50M smoke run this beat naive/AutoETS one-step loss-curve baselines; avoid higher-degree step polynomials unless a longer run justifies them.

Online W&B ratio logging is enabled by default after enough rows:

```text
mix_ablation/recommended_keep_ratio/{unit}
mix_ablation/best_drop_rate/{unit}
mix_ablation/stderr/{unit}
mix_ablation/effect/{unit}
```
