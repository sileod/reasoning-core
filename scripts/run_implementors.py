#!/usr/bin/env python3
"""Implement the backlog: plan, run and land every proposal no task covers yet.

A wave at a time, in the order the ideas arrived, for as long as it is left running. Each
wave is three subprocesses -- `plan`, `run`, then `land --apply` -- because that is the
pipeline a person runs by hand, and a service that runs a different one would drift from
it. The proposer writes archives on its own schedule (`propose_from_briefs.py`), so an
idle pass is normal: with nothing owed this sleeps and looks again.

Resume is the repository. `backlog` derives what is owed from the archive, the package and
the plans, so a service killed mid-wave rediscovers exactly what is left on the next pass
and needs no state file. That also dedupes across waves for free: two archives proposing
the same idea are two rows until the first one lands, and one row after.

    scripts/run_implementors.py --once --dry-run       # what would it do
    scripts/run_implementors.py --max-attempts 3       # then leave it running

Provider and credential come from the environment the CLI already reads
(TASK_SEARCH_PROVIDER, TASK_SEARCH_KEY_ENV), so this stays provider-agnostic.
"""
import argparse
from collections import Counter
from pathlib import Path
import shutil
import subprocess
import sys
import time

import yaml

from reasoning_core.task_search.backlog import (
    next_round, pending, plan_name, unimplemented)

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "reasoning_core" / "task_search" / "proposals" / "archive"
PLANS = ROOT / "reasoning_core" / "task_search" / "plans"
# Where `run` puts a wave's trials, and where `land` looks for them. Kept in step with
# implementation_runner.run_plan, which defaults runs_root to the same path.
RUNS = ROOT.parent / f".{ROOT.name}-task-search"
# Consecutive wave failures that mean the machine or the provider is gone rather than one
# wave being unlucky. Without it an overnight service fails identically until morning.
GIVE_UP_AFTER = 3


# Run directories to delete per pass. Deleting one is a recursive unlink of a whole
# worktree over NFS and takes minutes; a first pass facing a year of them would stall the
# service for an hour before planning anything. The backlog drains over a few passes, and
# a steady state has one or two a night, so the cap is only ever felt once.
RETIRE_PER_PASS = 4


def retire_runs(days, *, apply=True, limit=RETIRE_PER_PASS):
    """Delete run worktrees older than `days` and unregister them.

    Every trial is a `git worktree add`, and git reads all of .git/worktrees over NFS each
    time it makes another: at 1,273 registrations that add took ~50 seconds, which is most
    of a short trial. Landing has already copied what it wanted out of a finished run, and
    a worktree is regenerable from the commit it was cut from, so keeping them costs 15G
    and an hour a night to buy nothing. Deleting the directory is what makes the
    registration stale; `git worktree prune` is what then removes it.
    """
    cutoff = time.time() - days * 86400
    spent = sorted((directory for wave in RUNS.glob("*") if wave.is_dir()
                    for directory in wave.glob("*")
                    if directory.is_dir() and directory.stat().st_mtime < cutoff),
                   key=lambda directory: directory.stat().st_mtime)[:limit]
    if apply:
        for directory in spent:
            shutil.rmtree(directory, ignore_errors=True)
        subprocess.run(["git", "worktree", "prune"], cwd=ROOT, check=False)
    return spent


def still_owed(arguments, wave):
    """What this wave owes right now, which is not what it owed at the top of the pass.

    Two archives often propose the same idea, and the wave that runs first lands it. Asking
    again here is what keeps the second wave from being planned for nothing and counted as
    a failure when `plan` correctly refuses to build an empty one.
    """
    document = yaml.safe_load((ARCHIVE / f"{wave}.yaml").read_text()) or {}
    return unimplemented(document, ROOT, max_attempts=arguments.max_attempts or None)


