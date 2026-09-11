"""Command-line interface for task search."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from .implementor_prompt import DEFAULT_PACE, PACE, render_implementor_prompt
from .design_proposer import (
    DEFAULT_API_KEY_ENV as DESIGN_API_KEY_ENV,
    DEFAULT_ENDPOINT as DESIGN_ENDPOINT,
    DEFAULT_MODEL as DESIGN_MODEL,
)
from .legacy import LEGACY_SOURCE
from .chat import build_pool
from .wave_proposer import (
    CRITIC_API_KEY_ENV,
    CRITIC_ENDPOINT,
    CRITIC_MODEL,
    CRITIC_SAMPLES,
    DEFAULT_API_KEY_ENV,
    DEFAULT_ENDPOINT,
    DEFAULT_MODEL,
)
from .plan import _frozen_module_drift, _plan_problems, load_plan
from .implementation_runner import _repo_root, run_plan
from .sandbox import _write_json
from .doctor import default_provider

# The implementor that every landed wave was built with. A model name is a fact about
# what works and belongs in the repository; which provider serves it is a fact about a
# machine and does not, so the provider default is read from the environment and ships
# empty. Set TASK_SEARCH_PROVIDER in ~/.config/reasoning_core/env to have a local default.
IMPLEMENTOR_MODEL = "deepseek-v4-flash"



def _worker_credentials(named):
    """The credential variables the harness may see, falling back to the old convention.

    `scripts/run_task_search_weekend.sh` has always passed --credential-env the name held
    in TASK_SEARCH_KEY_ENV. Reading that variable directly keeps a plain `run` working now
    that the environment is an allowlist and an unnamed key would simply be absent.
    """
    if named:
        return list(named)
    fallback = os.environ.get("TASK_SEARCH_KEY_ENV", "").strip()
    return [fallback] if fallback else []


def _archive_path(repo_root, name):
    return (repo_root / "reasoning_core" / "task_search" / "proposals" / "archive"
            / f"{name}.yaml")


def _plan_path(repo_root, name):
    return repo_root / "reasoning_core" / "task_search" / "plans" / f"{name}.yaml"


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate and summarize a plan")
    check.add_argument("plan")
    render = subparsers.add_parser("render", help="render one worker prompt")
    render.add_argument("plan")
    render.add_argument("trial_id")
    render.add_argument("--pace", choices=sorted(PACE), default=DEFAULT_PACE)
    propose = subparsers.add_parser(
        "propose", help="generate an SFT-first proposal wave with novelty review"
    )
    propose.add_argument("name")
    propose.add_argument("--count", type=int, default=12)
    propose.add_argument("--output")
    propose.add_argument(
        "--model", default=DEFAULT_MODEL,
        help="comma-separated models in preference order; a later one is used only when"
             " every key is refusing the earlier ones")
    propose.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    propose.add_argument(
        "--api-key-env", default=DEFAULT_API_KEY_ENV,
        help="comma-separated names of credential variables to share round-robin, so one"
             " key's quota does not cap the wave")
    propose.add_argument("--seed", type=int, default=0)
    propose.add_argument("--temperature", type=float, default=1.0)
    propose.add_argument(
        "--reasoning-effort",
        choices=("low", "high", "max", "none"),
        default="max",
        help="none omits the field, for endpoints that reject unknown keys",
    )
    propose.add_argument(
        "--brief",
        help="what this wave is for, in a sentence or two: a domain, a family of "
             "structures, a shape of answer. Recorded in the wave's provenance so an "
             "archived wave says what it was asked for. Steering narrows the search and "
             "relaxes no novelty rule")
    propose.add_argument(
        "--brief-file", type=Path,
        help="read --brief from a file, for a steer worth keeping under version control")
    propose.add_argument("--rounds", type=int, default=3)
    propose.add_argument(
        "--timeout-seconds",
        type=int,
        default=2400,
        help="per-call budget; NIM queues kimi-k3 for minutes before it answers",
    )
    propose.add_argument(
        "--max-batch",
        type=int,
        default=12,
        help="proposals per model call; NIM's gateway returns 504 long before "
             "kimi-k3 finishes writing sixty of them",
    )
    propose.add_argument(
        "--pool-size", type=int, default=48,
        help="candidates to ask for per round before diversity selection")
    propose.add_argument(
        "--critic-model", default=CRITIC_MODEL,
        help="model for the novelty review, on its own provider so that the two calls in"
             " a round cannot starve each other; 'same' reuses the proposer's client")
    propose.add_argument("--critic-endpoint", default=CRITIC_ENDPOINT)
    propose.add_argument("--critic-api-key-env", default=CRITIC_API_KEY_ENV)
    propose.add_argument(
        "--critic-reasoning-effort", default="none", choices=("none", "low", "high", "max"))
    propose.add_argument(
        "--critic-samples", type=int, default=CRITIC_SAMPLES,
        help="review each candidate this many times over shuffled orderings and take the"
             " majority; 1 restores a single opinion")
    doctor = subparsers.add_parser(
        "doctor", help="check this machine can run a wave before a wave finds out"
    )
    doctor.add_argument("--provider", default=default_provider())
    doctor.add_argument("--harness", default="opencode",
                        choices=("opencode", "mini", "agy"))
    doctor.add_argument("--live", action="store_true",
                        help="spend one tiny completion proving the reviewer key works")
    doctor.add_argument("--timeout", type=float, default=60)
    proposal_check = subparsers.add_parser(
        "check-proposals", help="validate an archived SFT proposal wave"
    )
    proposal_check.add_argument("proposal_wave")
    legacy = subparsers.add_parser(
        "import-legacy",
        help="archive the hand-written candidate list as a reference proposal wave",
    )
    legacy.add_argument("--name", default="external")
    legacy.add_argument("--source", default=LEGACY_SOURCE)
    legacy.add_argument("--output")
    build = subparsers.add_parser(
        "plan", help="turn an archived proposal wave into an executable plan"
    )
    build.add_argument("proposal_wave")
    build.add_argument(
        "--name",
        required=True,
        help="name of the implementation wave, which is not the proposal wave it runs: "
             "one set of ideas can be implemented repeatedly. Convention: "
             "<proposal_wave>_r<n>, e.g. external_r2",
    )
    build.add_argument(
        "--variants",
        type=int,
        default=1,
        help="independent implementations to run per proposal (different seeds)",
    )
    build.add_argument("--base-ref", default="HEAD")
    build.add_argument("--output")
    build.add_argument("--context-file", action="append", default=[])
    build.add_argument(
        "--design-choices",
        type=int,
        default=0,
        help="ask the design proposer for this many approaches per task and split the"
             " variants across them, instead of splitting on seed alone; must equal"
             " --variants. 0 leaves the plan exactly as it has always been built",
    )
    build.add_argument(
        "--skip-implemented",
        action="store_true",
        help="leave out the proposals a task already implements, so a wave can be"
             " re-planned for what it still owes instead of rebuilding what it got",
    )
    build.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="with --skip-implemented, also leave out ideas already tried this many"
             " times across all plans; 0 keeps them however often they have failed",
    )
    build.add_argument("--design-model", default=DESIGN_MODEL)
    build.add_argument("--design-endpoint", default=DESIGN_ENDPOINT)
    build.add_argument("--design-api-key-env", default=DESIGN_API_KEY_ENV)
    owed = subparsers.add_parser(
        "backlog", help="proposals the package has no task for yet"
    )
    owed.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="hide ideas already tried this many times across all plans; 0 shows all",
    )
    catalog = subparsers.add_parser(
        "proposal-catalog", help="summarize the durable novelty catalog"
    )
    catalog.add_argument(
        "--output", help="optionally write the complete catalog as JSON"
    )
    run = subparsers.add_parser("run", help="launch folder-scoped coding workers")
    run.add_argument("plan")
    run.add_argument("--model", default=IMPLEMENTOR_MODEL,
                     help=f"implementor model (default: {IMPLEMENTOR_MODEL})")
    run.add_argument(
        "--harness", choices=("opencode", "mini", "agy"), default="opencode"
    )
    run.add_argument("--provider", default=default_provider(),
                     help="Harness Link provider; defaults to $TASK_SEARCH_PROVIDER")
    run.add_argument(
        "--snapshots",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="enable OpenCode session undo snapshots (default: disabled; OpenCode only)",
    )
    run.add_argument(
        "--credential-env",
        action="append",
        default=[],
        help="name of a provider credential the harness may see; candidate validation "
             "never sees it (default: the variable named by TASK_SEARCH_KEY_ENV)",
    )
    run.add_argument("--jobs", type=int, default=1)
    run.add_argument("--trial", action="append", default=[])
    run.add_argument("--queue", action="append", default=[])
    run.add_argument("--agent", default="task-search-worker")
    run.add_argument("--variant")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument(
        "--forward-seed",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="forward each derived trial seed to OpenCode (default: enabled)",
    )
    run.add_argument("--temperature", type=float)
    run.add_argument("--top-p", type=float)
    run.add_argument("--max-steps", type=int, default=56)
    run.add_argument(
        "--pace",
        choices=sorted(PACE),
        default=DEFAULT_PACE,
        help="how hard the worker is told to hurry; recorded in generation metadata so waves stay comparable",
    )
    run.add_argument("--timeout-seconds", type=int, default=1800)
    run.add_argument("--transient-retries", type=int, default=2)
    run.add_argument("--retry-backoff-seconds", type=int, default=30)
    run.add_argument("--validation-timeout-seconds", type=int, default=300)
    run.add_argument("--hlink-bin", default="hlink")
    run.add_argument("--bwrap-bin", default="bwrap")
    run.add_argument(
        "--resource-limits",
        choices=("auto", "required", "none"),
        default="auto",
        help="apply a user systemd scope to every worker and validation process",
    )
    run.add_argument("--systemd-run-bin", default="systemd-run")
    run.add_argument("--memory-max", default="8G")
    run.add_argument("--tasks-max", type=int, default=512)
    run.add_argument("--cpu-quota", default="400%")
    run.add_argument("--runs-root")
    return parser


def main(argv=None):
    args = _parser().parse_args(argv)
    if args.command == "propose":
        from .wave_proposer import propose_wave, write_proposal_wave

        repo_root = _repo_root(Path.cwd())
        output = Path(args.output) if args.output else _archive_path(repo_root, args.name)
        if output.exists():
            raise SystemExit(
                f"refusing to spend model calls: archive already exists: {output}"
            )
        # Both accept comma-separated lists: models in preference order, keys to share
        # round-robin. One of each is the single client this always built.
        models = [item.strip() for item in args.model.split(",") if item.strip()]
        key_envs = [item.strip() for item in args.api_key_env.split(",") if item.strip()]
        missing = [env for env in key_envs if not os.environ.get(env)]
        if len(missing) == len(key_envs):
            raise SystemExit(f"{' or '.join(key_envs)} is required for the proposer")
        for env in missing:
            print(f"WARNING: {env} is unset and will not be used", file=sys.stderr)
        client = build_pool(
            models, args.endpoint, key_envs,
            seed=args.seed, temperature=args.temperature,
            reasoning_effort=(None if args.reasoning_effort == "none"
                              else args.reasoning_effort),
            timeout=args.timeout_seconds)
        critic_model = None if args.critic_model == "same" else args.critic_model
        critic_key = os.environ.get(args.critic_api_key_env)
        if critic_model and not critic_key:
            # Degrading to a shared client is right -- the split is a robustness measure,
            # not a correctness one -- but silently is not: the 429 it prevents arrives
            # an hour later, in the critic, with the whole wave lost.
            print(f"WARNING: {args.critic_api_key_env} is unset, so the critic shares the"
                  f" proposer's client and quota", file=sys.stderr)
            critic_model = None
        if args.brief and args.brief_file:
            raise SystemExit("pass --brief or --brief-file, not both")
        brief = args.brief_file.read_text() if args.brief_file else (args.brief or "")
        wave = propose_wave(
            repo_root,
            name=args.name,
            brief=brief,
            count=args.count,
            model=models[0],
            endpoint=args.endpoint,
            client=client,
            seed=args.seed,
            temperature=args.temperature,
            reasoning_effort=None if args.reasoning_effort == "none" else args.reasoning_effort,
            critic_model=critic_model,
            critic_endpoint=args.critic_endpoint,
            critic_api_key=critic_key,
            critic_reasoning_effort=(None if args.critic_reasoning_effort == "none"
                                     else args.critic_reasoning_effort),
            critic_samples=max(1, args.critic_samples),
            rounds=args.rounds,
            pool_size=args.pool_size,
            max_batch=args.max_batch,
            timeout=args.timeout_seconds,
        )
        write_proposal_wave(output, wave)
        print(
            f"{output}: {len(wave['proposals'])} accepted, "
            f"{len(wave['rejected'])} rejected"
        )
        if not wave["objective"]["complete"]:
            print(
                f"INCOMPLETE: requested {wave['objective']['requested']}; "
                "increase --rounds after reviewing the archive",
                file=sys.stderr,
            )
            raise SystemExit(2)
        return
    if args.command == "import-legacy":
        from .legacy import build_legacy_wave
        from .wave_proposer import write_proposal_wave

        repo_root = _repo_root(Path.cwd())
        output = Path(args.output) if args.output else _archive_path(repo_root, args.name)
        wave = build_legacy_wave(repo_root, name=args.name, source=args.source)
        write_proposal_wave(output, wave)
        print(
            f"{output}: {len(wave['proposals'])} imported, "
            f"{len(wave['rejected'])} rejected"
        )
        return
    if args.command == "plan":
        import yaml

        from .plan_builder import DEFAULT_CONTEXT_FILES, build_plan, write_plan

        repo_root = _repo_root(Path.cwd())
        wave = yaml.safe_load(Path(args.proposal_wave).read_text())
        if args.skip_implemented:
            from .backlog import unimplemented

            owed = unimplemented(
                wave, repo_root,
                max_attempts=args.max_attempts or None)
            dropped = len(wave.get("proposals") or []) - len(owed)
            if not owed:
                raise SystemExit(
                    f"{args.proposal_wave}: every proposal is implemented or out of"
                    f" attempts; nothing to plan")
            # A copy, because the archive is the record of what was proposed and must not
            # start describing what is left of it.
            wave = {**wave, "proposals": [proposal for proposal, _, _ in owed]}
            print(f"{dropped} of {dropped + len(owed)} proposals already implemented"
                  f" or out of attempts")
        # Resolve a moving ref now: a plan that says HEAD means a different experiment
        # every time it is read, and base_ref is the commit every worktree is cut from.
        base_ref = subprocess.check_output(
            ["git", "rev-parse", f"{args.base_ref}^{{commit}}"],
            cwd=repo_root, text=True,
        ).strip()
        design_choices = None
        if args.design_choices:
            from .design_proposer import propose_wave_design_choices

            # K named approaches plus one unguided variant, so a wave measures whether
            # naming an approach helped at all and not only which name won.
            if args.design_choices + 1 != args.variants:
                raise SystemExit(
                    f"--design-choices {args.design_choices} needs"
                    f" --variants {args.design_choices + 1}: one variant per named"
                    f" approach, plus an unguided baseline"
                )
            api_key = os.environ.get(args.design_api_key_env)
            if not api_key:
                raise SystemExit(
                    f"{args.design_api_key_env} is required for the design proposer"
                )
            design_choices = propose_wave_design_choices(
                wave, args.design_choices, model=args.design_model,
                endpoint=args.design_endpoint, api_key=api_key,
                temperature=0.7, reasoning_effort=None,
            )
            # The baseline is appended here rather than asked for: an "approach" that is
            # the absence of one is not something to spend a design call on.
            design_choices = {proposal_id: tuple(choices) + ("",)
                              for proposal_id, choices in design_choices.items()}
        plan = build_plan(
            wave,
            name=args.name,
            design_choices=design_choices,
            base_ref=base_ref,
            variants=args.variants,
            context_files=tuple(args.context_file) or DEFAULT_CONTEXT_FILES,
        )
        output = (
            Path(args.output)
            if args.output
            else _plan_path(repo_root, args.name)
        )
        write_plan(output, plan)
        print(
            f"{output}: {len(plan['trials'])} trials from "
            f"{len(wave['proposals'])} proposals at {base_ref[:7]}"
        )
        return
    if args.command == "doctor":
        from .doctor import check

        raise SystemExit(check(provider=args.provider, harness=args.harness,
                               live=args.live, timeout=args.timeout).show())
    if args.command == "check-proposals":
        from .wave_proposer import check_proposal_file

        problems = check_proposal_file(args.proposal_wave)
        if problems:
            for problem in problems:
                print(f"PROBLEM: {problem}")
            raise SystemExit(1)
        print(f"{args.proposal_wave}: OK")
        return
    if args.command == "backlog":
        from .backlog import pending

        repo_root = _repo_root(Path.cwd())
        rows = pending(repo_root, max_attempts=args.max_attempts or None)
        for row in rows:
            print(f"{row.wave}\t{row.name}\t{row.attempts} attempts")
        print(f"{len(rows)} unimplemented "
              f"{'proposal' if len(rows) == 1 else 'proposals'}")
        return
    if args.command == "proposal-catalog":
        from .wave_proposer import build_catalog, catalog_record

        repo_root = _repo_root(Path.cwd())
        entries = build_catalog(repo_root)
        record = catalog_record(entries)
        print(json.dumps(record, indent=2, sort_keys=True))
        if args.output:
            _write_json(Path(args.output), [entry.as_dict() for entry in entries])
        return

    plan = load_plan(args.plan)
    if args.command == "check":
        print(
            f"implementation wave {plan.name}: {len(plan.trials)} trials "
            f"implementing proposal wave {plan.proposal_wave or '(unrecorded)'} "
            f"at {plan.base_ref}"
        )
        repo_root = _repo_root(plan.path.parent)
        problems = _plan_problems(plan, repo_root)
        for problem in problems:
            print(f"PROBLEM: {problem}")
        drift = _frozen_module_drift(repo_root, plan.base_ref)
        if drift:
            print(f"WARNING: {drift}")
        for name, members in plan.queues.items():
            print(f"queue\t{name}\t{','.join(members)}")
        for trial in plan.trials:
            print(f"{trial.trial_id}\t{trial.hypothesis or '-'}\t{trial.owned_path}")
        if problems:
            raise SystemExit(1)
    elif args.command == "render":
        trial = next(
            (item for item in plan.trials if item.trial_id == args.trial_id), None
        )
        if trial is None:
            raise SystemExit(f"unknown trial: {args.trial_id}")
        # A template preview: execution builds a model-, seed- and budget-dependent
        # TASK_META and passes it in. The prompt a worker actually got is its
        # prompt.md, in the trial directory.
        print(
            render_implementor_prompt(
                plan, trial, _repo_root(plan.path.parent), pace=args.pace
            ),
            end="",
        )
    else:
        credential_env_names = _worker_credentials(args.credential_env)
        if not credential_env_names:
            print(
                "warning: no worker credential named. The sandbox now builds the worker's"
                " environment from an allowlist, so a provider key reaches it only when"
                " named with --credential-env or TASK_SEARCH_KEY_ENV.",
                file=sys.stderr,
            )
        results = run_plan(
            args.plan,
            model=args.model,
            jobs=args.jobs,
            trial_ids=args.trial,
            queue_names=args.queue,
            agent=args.agent,
            variant=args.variant,
            seed=args.seed,
            forward_seed=args.forward_seed,
            temperature=args.temperature,
            top_p=args.top_p,
            max_steps=args.max_steps,
            timeout_seconds=args.timeout_seconds,
            transient_retries=args.transient_retries,
            retry_backoff_seconds=args.retry_backoff_seconds,
            harness=args.harness,
            hlink_bin=args.hlink_bin,
            bwrap_bin=args.bwrap_bin,
            runs_root=args.runs_root,
            provider=args.provider,
            resource_limit_mode=args.resource_limits,
            systemd_run_bin=args.systemd_run_bin,
            memory_max=args.memory_max,
            tasks_max=args.tasks_max,
            cpu_quota=args.cpu_quota,
            validation_timeout_seconds=args.validation_timeout_seconds,
            credential_env_names=credential_env_names,
            pace=args.pace,
            snapshots=args.snapshots,
        )
        for result in results:
            print(
                f"{result['trial_id']}\t{result['status']}\t"
                f"{result.get('worktree', '-')}"
            )
            if result.get("error"):
                print(f"{result['trial_id']}: {result['error']}", file=sys.stderr)
        if any(result["status"] != "success" for result in results):
            raise SystemExit(1)
