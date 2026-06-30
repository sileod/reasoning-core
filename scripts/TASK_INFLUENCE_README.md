# Task Influence Workflow

Use `scripts/task_influence.py` as the repo-local, repeatable summary layer
for task influence. It does not train models. It reads existing
`per_task_influence.py` outputs and rewrites the public Markdown table plus a
machine-readable JSON sidecar.

## Inputs

- `per_task_results/influence_*.json`: per-task held-out loss deltas.
- `per_task_results/sat_*.json`: per-task answer-token accuracy curves.
- `reasoning_core/tasks/*.py`: local task definitions, used only for cached
  smoke metrics and task behavior hashes.

Default scoring profile is `--profile dolci`:

- `dolci_delta`: target-domain metric. Lower is better.
- `bbh_delta`: reasoning-transfer metric. Lower is better.
- `fw_delta`: language-model tax guardrail. Positive means the task hurt FW.
- `flan_delta`: optional diagnostic metric, not part of the default Dolci
  score.
- `acc_start` / `acc_end`: diagnostic saturation accuracy, not part of the
  score.

Switch score regimes without editing code:

- `--profile dolci`: `dolci=1, bbh=1, fw=1, flan=0`
- `--profile flan`: `flan=1, bbh=1, fw=1, dolci=0`

Use `--weight target=value` for one-off overrides.

## Run / Refresh Influence

```bash
python scripts/task_influence.py \
  --tasks task_a task_b \
  --run-influence \
  --run-tag MYTAG
```

This builds `task_influence_work/MYTAG_instruct.json` from the local generators,
launches `per_task_influence.py` in tmux, and writes raw results to the runner's
`per_task_results/` directory. If the expected influence file already contains
all requested tasks, it skips retraining and refreshes `scripts/TASK_INFLUENCE.md`
plus `scripts/TASK_INFLUENCE.json` from the cached result.

Use `--force-run` to rerun a completed raw influence file. Use `--foreground`
when you do not want tmux.

To refresh the public report from existing raw files only:

```bash
python scripts/task_influence.py \
  --results-dir ~/sandboxes/rc_grad/per_task_results \
  --include MYTAG \
  --tasks task_a task_b \
  --out scripts/TASK_INFLUENCE.md
```

Use `--csv-out path.csv` only when a CSV export is explicitly needed.

Default behavior caches local task checks in `.task_influence_cache.json`.
The cache key includes task behavior hash, config, sample count, and script
version, so edited tasks are recomputed automatically.

Useful options:

- `--refresh`: recompute all local task checks, even when hashes match.
- `--no-local`: skip task generation and only aggregate existing result JSONs.
- `--tasks task_a task_b`: restrict local checks and output rows.
- `--include TAG`: only read result files containing `TAG`; repeatable.
- `--exclude TAG`: skip result files containing `TAG`; repeatable.
- `--weight flan=3`: override ranking weights; repeatable.

## Build Aux Data From Generators

To build a `LOCAL_AUX` file directly from current generators:

```bash
python scripts/task_influence.py \
  --tasks task_a task_b \
  --build-aux task_influence_work/staging_aux.json \
  --aux-examples 256 \
  --no-local
```

The JSON is keyed as expected by `per_task_influence.py`:

```json
{
  "task_a": [["prompt text", "answer text"]]
}
```

It also writes `task_influence_work/staging_aux.json.manifest.json` with task
behavior hashes, source files, modified times, and row counts. `task_influence_work/`
is ignored by git.

## Selective Gallery

The same script can rebuild a compact gallery:

```bash
python scripts/task_influence.py \
  --results-dir ~/sandboxes/rc_grad/per_task_results \
  --no-local \
  --gallery-out GALLERY.md
```

Gallery sections include each task behavior hash. On later runs, if a task's
hash still matches the existing section, that section is reused directly and
the task is not regenerated. Use `--gallery-refresh` to force all gallery
examples to regenerate.

The raw runner writes:

- `influence_<TAG>_S43_T300_M20_dolci_pretrained.json`
- `sat_<TAG>_S43_T300_M20_dolci_pretrained.json`
