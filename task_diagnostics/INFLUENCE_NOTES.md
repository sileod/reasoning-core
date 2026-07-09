# NOTES — what this measures and why (author hand-off)

These are the things that are easy to get subtly wrong. Read before changing the kernel.

## The measurement (per task X)
Marginal value of mixing task X into fine-tuning: train SmolLM2-135M on **80% dolci + 20% X** for 300
steps, vs the same run without X, and report the change in held-out NLL on each eval set. Lower delta =
X reduced that loss = X helped. This is a *differential* (mixture vs baseline), not X-in-isolation —
isolation systematically mis-ranks because real merges are mixtures (see below).

## The score: equal-z(dolci, fw, bbh), FLAN reference-only
- **dolci** = the fine-tuning target (instruction following). A task that raises dolci loss is taxing the
  thing we actually want — this is the main-loss guardrail, do not drop it.
- **fw** = FineWeb-edu LM loss = general-capability / do-no-harm guardrail (catches tasks that corrupt the
  base distribution). Magnitudes are tiny (±0.003) but the sign matters.
- **bbh** = reasoning benchmark = the upside signal.
- Each is **z-scored across the current task pool**, then averaged equal-weight. z-scoring is essential:
  raw bbh deltas (~0.3) dwarf dolci/fw (~0.003), so an unweighted sum would just be bbh.
- **FLAN is dropped from the score on purpose** (the dataset isn't trusted), but still measured and shown
  as a reference column. (Earlier this was the lead signal; it was demoted.)
- Lower score = better helper. The score is *relative to the pool* — adding/removing tasks shifts everyone's
  z slightly; that's expected, the ranking is the point, not the absolute number.

## Answer-only loss is mandatory (`COMPLETION_ONLY=1`)
Never train on the prompt. The **answer is the entire training signal**, so a task's value is a property of
its *answer*, and these consequences are load-bearing:
- **fw tax ⇐ unnatural answer chars** (pipes/brackets, no spaces), not difficulty. Worked, space-separated
  natural answers are fw-safe; `a|b|c` option-dumps are the worst case.
- **transfer rides on answer CONTENT, not domain or difficulty.** Same data, different answer format spans
  the whole ranking: the 3 table tasks ranged from #6 (`table_equivalence`, answer `yes/no`) to #34
  (`table_qa`, multi-row dump); a short eval-aligned pointer beat a worked-but-templated sentence by +0.13
  bbh on the analogical task. Rule when a task underperforms: **fix the answer format first** (short,
  eval-aligned, carrying the genuine reasoning step), before touching difficulty.
- **difficulty/learnability does NOT predict transfer.** Tuning a task from unlearnable→saturated left
  transfer flat. Do not chase "harder"; chase answer content.

## Gotchas
- **Env**: the kernel needs `trl`+`torch`+CUDA. If `flash_attn` throws a GLIBC error in one interpreter,
  use another (`MEASURE_PY=...`). This bit us repeatedly.
- **Generate from the local editable generators**, never a stale HF snapshot — that's the whole reason the
  cache is keyed on `behavior_hash()` (the generator's content hash). HF lags the code.
- **Seeds**: single-seed deltas have ~0.01 bbh noise. The table uses 2 seeds; treat sub-0.01 bbh gaps as ties.
- **DevTasks excluded**: `list_tasks()` already omits them; the table is non-Dev by construction.
- The measurement is a **135M proxy**. It ranks well at small scale; cross-model rank is somewhat
  idiosyncratic, and a few genuinely-hard tasks (lambda_reduction, analogical_case_retrieval) stay
  unlearnable through 360M even inside the full merge — i.e. the proxy fairly calls them weak at this scale.

## What I'd want next (not in scope here)
Vendor `per_task_influence.py` into the package and import it instead of shelling out; add a `--model` knob
to regenerate the table on a larger base when target scale is decided.
