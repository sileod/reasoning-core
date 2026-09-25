# Task Search

Developer tooling: use a checkout with an editable install. This subsystem is
included in the source distribution and excluded from the runtime wheel.

`reasoning_core.task_search` turns reviewed task ideas into isolated implementation
trials. Proposal generation remains a separate subsystem in `wave_proposer.py`.

## Package boundaries

- `plan.py` owns the frozen `Trial` and `SearchPlan` models, YAML loading, plan checks,
  and trial selection.
- `implementor_prompt.py` owns `PACE` and `render_implementor_prompt()`.
- `namespace.py` owns the filesystem a worker sees: the worktree is always
  `/home/workspace` and the trial's scratch space `/home/runtime`, whatever they are on
  this machine, so two runs of one trial differ by the work and not by the paths. It knows
  nothing about task search and is the piece to move if Harness Link ever grows a sandbox
  mode. `/home` is replaced wholesale because Bubblewrap cannot create a top-level mount
  point on a read-only root; `require_free_root()` fails loudly on a machine that keeps the
  interpreter or the operator's home there.
- `sandbox.py` owns Bubblewrap, resource limits, allowlisted environments, and bounded
  validation subprocesses. A worker's environment is built from `BASE_ENV_NAMES` rather
  than inherited: `HOME` and the XDG directories are named by `namespace.py`, the user
  and hostname are fixed, and the only credential present is the one named by
  `--credential-env` (default: the variable named by `TASK_SEARCH_KEY_ENV`). Candidate
  validation gets no credential at all.
- `validation.py` owns every coordinator and worker-facing gate and their failure
  precedence. `selfcheck.py` is only its CLI compatibility wrapper.
- `implementation_runner.py` creates worktrees, launches Harness Link, validates candidates, retries
  explicit infrastructure failures, and writes run records.
- `cli.py` contains argument parsing and command dispatch.
- `plans/` holds the `wave*.yaml` plans and the idea documents they came from;
  `proposals/` holds proposal waves and the archive a plan is generated from.

## Run a wave

Install a Harness Link version that provides the `hlink` frontend, then validate,
render, or run a plan:

```bash
python -m reasoning_core.task_search check reasoning_core/task_search/plans/wave8.yaml
python -m reasoning_core.task_search render reasoning_core/task_search/plans/wave8.yaml P001v1
python -m reasoning_core.task_search run reasoning_core/task_search/plans/wave8.yaml \
  --harness opencode --model deepseek-v4-flash --provider albert --trial P001v1
```

`--provider` is optional. Harness Link owns harness discovery, provider adaptation,
model selection, cwd, prompt delivery, unattended mode, and native argument forwarding.
Task search still owns experiment-specific permissions/configuration, step limits,
trajectory paths, AGY writable overlays, and the outer sandbox/resource limits.

`--fallback NAME` (or `TASK_SEARCH_FALLBACK`) names a second provider to answer what the
first one refuses. A 429 is one token bucket shared by every worker in the wave, so a
provider that saturates does not cost a trial, it costs the wave: the retry ladder waits
ten minutes per trial and then gives up. The fallback answers on *its own* default model,
so the trade is the run for knowing up front which model wrote the task -- the armed
fallback is recorded in the task's `settings.fallback_provider`, and which provider each
trial was actually served by is in its `run.json` under `launcher.fallback.routes`. Its
key must be named too, so `--credential-env` is given twice (or `TASK_SEARCH_KEY_ENV`
lists both, comma-separated); a fallback whose key is not named is refused before the
wave, because unnamed it would be absent from every worker's environment and Harness Link
would exit before the first step of every trial.

**Measure before arming it**, and read the measurement carefully. A fallback makes Harness
Link route every request through a local LiteLLM bridge, including the requests that never
fall back. Over 99 trials in four waves it rescued 3 (two of which then failed validation)
and killed 2 outright on `LiteLLM bridge did not become HTTP-ready`. That is the whole
case against it, and it is thin -- roughly break-even, which is why it ships off.

