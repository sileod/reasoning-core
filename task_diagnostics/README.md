# task_diagnostics

Tooling to measure **which tasks are worth their slot** in the reasoning-core roster.
Two complementary signals, each with its own script and result file:

| tool | question | needs GPU? | result files |
|---|---|---|---|
| `task_influence.py` | Does training on this task reduce held-out loss (BBH/dolci/FW)? | yes (trainer) | `TASK_INFLUENCE_RESULTS.{md,json}` |
| `zero_shot_eval.py` | Can a capable model actually solve it (real free-gen reward)? | no (API only) | `TASK_ZEROSHOT_RESULTS.{md,json}` |

Influence measures *transfer*; zero-shot measures *genuine solvability* — the honest
counterpart to teacher-forced token accuracy, which inflates on tasks a model can
"follow" but not "lead". Read them together: a task that transfers well but is
zero-shot-unsolvable is helping structurally, not by teaching a skill.

Only the `.md` files are tracked; the `.json` sidecars and `zero_shot_preds.jsonl`
are regenerable and git-ignored.

---

## TaskRow cache

For agentic audits and repeatable experiments, build immutable HF-compatible Parquet
rows first, then run analyses on those rows:

```bash
python -m task_diagnostics.cache build --tasks logic_nli arithmetics --levels 0 1 2 --n 16
python task_diagnostics/zero_shot_eval.py --cache task_diagnostics/cache/task_rows/<cache_id>
python task_diagnostics/task_influence.py --run-influence --taskrow-cache task_diagnostics/cache/task_rows/<cache_id>
```

Each row preserves prompt, answer, full metadata, level, config, behavior hash, token
counts, generation time, and `row_hash`. Local generated cache data is ignored by git.
See `MIGRATION.md` for the short transition notes.

---

## task_influence.py — transfer ranking

Builds aux data, trains SmolLM2-135M to measure each task's influence on held-out
loss, and rewrites a compact Markdown ranking plus a JSON sidecar. Only tasks whose
generator changed (behavior hash) are re-measured.

Refresh everything that changed (generate aux locally, measure stale tasks, rewrite table):

```bash
python task_diagnostics/task_influence.py --run-influence
```

Use a fixed TaskRow cache for aux training rows, saturation token accuracy, and
begin/end `score_answer` reward:

```bash
python task_diagnostics/task_influence.py --run-influence \
  --taskrow-cache task_diagnostics/cache/task_rows/<cache_id>
```

That's the whole workflow — defaults are baked in (SmolLM2-135M, dolci main data,
answer-only loss, 300 steps, 20% aux mix, seed 43, dedup on). The run tag is
auto-derived from the task/config hash; you never supply one.

Rebuild the table from already-measured results, no GPU:

```bash
python task_diagnostics/task_influence.py --no-local
```

### Aux data source: generate vs staging

By default aux data is generated locally from the task generators (serial, slow —
see `--gen-workers`). If you build task data on a cluster and push it to an HF repo,
pull that instead:

```bash
python task_diagnostics/task_influence.py --run-influence --source staging \
  --staging-repo reasoning-core/staging
```

`--source staging` streams the HF repo (rows keyed by `task`), takes the first
`--aux-examples` per task, and **deduplicates prompts** before measuring. Dedup is on
by default for both sources (`--no-dedup` to keep duplicates). Switching source or
dedup invalidates the aux cache, so the affected tasks re-pull/re-measure.

### Scoring

Default profile `--profile dolci` weights `dolci=1, bbh=1, fw=1, flan=0`:

- `dolci`: fine-tuning target. Lower is better (main-loss guardrail).
- `bbh`: reasoning-transfer upside. Lower is better.
- `fw`: FineWeb-edu LM tax. Positive = the task hurt FW (do-no-harm guardrail).
- `flan`: reference-only, not in the score.
- `acc` (`start→end`) and `tok` (`prompt/answer`) are diagnostics, not scored.

`--profile flan` flips to `flan=1, bbh=1, fw=1, dolci=0`. Use `--weight target=value`
for one-off overrides (e.g. `--weight fw=0.5`).

### Useful options

