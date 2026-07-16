# Shared pipeline dev audit

Production `run_sft.py` and influence scripts remain unchanged. The dev runner
must prove each item below before any migration.

## Preserved and tested

- Formatting is versioned: `sft_qa_v1` preserves `Q: {prompt}\nA:` plus a
  leading answer space; `influence_legacy_v1` preserves `{prompt}\n` with no
  leading answer space. Formatter IDs are stored in arm specs and events.
- Prodigy and loss-aware AdamC both train and evaluate through `SFTTrainer`.
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
- Exact parity for batch auto-sizing, packing/source-aware collation, token
  budgets, filtering, and stage-2 stream offsets.
- Exact parity for main/task-level/intrinsic/downstream evaluation cadence and
  W&B mirroring.
- Versioned evaluator registry covering every existing MMLU/BBH/Platinum leg.
- Durable initialization artifact and hash for paired influence arms.
- Baseline compatibility key covering model initialization, data revisions,
  optimizer settings, batching, packing, masking, length, seed, and budget.
