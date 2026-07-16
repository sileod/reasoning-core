# Shared pipeline dev audit

Production `run_sft.py` and influence scripts remain unchanged. The dev runner
must prove each item below before any migration.

## Preserved and tested

- Formatting is versioned: `sft_qa_v1` preserves `Q: {prompt}\nA:` plus a
  leading answer space; `influence_legacy_v1` preserves `{prompt}\n` with no
  leading answer space. Optional prompt prefixes preserve the `run_sft.py`
  `SPECIAL + "\n"` behavior. Formatter IDs and prefixes are stored in arm specs.
- Prodigy and loss-aware AdamC both train and evaluate through `SFTTrainer`.
  The influence dev planner separately defaults to its production
  `adamw_torch`, `1e-4` learning rate, `0.01` weight decay, and linear schedule.
- Mixing semantics are explicit: influence `--mix-aux` is the absolute auxiliary
  fraction (`0.2` means probabilities `[0.8, 0.2]`), while SFT
  `--aux-ratio` remains an auxiliary/main ratio (`0.2` means `1/6` auxiliary).
- Influence packing defaults on. Auxiliary streams use an exact token-length
  filter with the production-style `max_length - len_margin` budget; SFT streams
  retain their cheaper character guard.
- Influence records both historical raw `delta_nll = treatment - baseline` and
  report-facing `reduction_pct = 100 * (baseline - treatment) / baseline`.
- Schedule-free optimizers enter eval mode only around evaluation/checkpoint
  serialization, then restore their prior mode.
- Runtime writes are rooted under `~/.reasoning_core`.
- Checkpoint deadlines use monotonic wall time and fire at optimizer-step
  boundaries.
- SIGTERM/SIGUSR1 request a save at the next step and leave the arm incomplete.
- Only checkpoints with `.complete` are resumed; existing complete Trainer
  checkpoints can be adopted once.
- SFT arms may retain a final checkpoint; short influence arms do not force one.
- Completed arms reuse local `status.json` metrics without retraining.
- Local JSON/JSONL/Parquet and Hugging Face datasets share one streaming recipe;
  main and auxiliary sources are independently configurable.
- HF streaming SFT completed cleanly with Dolci main + FLAN auxiliary. Remote
  influence arms are process-isolated; a short post-GC grace period avoids an
  environment-specific native `datasets`/Arrow shutdown race.
- The production-like AdamW/linear/packing influence path completed paired
  one-step runs with synthetic local data and Dolci + FLAN HF streams on
  `sileod/microlm-ettin-swa-5m`.
- Seeded interleave+buffered-shuffle replay followed by deterministic skipping
  reproduces local-stream continuation exactly.
- On `sileod/microlm-ettin-swa-5m`, signal checkpoint/resume over the shuffled
  two-stream iterable matched uninterrupted AdamC parameters exactly and
  Prodigy within `5.96e-08` maximum absolute difference.
- Local metrics and experiment events are canonical; no W&B dependency exists.

## Still required before migration

- Automate the Trainer-level resume-equivalence smoke currently checked
  manually with the micro model.
- Multi-stage optimizer continuity matching `run_sft.py` stage 1 → stage 2.
- NFS lock/heartbeat behavior and stale-lock recovery.
- Exact parity for batch auto-sizing, source-aware collation, token budgets,
  all production data adapters, and stage-2 stream offsets.
- Numerical packing parity on a model with a supported packed attention
  implementation. The 5M smoke model warns that its attention implementation
  is not packing-aware, so its packed results prove execution only.
- Exact parity for main/task-level/intrinsic/downstream evaluation cadence and
  W&B mirroring.
- Versioned evaluator registry covering every existing MMLU/BBH/Platinum leg.
- A production-vs-dev real influence comparison using the same initialization,
  data, AdamW configuration, packing/filtering, and one shared NLL evaluator.
- Durable initialization artifact and hash for paired influence arms.
- Baseline compatibility key covering model initialization, data revisions,
  optimizer settings, batching, packing, masking, length, seed, and budget.
