# Shared pipeline dev audit

Production `run_sft.py` and influence scripts remain unchanged. The dev runner
must prove each item below before any migration.

## Preserved and tested

- QA formatting is exactly `Q: {prompt}\nA:` plus `" " + answer + EOS`.
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
- Local metrics and experiment events are canonical; no W&B dependency exists.

## Still required before migration

- Continuous-run versus kill/resume equivalence for shuffled iterable datasets.
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
