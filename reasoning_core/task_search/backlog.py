"""What was proposed, what got built, and what is still owed.

Three directories already answer this between them, so the backlog needs no state of its
own and has none to go stale: the proposal archive says what was asked for,
`reasoning_core/tasks` says what exists, and the plans say what was already attempted.
A service implementing the backlog reads those three, and can be interrupted at any point
because the same three directories say where it stopped.

The attempt count is the half that is easy to leave out and expensive to miss. Every
proposal with no task is not equally owed: as of this writing the five unimplemented ones
had been attempted four to seven times each, so they are the ideas that resist
implementation, not the ideas nobody got to. Re-running them forever is how an
unsupervised service spends a night on the same five failures.
"""
from collections import Counter
from dataclasses import dataclass
import itertools
from pathlib import Path
import re

import yaml

from .wave_proposer import _snake, _task_entries


# `wave8` fans one proposal into `strongly_connected_component_v1` and `_v2`; the idea
# they are drafts of is the name without the suffix.
VARIANT_SUFFIX = re.compile(r"_v\d+$")


def comparison_key(name):
    """A task name reduced to what survives an implementor renaming it.

    A proposal asks for `BTreePromotedKey` and the task that implements it is called
    `b_tree_promoted_key`, because `_snake` breaks before every capital while the proposal
    wrote the same word lowercase. Underscore placement is the whole difference, and
    dropping underscores matches those two without matching anything else: no two distinct
    ideas in the catalog differ only by where the underscores fall.
    """
    return _snake(name).replace("_", "")


def implemented(repo_root):
    """Comparison keys for every task in the package, generated ones included."""
    return frozenset(comparison_key(entry.name) for entry in _task_entries(repo_root))


def attempted(repo_root):
    """Comparison key -> how many plan trials have already tried to build it.

    Counted in trials rather than plans because a plan with three variants spends three
    implementor runs on the idea, and the budget being protected is implementor runs.
    """
    root = Path(repo_root) / "reasoning_core" / "task_search" / "plans"
    counts = Counter()
    for path in sorted(root.glob("*.yaml")):
        try:
            plan = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        for trial in plan.get("trials", ()):
            # `idea` is "<task name> (draw 2 of 3)", and the task name is what the
            # proposal was called before the variant suffix was appended.
            idea = str(trial.get("idea", "")).split(" (", 1)[0]
            name = _snake(idea) or _snake(Path(str(trial.get("owned_path", ""))).name)
            if name:
                counts[comparison_key(VARIANT_SUFFIX.sub("", name))] += 1
    return counts


def plan_name(wave, round_number):
    """`k3_reusable-operations` -> `k3_reusable_operations_r2`.

    A plan name becomes a package directory under `reasoning_core/tasks/generated` and the
    contract audit imports candidates by module path, so it has to be a Python identifier
    -- a proposal wave named with a dash is not one. The round number keeps a set of ideas
    re-implementable: one wave of proposals can be built more than once.
    """
    return f"{_snake(wave)}_r{round_number}"


def next_round(repo_root, wave):
    """The first round number this wave has no plan for."""
    taken = {path.stem for path
             in (Path(repo_root) / "reasoning_core" / "task_search" / "plans").glob(
                 f"{_snake(wave)}_r*.yaml")}
    return next(number for number in itertools.count(1)
                if plan_name(wave, number) not in taken)


@dataclass(frozen=True)
class Pending:
    """One proposal that no task implements yet."""

    wave: str
    path: Path
    proposal: dict
    name: str
    attempts: int


def unimplemented(wave, repo_root, *, max_attempts=None, built=None, tried=None):
    """The proposals in one loaded wave that no task implements yet.

    `max_attempts` drops the ideas already tried that many times or more; None keeps them.
    `built` and `tried` let a caller sweeping many waves scan the package once.
    """
    built = implemented(repo_root) if built is None else built
    tried = attempted(repo_root) if tried is None else tried
    rows = []
    for proposal in wave.get("proposals") or ():
        name = _snake(proposal.get("name"))
        if not name:
            continue
        key = comparison_key(name)
        if key in built:
            continue
        attempts = tried.get(key, 0)
        if max_attempts is not None and attempts >= max_attempts:
            continue
        rows.append((proposal, name, attempts))
    return rows


def pending(repo_root, *, max_attempts=None):
    """Every unimplemented proposal across the archive, oldest wave first.

    Waves are ordered by the time their file was last written, so a service works through
    the backlog in the order the ideas arrived rather than in alphabetical order.
    """
    repo_root = Path(repo_root)
    archive = repo_root / "reasoning_core" / "task_search" / "proposals" / "archive"
    built, tried = implemented(repo_root), attempted(repo_root)
    rows = []
    if not archive.is_dir():
        return rows
    for path in sorted(archive.glob("*.yaml"), key=lambda item: item.stat().st_mtime):
        try:
            wave = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        if wave.get("kind") != "sft_task_proposals":
            continue
        name = str(wave.get("name") or path.stem)
        for proposal, task_name, attempts in unimplemented(
                wave, repo_root, max_attempts=max_attempts, built=built, tried=tried):
            rows.append(Pending(name, path, proposal, task_name, attempts))
    return rows