It is *not* the reason waves time out. That is the clock:

    07-15 UTC   28 timed out of 150 trials   (19%)
    15-07 UTC    4 timed out of 351 trials   ( 1%)

Trials are nineteen times likelier to burn their full wall clock during the working day,
armed or disarmed -- the first disarmed daytime wave timed out at 21% after six clean
nights. Blaming the bridge for this took three passes to stop doing; a provider under
load and a change you just made look identical from inside one wave.

Count those numbers with `trajectory.trial_directories`, never with a raw glob over
`run.json`: a retried trial leaves its dead attempt behind as `<trial>.attempt<N>-<reason>`
and counting those reports a wave as far bigger and far more broken than it was.

What is not in doubt is which failure it covers: Harness Link falls back on *errors*,
never on *latency*. Eleven trials burned their whole wall clock at thirty minutes each
while a healthy fallback sat idle, and the `primary` in every one of their
`launcher.fallback.routes` is how that was diagnosed. Arm it for a provider that refuses
outright; a provider that answers slowly is not the case it wins.

`run` requires a plan and `--model`. Defaults are OpenCode, one job, 56 steps,
and a 30-minute worker timeout. With no `--trial` or `--queue`, it runs every
trial in the plan; use `--trial ID` for a single-task smoke run.

OpenCode filesystem snapshots are disabled by default to avoid a second Git index
of each isolated worktree. Use `--snapshots` to enable session undo, or
`--no-snapshots` to disable it explicitly. This setting affects only OpenCode and
is recorded in `summary.json` and `run.json`; it does not change the worker prompt,
sandbox permissions, validation, or retained worktrees.

Each trial runs from the same detached base commit and may write only its owned task
directory and private runtime. The coordinator independently checks scope, provenance,
discovery, contract behavior, samples, reproducibility, validation commands,
gameability, semantics, and candidate stability in a fixed order.

Runs go to `$TASK_SEARCH_RUNS_ROOT/<wave>/<timestamp>/`, or to
`.reasoning_core-task-search/` beside the checkout when it is unset. Point it at local
disk when the checkout is on NFS: every trial checks out the whole repository, which takes
six and a half minutes over NFS and sixteen seconds locally. They retain prompts, harness output, validation logs, candidate hashes, `run.json`, and
an incrementally updated `summary.json`. See `BABYSITTING.md` for safe monitoring.
The runner prints the artifact directory at startup. Custom `--runs-root` paths
must be outside `/tmp` and `/run`, which are hidden by the sandbox.

## What a run pins

Every trial writes a `run.json` that names what it ran under, so a result can be argued
with rather than trusted: `base_commit` and `plan_sha256` (the plan as loaded, hashed at
load so an edit mid-wave cannot restamp earlier trials), `prompt_sha256` for the prompt
the worker actually got, `generation` for the model, provider, agent, requested seed and
whether it was forwarded, `launcher` for the Harness Link build, `harness_version` for
the harness build under it, `sandbox` for Bubblewrap, `resource_limits`, and
`scrubbed_credential_env_names` for what the worker was allowed to see.

That makes a wave **replayable**, not **deterministic**. Nothing here makes a provider
return the same tokens twice: the seed is forwarded where the harness supports it, and
the rest is the model's. What is reproducible is the setup -- the same commit, plan,
prompt and budget -- and what is reproducible *exactly* is the gate: a proposal wave
archives the candidates it turned down along with the catalog it judged them against, so
`propose --replay N` re-judges them verbatim and a change to the critic can be measured
rather than asserted.

## Before you launch

```bash
python -m reasoning_core.task_search doctor --live
```

