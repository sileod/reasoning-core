# Agent Notes

- Start with `TASK_AUTHORING_GUIDE.md` before adding or changing tasks. It explains the expected `Task`/`DevTask` shape, canonical answers, scoring, validation, and dataset hygiene.
- Use `GALLERY.md` for concrete examples of prompt/answer style. Keep new tasks similarly short, unambiguous, and easy to score.
- Prefer `Task` only for stable core datasets. Use `DevTask` for experimental, diagnostic, or non-SFT-friendly tasks so they stay out of the main task list.
- `generate()` should return a `Problem`, not `None`. Let retries happen inside generation helpers or raise a clear `RuntimeError` after bounded attempts.
- Keep answers canonical and compact: booleans, numbers, sorted Python lists, or exact constrained strings. Avoid asking models to copy long bodies unless the task is explicitly about generation.
- Do not touch unrelated dirty files. Check `git status --short` first; this repo often has work in progress.
- `rg` may be unavailable in this environment. Fall back to `find`, `grep`, and `sed`.
- Avoid traversing `reasoning_core/openenv`, `.venv`, checkpoints, and other generated environments when searching.
- For Lean tasks, keep hidden oracle state out of prompts. If an answer depends on a graph or candidates, display the exact graph or candidates used to compute that answer.
