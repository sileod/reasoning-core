# GRU Shortcut Probe

Purpose: find task pockets where shallow prompt-derived cues improve answer likelihood. Treat this as a shortcut-discovery tool, not a solver.

## Run

Small targeted run:

```bash
KERAS_BACKEND=torch python local_scripts/potato_lm.py \
  --tasks navigation,regex_reasoning,table_qa,set_missing_element \
  --modes instruct \
  --per-task 120 \
  --min-examples 60 \
  --epochs 8 \
  --seconds-per-task 40 \
  --hidden 64 \
  --vocab-size 512 \
  --shared-tokenizer \
  --project-vocab \
  --examples-out local_scripts/logs/gru_probe.examples.tsv \
  > local_scripts/logs/gru_probe.tsv
```

Broader pass:

```bash
KERAS_BACKEND=torch python local_scripts/potato_lm.py \
  --modes instruct \
  --per-task 240 \
  --min-examples 100 \
  --epochs 12 \
  --seconds-per-task 45 \
  --hidden 64 \
  --vocab-size 256 \
  --tokenizer bpe \
  --examples-out local_scripts/logs/gru_all.examples.tsv \
  > local_scripts/logs/gru_all.tsv
```

## Read The Output

Main columns:

- `base_nll`: answer-only baseline loss.
- `cue_nll`: loss with shallow prompt cues.
- `gain = base_nll - cue_nll`: higher means cues help predict answers.
- `gain_proj`: same idea with task-local vocabulary projection.
- `p90/p95`: within-task high shortcutability pockets.
- `exact`: rough generation sanity check; low exact does not invalidate likelihood gains.
- `rules`: simple cue enrichments among high-gain validation examples.

Use `examples.tsv` for manual inspection. Do not trust ranking alone.

## Interpretation

Good shortcut candidates have:

- positive mean gain or high `p90/p95`,
- human-readable rules,
- high-gain examples that share a generator mechanism,
- a clear generator-side balancing key.

Common false positives:

- answer format only: tuple/list/CSV/boolean;
- low-cardinality answer priors;
- tiny validation split imbalance;
- bad generations with only prefix learning.

## Workflow

1. Run GRU probe on instruct data.
2. Sort by `gain`, then by `p90/p95`.
3. Inspect high-gain examples manually.
4. Identify generator-state features causing shortcut pockets.
5. Add/adjust `balancing_key` and `balancing_key_ratio`.
6. Regenerate with `generate_balanced_batch`.
7. Rerun the probe and check that the specific pocket drops.

Prefer balancing keys over deletion. Keep keys coarse: answer length buckets, count buckets, query family, object touched/not touched, etc. Avoid exact-answer keys unless the answer space is intentionally tiny.
