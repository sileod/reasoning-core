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

Task-level ablation and W&B ratio logging are enabled by default. Defaults use rates `0,0.25,0.5,1`; window length is chosen from the expected step budget, bounded by `--ablation_min_window_steps` and `--ablation_max_window_steps`.

## Analyze

```bash
PYTHONPATH=$PWD python reasoning_core/training/analyze_mix_ablation.py \
  run_logs/mix_ablation.jsonl
```

Output:

```text
task | best_drop_rate | recommended_keep_ratio | stderr
```

Higher `best_drop_rate` means dropping that task helped FineWeb loss, so keep less of it. Lower `best_drop_rate` means dropping it did not help, or hurt, so keep more of it.

The analyzer regresses local loss deltas on previous loss, a quadratic step trend, and current/lagged ablation terms. A 50M smoke run favored this over naive/AutoETS one-step loss-curve baselines; avoid higher-degree step polynomials without a longer run.