It checks the two credential paths, which are separate and both fail open. Worker
credentials reach the coding agent through a copy of the environment, so the provider's
own key (`ALBERT_API_KEY` for albert) must be set in the shell that launches the run; a
wave without it spends its whole queue on `harness_failed`. The semantic reviewer reads
`TASK_SEARCH_REVIEW_ENDPOINT`, `TASK_SEARCH_REVIEW_MODEL` and
`TASK_SEARCH_REVIEW_KEY_ENV` instead; without them it returns a null verdict for every
trial and `land` skips them all as `unreviewed`. Both live in
`~/.config/reasoning_core/env`, which is outside the checkout and must be sourced --
background scripts do not inherit it. `--live` spends one tiny completion to prove the
key is not merely present but accepted, which is how a spent daily quota shows up before
a run rather than during one.

Those three variables say where the reviewer lives; `TASK_SEARCH_JUDGE_BACKEND` says what
kind of thing answers it. `llm` is the default: it asks a chat model for a `VERDICT:` and
a `WHY:`, which is what the gates have always done. `jev` asks TypeSafe's Jev through
OpenRouter's decisions endpoint and gets a typed choice with a distribution instead; it
reads `JEV_OPENROUTER_API_KEY`, a paid key, which is why it is never the default. A single
gate can be moved on its own with `TASK_SEARCH_<PURPOSE>_BACKEND` (`SANITY`, `FIDELITY`),
so a new judge can be measured against the gates that did not move rather than against a
memory of how the old one scored.

`run` defaults `--model` to `deepseek-v4-flash`, the implementor every landed wave
was built with. It has no default provider: which host serves that model is a fact
about a machine, so set `TASK_SEARCH_PROVIDER` in the env file and `run` and `doctor`
both pick it up.

## Propose tasks

```bash
python -m reasoning_core.task_search proposal-catalog
python -m reasoning_core.task_search propose sft-wave-1 --count 12
python -m reasoning_core.task_search check-proposals \
  reasoning_core/task_search/proposals/archive/sft-wave-1.yaml
```

### Replay what the gate turned down

A wave that dies mid-flight leaves `<archive>.yaml.partial`, and the next `propose` for that
name picks it up -- accepted proposals, ballots, and the candidates it generated but never
had critic budget to review. The archive itself stays write-once, because an archive on disk
is what tells the briefs driver a brief is finished.

`--replay N` seeds that same pool from history instead. A proposal is a name and a summary
and nothing else, so an archived rejection is a whole proposal: `--replay` re-judges up to N
of them under the current gate, and because the pool is always reviewed before a round
generates, they cost critic calls and no generation at all.

```bash
python -m reasoning_core.task_search propose replay-1 --count 12 --replay 60
```

This is the cheap half of a feedback loop, and deliberately the only half. Of 523 candidates
proposed so far, 300 died at the novelty gate, 0 at scheduling and 2 at implementation --
`funnel.py` prints that -- so the gate is already the only stage rejecting anything, and
tightening it further would buy nothing. Replay is one second chance per idea: a name turned
down twice is held back, counted from the archives so replaying needs no state of its own.
Anything that has since shipped under the same name is skipped too. Use `audit_novelty.py`
to measure how harsh the gate currently is -- it offers shipped tasks back as fresh
candidates and reports what the critic says about tasks already known to be worth having.

### How strictly the gate dedups

`--dedup lenient` (the default) and `--dedup strict` differ in one thing: whether a nearest
neighbour labelled `variant` can veto a `novel` verdict. Strict refuses the candidate on it;
lenient keeps the label as evidence the critic reports and refuses only on `same_operation`,
the claim that the task already exists. Nothing else moves -- not the score floors, and not
the verdict, which still has to be `novel`. `variant` as a *verdict* means what the critic
prompt says it means, a known operation with surface, parameter, direction or output-only
changes, so a gate that let it through would be admitting reskins by definition.

