# Task Importance Runs

Controlled runs compare main-only, full RC mix, and isolated RC auxiliary tasks.
Each run uses `run_sft.py`'s normal `run_hash` checkpoint directory, so rerunning
the launcher resumes unfinished treatments. The launcher also keeps a lightweight
completion manifest in `checkpoints/task_importance/`, so already completed
commands are skipped without importing `run_sft.py`.

Plan a small grid:

```bash
python reasoning_core/training/task_importance.py plan \
  --experiment-name rc-task-impact-v1 \
  --reasoning-core-path "$PWD" \
  --main-data dolci fw \
  --seeds 1 2 \
  --tasks bayesian_intervention logic_nli \
  --extra --save_total_limit 1
```

Run the same grid sequentially:

```bash
python reasoning_core/training/task_importance.py run \
  --experiment-name rc-task-impact-v1 \
  --reasoning-core-path "$PWD" \
  --main-data dolci fw \
  --seeds 1 2 \
  --extra --save_total_limit 1
```

Defaults are intentionally small for controlled sweeps: `--token-budget 5M`
and `--aux-ratio 0.7`. Full RC mix is not included by default for task
importance sweeps; add `--include-full-mix` when you want that reference.
If `--tasks` is omitted, the launcher discovers task names from the selected
remote auxiliary dataset's test parquet metadata. Use `--aux-data rg` to run the
same isolated-task grid over Reasoning Gym source datasets.
Optional `--aux-mode` and `--aux-level` filters are passed through to
`run_sft.py`, for example:

```bash
python reasoning_core/training/task_importance.py plan \
  --experiment-name rc-task-impact-v1 \
  --reasoning-core-path "$PWD" \
  --tasks bayesian_intervention \
  --aux-mode cot \
  --aux-level 3
```

For OAR, use `plan` and submit each printed command, or wrap one command per
array index. The important part is to keep one shared `--experiment-name`; W&B
groups by it and local summaries filter by it. Prefer passing
`--reasoning-core-path /absolute/path/to/reasoning_core` so submitted commands
do not depend on the job's working directory.

Summarize completed local runs:

```bash
python reasoning_core/training/task_importance.py summary \
  --experiment-name rc-task-impact-v1
```

The summary joins `checkpoints/*/metrics.meta.json` with append-only
`metrics.jsonl`, then reports treatment deltas versus the `aux_ratio=0`
main-only baseline for each `main_data`, seed, and metric.