- `--tasks a b c`: restrict to specific tasks (default: all registered, DevTasks
  excluded). **Naming a DevTask here is enough to include it** in the table — no extra
  flag needed (e.g. `--tasks rocq_compute_nf`).
- `--include-dev NAME ...`: allow named DevTasks into a *full sweep* (when you don't
  pass `--tasks` and the DevTask arrives via its influence file rather than by name).
- `--gen-workers N`: parallel generator processes for `--build-aux` (real
  `ProcessPoolExecutor`). ~2x on pure-Python generators; **prover tasks
  (rocq/lean/tptp) can't run in the pool and auto-fall-back to serial**.
- `--dry-run`: render the table to stdout and write no files (report-only).
- `--force-run`: re-measure a task even if its result file is already complete.
- `--foreground`: run the trainer in this process instead of tmux.
- `--refresh`: recompute local smoke metrics even when behavior hashes match.
- `--results-dir DIR` / `--include TAG` / `--exclude TAG`: pick which raw result files
  to aggregate (`--include` matches by filename substring; repeat the flag for several).

### Caching

Local task checks cache in `.task_influence_cache.json`, keyed by behavior hash + config,
so edited tasks recompute automatically. Aux data caches under `task_influence_work/`
(git-ignored) with a manifest carrying per-task behavior hashes, source, and dedup flag.

The raw trainer (`per_task_influence.py`) writes:

- `per_task_results/influence_<TAG>_S43_T300_M20_dolci_pretrained.json`
- `per_task_results/sat_<TAG>_S43_T300_M20_dolci_pretrained.json`

See `INFLUENCE_NOTES.md` for methodology and gotchas (answer-only loss, answer-format
effects, the `flash_attn` GLIBC interpreter trap, 135M-proxy caveats).

---

## zero_shot_eval.py — real solvability

Measures real free-generation reward (`task.score_answer` on a capable model's output)
via **litlm** → free NVIDIA NIM endpoints (env `NVIDIA_NIM_API_KEY`) or OpenRouter
(`OPENROUTER_API_KEY`). Reproducible on any machine: in-repo generators + litlm, no
data_cache, no GPU, no training.

```bash
# default: 8B on all registered tasks, ~25 examples each
python task_diagnostics/zero_shot_eval.py

# a few tasks
python task_diagnostics/zero_shot_eval.py --tasks logic_nli count_elements analogical_case_retrieval

# scaling test: bigger model, throttled (free 70B tier is slow/rate-limited)
python task_diagnostics/zero_shot_eval.py --models nvidia_nim/meta/llama-3.3-70b-instruct --max-concurrency 2

# report the cached table without spending any API calls
python task_diagnostics/zero_shot_eval.py --dry-run

# evaluate a fixed TaskRow cache instead of generating fresh examples
python task_diagnostics/zero_shot_eval.py --cache task_diagnostics/cache/task_rows/<cache_id>
```

Examples are **non-deterministic by design** (no seeding — diverse generation is the
point). Predictions are hash-cached in `zero_shot_preds.jsonl` (keyed by the task's
behavior hash + system + max_tokens for fresh generation, or by `row_hash + model +
eval signature` for TaskRow caches) and **accumulate to `--n`**: each run tops up ok
examples and skips once the target is met, so free-tier rate-limit gaps self-heal.
A changed generator invalidates old fresh rows; changed cached rows get new row hashes.

Storage is kept **separate from the canonical task examples** — `zero_shot_preds.jsonl`
is the per-(task, model, example) source of truth; `TASK_ZEROSHOT_RESULTS.json` is the
derived aggregate (reward + gen-time per task/model).

Useful options: `--n`, `--models`, `--max-concurrency` (litlm semaphore — lower for
rate-limited tiers), `--gen-workers` (parallel gen, prover tasks auto-serial), `--dry-run`.

---

## Other diagnostics

Standalone probes for the *shortcut / pattern-magic* axis (do superficial cues alone
solve a task?). See `shortcut_gru_probe_notes.md`.

- `potato_lm.py` — cue-conditioned GRU answer LM (bag-of-cues → GRU → answer).
- `t5_shallow.py` — same bag-of-cues rendered as text → T5 encoder-decoder.
- `shortcut_miner.py` / `distractor_retrieval.py` — cue mining and distractor probes.