Leniency is a claim about the catalog, not about the critic. At four hundred tasks almost
every workable idea shares an operation with something already shipped -- 74% of one sweep's
811 rejections were `variant` -- and read strictly that breadth argues the catalog is
finished. What the setting reaches is the 8% the critic itself scored 4 or 5 and the labels
refused anyway; the other 96% were refused on the score floors, which no gate setting
touches. Raising the yield past that means changing what the critic is told counts as novel,
and that is a bigger experiment than it looks: the first attempt at one -- a prompt sentence
inviting the `variant` label -- took two briefs that had yielded 12 and 10 down to 1 and 0,
with the rejections scored `novelty: 2` almost to a candidate.

Each wave records the gate it was judged under in `review.dedup`, so waves proposed under
either setting stay comparable after the fact.

### Several models, several keys

`--model` and `--api-key-env` both take comma-separated lists: models in preference order,
keys shared round-robin.

```bash
python -m reasoning_core.task_search propose wave-12 \
  --model moonshotai/kimi-k3,deepseek-ai/deepseek-v4-pro-0813 \
  --api-key-env NVIDIA_API_KEY,NVIDIA_API_KEY_2
```

NVIDIA's quota is per account *and* per model, which is what the two dimensions are for: a
key that refuses kimi-k3 will still serve deepseek-v4-pro, and a second key serves both. A
pool steps sideways to another key before it steps down to another model, because a second
key on the model you asked for beats the first key on one you did not. A route that answers
429 is remembered as closed for half an hour, so a rotation does not keep handing work back
to an exhausted key and paying the retry ladder to learn what it was already told. Only 429
is routed around: hiding a 500 behind a fallback hides a broken endpoint.

See `proposals/FORMAT.md` for the proposal schema and novelty rules.

## Implement the backlog

What is owed is derived, not tracked: the archive says what was proposed, the package says
what exists, and the plans say what was already attempted. Nothing else is written down, so
nothing else can go stale.

```bash
python -m reasoning_core.task_search backlog                 # proposals with no task
python -m reasoning_core.task_search backlog --max-attempts 3  # ...still worth a try
```

`plan --skip-implemented` builds a plan over only what a wave still owes, so an archive can
be re-planned as tasks land instead of rebuilding what it already got. `--max-attempts N`
also drops the ideas N plan trials have already failed at.

`scripts/run_implementors.py` is that loop as a service: one wave at a time, `plan` then
`run` then `land --apply`, sleeping when nothing is owed and picking up archives as the
proposer writes them. It keeps no state, so it can be killed at any point. After each wave
it commits that wave's tasks, plan, outcomes and the manifest, and only those paths, so the
tracked tree stays clean for dataset builds; it never pushes. Then it deletes each trial's
checkout and runtime, keeping the logs, `run.json` and the task directory the worker wrote
(`candidate/`).

```bash
scripts/run_implementors.py --once --dry-run     # what it would do
scripts/run_implementors.py --max-attempts 3     # then leave it running
scripts/run_implementors.py --design-choices 2   # two named approaches + a baseline
```

`--design-choices` runs the design proposer first and gives each variant its own named
approach, as below. `--draws N` then asks each approach for N generators instead of one,
which is what separates a worse approach from an unlucky sample; it costs its multiple in
wall clock and, on a free provider, nothing else. Provider, fallback and credentials come from `TASK_SEARCH_PROVIDER`,
`TASK_SEARCH_FALLBACK` and `TASK_SEARCH_KEY_ENV`, so the service is not tied to one
provider and has no flags of its own for any of them.

Three numbers decide how much work one idea gets, and they are deliberately three:

| knob | question it answers |
|---|---|
| `--variants` / `--design-choices` | does this approach beat that one? |
| `--draws` | what does the same approach produce twice? |
| `--max-attempts` | how many more times is this idea worth trying? |

Attempts are counted in **rounds** -- one plan that ran the idea, whatever its fan-out.
They used to be counted in trials, which made the fan-out set the retry budget without
saying so: two design choices and a baseline spent three trials, so the service's
`--max-attempts 3` retired every idea after a single wave, and asking for draws on top
would have retired one partway through its first. Moving to rounds reopened 34 ideas that
had been tried exactly once.

