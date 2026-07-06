# Task Diagnostics Migration

## What changed

Task diagnostics now have a canonical cached row format:

```text
task_diagnostics/cache/task_rows/<cache_id>/
  manifest.json
  data/part-00000.parquet
  analysis.md
```

Each row preserves `task`, `level`, `prompt`, `answer`, full JSON `metadata`,
`task_version`, `behavior_hash`, config, token counts, generation time, and a stable
`row_hash`. Analyses should consume these immutable rows instead of regenerating
examples implicitly.

Local manifests also record `generator_commit`, `sources` (task class source as an
audit-only string), and `source_hashes`. The hash decides cache freshness; the source
text and commit make changed-result audits easier.

## New commands

Build a small local cache:

```bash
# default: changed or missing tasks for this levels/n/mode request
python -m task_diagnostics.cache build --levels 0 1 2 --n 16

# explicit subset
python -m task_diagnostics.cache build --tasks logic_nli arithmetics --levels 0 1 2 --n 16
```

Run zero-shot on cached rows:

```bash
python task_diagnostics/zero_shot_eval.py --cache task_diagnostics/cache/task_rows/<cache_id>
```

Run GPU influence on the same cached rows:

```bash
python task_diagnostics/task_influence.py --run-influence --taskrow-cache task_diagnostics/cache/task_rows/<cache_id>
```

Read rows from a pinned HF dataset revision:

```bash
python -m task_diagnostics.cache from-hf --repo reasoning-core/reasoning-gym --revision <sha>
python -m task_diagnostics.cache from-hf --repo reasoning-core/basic-procedural --revision <sha>
```

## Expected differences

- Zero-shot predictions are keyed by `row_hash + model + eval signature`; stale rows
  from older task versions no longer enter current aggregates.
- Cached rows carry enough metadata for native `reasoning_core.score_answer`.
- GPU aux training, saturation token accuracy, and begin/end `score_answer` reward use
  the same cached TaskRows.
- Fresh generation is an explicit cache-build step, not an analysis side effect.
- `task_influence.py --run-influence` now requires `--taskrow-cache`.
- Local generated cache data is ignored by git; commit code and reports, not Parquet
  scratch caches.

## Old paths

The existing scripts and result paths still exist during the migration:

- `zero_shot_eval.py`
- `task_influence.py`
- `per_task_influence.py`
- `TASK_ZEROSHOT_RESULTS.{json,md}`
- `TASK_INFLUENCE_RESULTS.{json,md}`

Legacy pair-format aux building and staging-source influence runs were removed; rebuild
TaskRow caches instead.
