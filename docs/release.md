# Releasing a dataset version

A release goes through three stages. Each one has a single entry point, and each writes
somewhere the next stage reads from.

| Stage | Command | Writes |
|---|---|---|
| 1. Build staging | `reasoning_core/generation/g5k/submit.sh` on Grid'5000 | `reasoning-core/staging`, folder `data/<version>/` |
| 2. Build the pile | `scripts/run_rc_preprocess_upload_safe.sh --source_version <version>` | `reasoning-core/procedural-pile` |
| 3. Update the card | `scripts/dataset_card.py stats`, `render`, `push` | the pile's `README.md` |

Before publishing a new version, tag the current one on the Hub, pinned to its commit
SHA, so the older version stays loadable (`paper-2608.05148` is one such tag).

## 1. Build staging

Sync the code to the storage, then submit from the Lille frontend:

```bash
g5k.sh sync                                   # refuses a dirty tree
ssh lille.g5k
cd /srv/storage/magnet@storage1.lille.grid5000.fr/dsileo/libs/reasoning_core
VERSION=rc13 SMOKE=1 bash reasoning_core/generation/g5k/submit.sh   # 1 node, tiny, no upload
VERSION=rc13 bash reasoning_core/generation/g5k/submit.sh           # 16 besteffort nodes + collector
```

`submit.sh` checks that the package parses under the fleet's Python 3.10. It then
resolves the roster and freezes it as `runs/<version>/roster.txt`. The roster is
`list_tasks()` by default; pass `ROSTER=<file>` (one name per line) to choose the tasks
yourself. The array writes JSONL to `runs/<version>/generated_data/`. A collector job
uploads it every 30 minutes to `staging/data/<version>/`. When generation finishes, run
one last `COLLECT_ONLY=1` pass. Logs go to `runs/<version>/logs/`, never to the
checkout. Resubmitting the same version resumes the run: workers skip finished files.

Other settings are documented at the top of `submit.sh`: `ARRAY_SIZE`,
`ROWS_PER_TASK`, `LEVELS`, `THREADS` and `DATASET_NAME`.

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
