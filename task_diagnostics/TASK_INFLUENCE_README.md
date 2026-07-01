# Task Influence Workflow

`scripts/task_influence.py` maintains the task-quality table: it builds aux data,
trains a small model to measure each task's influence on held-out loss, and rewrites
a compact Markdown ranking (`scripts/TASK_INFLUENCE.md`) plus a JSON sidecar
(`scripts/TASK_INFLUENCE.json`). Only tasks whose generator changed are re-measured.

Gallery rendering is a separate tool: `scripts/build_gallery.py`.

## Quick start

Refresh everything that changed (generate aux locally, measure stale tasks, rewrite table):

```bash
python scripts/task_influence.py --run-influence
```

That's the whole workflow — no other flags required. Sensible defaults are baked in
(SmolLM2-135M, dolci main data, answer-only loss, 300 steps, 20% aux mix, seed 43,
dedup on). A run tag is auto-derived from the task/config hash; you never supply one.

Rebuild the table from already-measured results, no GPU:

```bash
python scripts/task_influence.py --no-local
```

## Aux data source: generate vs staging

By default aux data is generated locally from the task generators, which is slow.
If you build task data on a cluster and push it to an HF repo, pull that instead:

```bash
python scripts/task_influence.py --run-influence --source staging \
  --staging-repo reasoning-core/staging
```

`--source staging` streams the HF repo (rows keyed by `task`), takes the first
`--aux-examples` per task, and **deduplicates prompts** before measuring. Dedup is on
by default for both sources (`--no-dedup` to keep duplicates). Switching source or
dedup invalidates the aux cache, so the affected tasks re-pull/re-measure.

## Scoring

Default profile `--profile dolci` weights `dolci=1, bbh=1, fw=1, flan=0`:

- `dolci`: fine-tuning target. Lower is better (main-loss guardrail).
- `bbh`: reasoning-transfer upside. Lower is better.
- `fw`: FineWeb-edu LM tax. Positive = the task hurt FW (do-no-harm guardrail).
- `flan`: reference-only, not in the score.
- `acc` (`start→end`) and `tok` (`prompt/answer`) are diagnostics, not scored.

`--profile flan` flips to `flan=1, bbh=1, fw=1, dolci=0`. Use `--weight target=value`
for one-off overrides (e.g. `--weight fw=0.5`).

## Useful options

- `--tasks a b c`: restrict to specific tasks (default: all registered, DevTasks excluded).
- `--force-run`: re-measure a task even if its result file is already complete.
- `--foreground`: run the trainer in this process instead of tmux.
- `--refresh`: recompute local smoke metrics even when behavior hashes match.
- `--results-dir DIR` / `--include TAG` / `--exclude TAG`: pick which raw result files to aggregate.

## Caching

Local task checks cache in `.task_influence_cache.json`, keyed by behavior hash + config,
so edited tasks recompute automatically. Aux data caches under `task_influence_work/`
(git-ignored) with a manifest carrying per-task behavior hashes, source, and dedup flag.

The raw trainer (`per_task_influence.py`) writes:

- `influence_<TAG>_S43_T300_M20_dolci_pretrained.json`
- `sat_<TAG>_S43_T300_M20_dolci_pretrained.json`

See `scripts/INFLUENCE_NOTES.md` for methodology and gotchas (answer-only loss,
answer-format effects, the `flash_attn` GLIBC interpreter trap, 135M-proxy caveats).