A trial counts only once it has recorded an outcome in `plans/outcomes/<plan>.yaml`. A
plan is intent: killed between planning and running, it still claims its trials, and
counting those as spent retired every idea in the archive and left the service reporting
`0 proposals owed` for six days. An empty backlog now says which kind of empty it is. The count is what stops an unsupervised service from spending a
night on the same failures: the five proposals with no task today have been attempted four
to seven times each, so they are the ideas that resist implementation, not the ones nobody
got to.

## Running the loop as a service

Both loops run as systemd **user** services, enabled with boot recovery:

```bash
systemctl --user status  rc-task-search-proposer rc-task-search-implementor
systemctl --user restart rc-task-search-implementor
journalctl --user -u rc-task-search-proposer -f      # or runs/*-service.log
```

Three things about this machine that a unit has to say out loud, because each one fails
silently and looks like something else:

- **The user manager runs with `HOME=/home/dsileo`, and this account's real home is on
  NFS.** Units written to `$HOME/.config/systemd/user` are never found; they belong in
  `/home/dsileo/.config/systemd/user`. Each unit sets `Environment=HOME=` back to the NFS
  path, because Python resolves its *user* site-packages from `HOME`: without it `hlink` is
  not importable and every trial fails as `harness_failed` in under a minute, which reads
  exactly like a broken harness.
- **The credential is in the profile, not the env file.** `~/.config/reasoning_core/env`
  only *names* the variable (`TASK_SEARCH_KEY_ENV=ALBERT_API_KEY`); the value lives in
  `.profile`, so a unit sources that by absolute path before the env file. Without it the
  critic degrades to sharing the proposer's NVIDIA quota behind one WARNING line -- the 429
  that killed wave9 -- and the wave dies hours later.
- **Do not wrap the sourcing in `set -a`.** It exports shell *functions* too, and this
  profile defines about 230KB of them, which is enough to fail every later `exec` with
  `Argument list too long`. Both files already use `export`.

A worker also runs under a synthetic `HOME` inside bubblewrap, on purpose, so anything the
runner shells out to has to be importable without the operator's home. Install such tools
into the interpreter's own site-packages rather than `--user`.

## Compare implementation choices

Generate two distinct approaches per proposal, then run one worker per approach:

```bash
python -m reasoning_core.task_search plan proposals.yaml --name choice_pilot \
  --variants 3 --design-choices 2
python -m reasoning_core.task_search run reasoning_core/task_search/plans/choice_pilot.yaml \
  --model deepseek-v4-flash --provider albert
```

The design proposer defaults to DeepSeek V4 Flash on Albert and uses `ALBERT_API_KEY`.
`--variants` must be `--design-choices` plus one: the extra draw gets no named approach,
so every wave carries an unguided baseline to compare the guided ones against. Without
`--design-choices` at all, variants differ only by seed.
Every proposal in the input is included, so use a proposal subset for a small pilot.

The exact assigned approach is stored as `trials[].design_choice` in the plan, under
`Assigned design choice` in `prompt.md`, and as `design_choice` in each completed
trial's `run.json` and its `summary.json` result. This records the assignment, not
proof that the implementation followed it: inspect the candidate and samples before
comparing approaches. The generated module's `TASK_META` does not include this field;
retain the plan and run records alongside any selected candidate.

## Audit the gate

```bash
python -m reasoning_core.task_search.funnel          # add --json for the raw rows
```

Two tables, from the archives and the runs they produced, with no model calls. The first
is per-wave yield: accepted, rejected, pooled, and how many rejections were decided by a
short critic panel and how many of those were an exact split. The second is per-arm trial
outcomes and landings, counted only from plans that actually ran an unguided baseline
against guided arms -- the arm label alone means different things in different waves, so
grouping by it reports how long `v1` has existed rather than whether guidance helps.

Use it before concluding anything about a critic or prompt change. The redesigned critic
was credited with 22% against 1.4% by hand, and the same numbers by hand missed that a
third of all rejections that week ran on two samples instead of three.