def steps(arguments, wave, name):
    archive = ARCHIVE / f"{wave}.yaml"
    plan_path = PLANS / f"{name}.yaml"
    # K named approaches plus one unguided variant, so the service asks for a behaviour
    # and derives the count rather than offering a second knob that can only be set wrong.
    variants = arguments.design_choices + 1
    build = [sys.executable, "-m", "reasoning_core.task_search", "plan", str(archive),
             "--name", name, "--skip-implemented",
             "--max-attempts", str(arguments.max_attempts),
             "--variants", str(variants)]
    if arguments.design_choices:
        build += ["--design-choices", str(arguments.design_choices)]
    run = [sys.executable, "-m", "reasoning_core.task_search", "run", str(plan_path),
           "--harness", arguments.harness, "--jobs", str(arguments.jobs),
           "--max-steps", str(arguments.max_steps),
           "--timeout-seconds", str(arguments.timeout_seconds),
           "--resource-limits", "required"]
    if arguments.model:
        run += ["--model", arguments.model]
    land = [sys.executable, "-m", "reasoning_core.task_search.land",
            str(RUNS / name), "--plan", str(plan_path), "--apply",
            # Which approach each landed task was asked to take, taken from the plan
            # rather than from the worktree. Without it the guided arms and the unguided
            # baseline are indistinguishable once landed, and the baseline variant exists
            # for exactly that comparison -- k3_rule_induction landed 5/5 from the first
            # guided choice, 2/5 from the second, and 4/5 from no guidance at all.
            "--json-out", str(arguments.log_dir / f"{name}.landed.json")]
    # The flag is whether the step's exit status decides the wave. `run` exits non-zero
    # when any single trial failed, which is the ordinary shape of a wave rather than a
    # problem: the first wave this service ran was four successes and one
    # `answers_impossible`, and treating that as a failed wave skipped landing and threw
    # the four away. Only `land` can say whether a wave produced anything -- it refuses a
    # run with no successful trials -- so it is the step whose status is the wave's.
    return [("plan", build, True), ("run", run, False), ("land", land, True)]


def implement(arguments, wave, log_dir):
    """Plan, run and land one wave. True unless a step failed."""
    owed = still_owed(arguments, wave)
    if not owed:
        print("    nothing left to implement", flush=True)
        return True
    name = plan_name(wave, next_round(ROOT, wave))
    print(f"  {time.strftime('%H:%M')} {name}", flush=True)
    for label, command, decides in steps(arguments, wave, name):
        if arguments.dry_run:
            print(f"    would {label}: {' '.join(command[2:])}", flush=True)
            continue
        started = time.time()
        log = log_dir / f"{name}.{label}.log"
        with log.open("w") as handle:
            completed = subprocess.run(command, cwd=ROOT, stdout=handle,
                                       stderr=subprocess.STDOUT)
        minutes = (time.time() - started) / 60
        if completed.returncode == 0:
            print(f"    {label} ok in {minutes:.0f}m", flush=True)
            continue
        note = "FAILED" if decides else "some trials failed"
        print(f"    {label} {note} (exit {completed.returncode}) after"
              f" {minutes:.0f}m -- see {log}", flush=True)
        if decides:
            return False
    return True


def waves_owed(arguments):
    """Wave name -> how many of its proposals are owed, oldest wave first."""
    return Counter(row.wave for row
                   in pending(ROOT, max_attempts=arguments.max_attempts or None))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--design-choices", type=int, default=2,
                        help="named approaches to implement per proposal; each proposal"
                             " also gets one unguided baseline variant, so K here is K+1"
                             " implementations. 0 implements the summary alone")
    parser.add_argument("--max-attempts", type=int, default=3,
                        help="stop offering an idea once this many plan trials have"
                             " tried it; 0 retries forever")
    parser.add_argument("--harness", default="opencode",
                        choices=("opencode", "mini", "agy"))
    parser.add_argument("--model", default="",
                        help="implementor model; empty uses the CLI default")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--max-steps", type=int, default=56)
    parser.add_argument("--timeout-seconds", type=int, default=1800)
    parser.add_argument("--poll-seconds", type=int, default=900,
                        help="wait this long when nothing is owed, then look again")
    parser.add_argument("--once", action="store_true",
                        help="one pass over what is owed now, then stop")
    parser.add_argument(
        "--keep-runs-days", type=int, default=7,
        help="delete run worktrees older than this at each pass. Landing has already"
             " taken what it wanted from a finished run, and git re-reads every"
             " registration over NFS on each new worktree, so keeping them slows down"
             " exactly the thing that makes them")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-dir", type=Path, default=ROOT / "runs" / "implementors")
    arguments = parser.parse_args()
    arguments.log_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    while True:
        # Before planning, not after: a pass that is about to cut dozens of worktrees wants
        # the stale ones gone first, and an idle pass is where the tidying is free.
        retired = retire_runs(arguments.keep_runs_days, apply=not arguments.dry_run)
        if retired:
            print(f"{time.strftime('%H:%M')} retired {len(retired)} spent run"
                  f" worktrees older than {arguments.keep_runs_days}d", flush=True)
        owed = waves_owed(arguments)
        total = sum(owed.values())
        print(f"{time.strftime('%H:%M')} {total} proposals owed across"
              f" {len(owed)} waves", flush=True)
        for wave, count in owed.items():
            print(f"  {wave}: {count}", flush=True)
            if implement(arguments, wave, arguments.log_dir):
                failures = 0
            else:
                failures += 1
                if failures >= GIVE_UP_AFTER:
                    print(f"stopping: {failures} waves failed in a row", flush=True)
                    return 1
        if arguments.once:
            return 0
        if arguments.dry_run:
            return 0
        time.sleep(arguments.poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
