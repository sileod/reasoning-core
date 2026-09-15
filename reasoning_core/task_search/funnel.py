"""How the gate is performing, measured from the archives and the runs they produced.

`backlog` answers what the pipeline still owes and `digest` explains why one trial died.
Neither answers the question a night of running actually raises: is the critic letting
the right fraction through, and is the guided/baseline split earning its compute. Both
were measured by hand the night the critic was redesigned, which is how the redesign got
credit for 22% against 1.4% -- and also how a short critic panel went unnoticed for a
week. A number nobody can recompute is an anecdote.

    python -m reasoning_core.task_search.funnel

Everything here is mechanical: no model calls, no network, just the three directories
the rest of the package already treats as the record.
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import yaml

from .trajectory import trial_directories
# The tally format belongs to the module that writes it.
from .wave_proposer import TALLY
# `generate_samples_P003v1.py` beside a landed task names the trial that won it. The
# module the implementor wrote can be called anything, but this filename cannot.
WINNER = re.compile(r"^generate_samples_(P\d+v\d+)\.py$")


def _archives(repo_root):
    root = Path(repo_root) / "reasoning_core" / "task_search" / "proposals" / "archive"
    return sorted(root.glob("*.yaml")) if root.is_dir() else []


def wave_yield(repo_root):
    """Per wave: what the critic accepted, and how much of a panel decided the rest.

    `pooled` is not a rejection. It is what the wave never reached, or -- since a split
    panel stopped counting as a verdict -- what it reached without a majority either way.
    """
    rows = []
    for path in _archives(repo_root):
        wave = yaml.safe_load(path.read_text()) or {}
        accepted = wave.get("proposals") or []
        rejected = wave.get("rejected") or []
        pooled = wave.get("pool") or []
        tallied = short = tied = 0
        for row in rejected:
            match = TALLY.search(str(row.get("reason") or ""))
            if not match:
                continue
            in_favour, cast = int(match.group(1)), int(match.group(2))
            tallied += 1
            if cast % 2 == 0:
                short += 1
                tied += in_favour * 2 == cast
        rows.append({
            "wave": path.stem,
            "accepted": len(accepted), "rejected": len(rejected), "pooled": len(pooled),
            "seen": len(accepted) + len(rejected) + len(pooled),
            "tallied": tallied, "short_panel": short, "split_panel": tied,
        })
    return rows


def _guidance(repo_root):
    """`(plan, trial id) -> design choice or None`, for plans that ran a baseline.

    The arm label is not the thing being measured and never was. `wave9` splits its
    queues into `v1`, `pilot` and `retry`, which are not arms at all; `wave12` runs
    `v1/v2/v3` all guided, so its `v3` is a third design choice; only a plan that also
    leaves one trial per proposal unguided is answering the question the baseline exists
    to answer. Grouping by label alone silently mixed all three.
    """
    root = Path(repo_root) / "reasoning_core" / "task_search" / "plans"
    guidance = {}
    for path in sorted(root.glob("*.yaml")) if root.is_dir() else ():
        try:
            plan = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        trials = plan.get("trials") or []
        choices = {str(trial.get("design_choice") or "") for trial in trials}
        if len(choices) < 2 or "" not in choices:
            continue
        name = str(plan.get("name") or path.stem)
        for trial in trials:
            guidance[(name, str(trial.get("id") or ""))] = \
                str(trial.get("design_choice") or "") or None
    return guidance


def arm_report(repo_root, runs_root=None):
    """Per arm: what its trials did, and how often it won the landing.

    A wave runs each proposal several times -- guided by one design choice per arm, plus
    an unguided baseline -- and lands the best result. Success rate alone does not settle
    whether the baseline is worth its third of the compute, because an arm can succeed
    often and still rarely produce the draft that wins; both numbers are needed together,
    and only from plans that actually ran a baseline against guided arms.
    """
    # Resolved, because the sibling runs directory is named after the repo directory and
    # a relative `.` has no name to be named after.
    repo_root = Path(repo_root).resolve()
    runs_root = (Path(runs_root) if runs_root
                 else repo_root.parent / f".{repo_root.name}-task-search")
    guidance = _guidance(repo_root)
    compared = {plan for plan, _ in guidance}
    outcomes, guided = {}, {}
    if runs_root.is_dir():
        for wave in sorted(runs_root.iterdir()):
            if not wave.is_dir() or wave.name not in compared:
                continue
            for run in sorted(path for path in wave.iterdir() if path.is_dir()):
                for trial in trial_directories(run):
                    key = (wave.name, trial.name)
                    if key not in guidance:
                        continue
                    record = trial / "run.json"
                    if not record.is_file():
                        continue
                    try:
                        status = json.loads(record.read_text()).get("status") or "unknown"
                    except (ValueError, OSError):
                        continue
                    arm = f"v{trial.name.split('v')[-1]}"
                    outcomes.setdefault(arm, Counter())[status] += 1
                    guided[arm] = guidance[key] is not None

    generated = repo_root / "reasoning_core" / "tasks" / "generated"
    won = Counter()
    for path in sorted(generated.rglob("generate_samples_*.py")) if generated.is_dir() else ():
        match = WINNER.match(path.name)
        relative = path.relative_to(generated)
        if not (match and relative.parts):
            continue
        key = (relative.parts[0], match.group(1))
        if key in guidance:
            arm = f"v{match.group(1).split('v')[-1]}"
            won[arm] += 1
            guided.setdefault(arm, guidance[key] is not None)

    # Union, not just the arms with runs on disk: run directories are retired after a
    # week and the tasks they landed are not, so an arm whose evidence has aged out would
    # otherwise drop off the report that is meant to justify keeping it.
    return [{"arm": arm,
             "guided": guided.get(arm, True),
             "trials": sum(outcomes.get(arm, ()).values()),
             "success": outcomes.get(arm, Counter()).get("success", 0),
             "landed": won.get(arm, 0),
             "failures": {status: n
                          for status, n in outcomes.get(arm, Counter()).most_common()
                          if status != "success"}}
            for arm in sorted(set(outcomes) | set(won))]


def report(repo_root, runs_root=None):
    """Both tables, as text."""
    lines = [f"{'wave':38s} {'acc':>4s} {'rej':>4s} {'pool':>5s} {'rate':>6s}"
             f" {'short':>6s} {'split':>6s}"]
    waves = wave_yield(repo_root)
    for row in waves:
        rate = f"{100 * row['accepted'] / row['seen']:.0f}%" if row["seen"] else "-"
        lines.append(f"{row['wave']:38s} {row['accepted']:4d} {row['rejected']:4d}"
                     f" {row['pooled']:5d} {rate:>6s}"
                     f" {row['short_panel']:6d} {row['split_panel']:6d}")
    seen = sum(row["seen"] for row in waves)
    got = sum(row["accepted"] for row in waves)
    lines.append(f"{'TOTAL':38s} {got:4d} {'':4s} {'':5s}"
                 f" {(f'{100 * got / seen:.0f}%' if seen else '-'):>6s}"
                 f" {sum(r['short_panel'] for r in waves):6d}"
                 f" {sum(r['split_panel'] for r in waves):6d}")

    lines += ["", f"{'arm':>5s} {'guidance':>9s} {'success':>9s} {'landed':>7s}"
                  f"  failures"]
    for row in arm_report(repo_root, runs_root):
        rate = f"{row['success']}/{row['trials']}"
        failures = ", ".join(f"{status} {n}" for status, n in row["failures"].items())
        lines.append(f"{row['arm']:>5s} {('guided' if row['guided'] else 'baseline'):>9s}"
                     f" {rate:>9s} {row['landed']:7d}  {failures or '-'}")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--runs-root")
    parser.add_argument("--json", action="store_true", help="machine-readable instead")
    args = parser.parse_args(argv)
    if args.json:
        print(json.dumps({"waves": wave_yield(args.repo_root),
                          "arms": arm_report(args.repo_root, args.runs_root)}, indent=1))
    else:
        print(report(args.repo_root, args.runs_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
