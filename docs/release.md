# Releasing a dataset version

A release goes through three stages. Each one has a single entry point, and each writes
somewhere the next stage reads from.

| Stage | Command | Writes |
|---|---|---|
| 1. Build staging | `g5k.sh build <version>` (`python -m reasoning_core.generation submit`) | `reasoning-core/staging`, folder `data/<version>/` |
| 2. Build the pile | `scripts/run_rc_preprocess_upload_safe.sh --source_version <version>` | `reasoning-core/procedural-pile` |
| 3. Update the card | `scripts/dataset_card.py stats`, `render`, `push` | the pile's `README.md` |

Before publishing a new version, tag the current one on the Hub, pinned to its commit
SHA, so the older version stays loadable (`paper-2608.05148` is one such tag).

## 1. Build staging

`python -m reasoning_core.generation` builds a version into a run directory:

| Command | Does |
|---|---|
| `init --run-dir R --version V [--roster FILE]` | freezes `R/run.json`: tasks, levels, rows per task, target dataset, git revision |
| `generate --run-dir R [--workers N]` | runs this machine's workers until no batch is left |
| `collect --run-dir R [--loop]` | uploads finished batches to `staging/data/V/` |
| `submit --run-dir R --version V [--nodes 16] [--smoke]` | `init`, a Python 3.10 syntax check, then the `oarsub` calls |

Any number of machines can run `generate` on the same directory. Workers claim
batches with lock files, skip finished ones, retry a failed batch up to three times,
and are recycled every 15 minutes. A batch running over 20 minutes is killed. So a
preempted or resubmitted node resumes where it stopped. The roster is
`list_tasks()` unless `--roster` names a file (one task per line). Re-running
`init` or `submit` with different settings for an existing run is refused.

On Grid'5000, from this checkout:

```bash
g5k.sh build rc13 --smoke     # sync, then 1 node x 2 batches per task, no upload
g5k.sh build rc13             # sync, then 16 besteffort nodes + a looping collector
```

`build` syncs the code to the Lille storage and runs `submit` on the Lille frontend,
with the run directory at `$ST/runs/<version>`. Logs are in `$ST/runs/<version>/logs/`.
When generation ends, run the final collect command that `submit` printed. It is a
single pass and deletes what it uploads. Then add the version as a configuration in
`datasets/staging/README.md` (make it the default) and upload that file as the staging
repo's `README.md`.

The same commands work locally, for instance
`python -m reasoning_core.generation init --run-dir /tmp/r --version test` followed by
`generate --run-dir /tmp/r --workers 8`. `tests/generation/test_build.py` runs the
whole chain on a two-task roster.

## 2. Build the pile

```bash
scripts/run_rc_preprocess_upload_safe.sh --source_version rc13 --clear_existing_data
```

This reads only `staging/data/rc13/`, deduplicates the rows, splits off a test set,
and uploads parquet shards. `--clear_existing_data` replaces the previous version's
shards. Run it with `--smoke_test 10000 --dry_run` first. Few-shot and verification
rows are legacy formats and off by default.

## 3. Update the card

`datasets/procedural-pile/README.md` is the card's source of truth. Its prose is written
by hand. The schema, row and task counts, and per-area counts are regenerated:

```bash
python scripts/dataset_card.py stats      # scans the Hub -> stats.json
python scripts/dataset_card.py render     # fails if the task list and the data disagree
git commit datasets/procedural-pile && python scripts/dataset_card.py push
```
