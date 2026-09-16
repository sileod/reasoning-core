"""What was proposed, what got built, and what is still owed.

Three directories already answer this between them, so the backlog needs no state of its
own and has none to go stale: the proposal archive says what was asked for,
`reasoning_core/tasks` says what exists, and the plans say what was attempted -- but only
alongside `plans/outcomes`, which says which of those attempts actually ran. A plan on its
own is intent, and reading intent as history is how this stalled for six days: killed
waves left trials that never launched, their ideas were counted out of budget, and the
service reported `0 proposals owed` while the backlog was full. A service implementing the
backlog reads those directories, and can be interrupted at any point because they say
where it stopped.

The attempt count is the half that is easy to leave out and expensive to miss. Every
proposal with no task is not equally owed: as of this writing the five unimplemented ones
had been attempted four to seven times each, so they are the ideas that resist
implementation, not the ideas nobody got to. Re-running them forever is how an
unsupervised service spends a night on the same five failures.
"""
from collections import Counter
from dataclasses import dataclass
import ast
import itertools
import os
from pathlib import Path
import re

import yaml

from .wave_proposer import _snake, _task_entries


# `wave8` fans one proposal into `strongly_connected_component_v1` and `_v2`; the idea
# they are drafts of is the name without the suffix.
VARIANT_SUFFIX = re.compile(r"_v\d+(?:d\d+)?$")


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


def landed_proposals(repo_root):
    """`(plan directory, proposal id)` for every generated task that names its proposal.

    A landed task is named by the module the implementor wrote, not by the proposal that
    asked for it: `regular_expression_derivative` shipped as `reg_exp_derivative`, and
    matching on the name alone therefore said the proposal was still owed. It would have
    been built again every night, forever, against a task that already exists.

    `TASK_META["hypothesis"]` carries the proposal id and the plan directory carries the
    wave, which together identify it whatever the implementor chose to call the class.
    """
    root = Path(repo_root) / "reasoning_core" / "tasks" / "generated"
    found = set()
    for path in sorted(root.rglob("*.py")) if root.is_dir() else ():
        relative = path.relative_to(root)
        if len(relative.parts) < 2 or path.name.startswith(("_", "test_", "generate_")):
            continue
        try:
            tree = ast.parse(path.read_text(), filename=str(path))
        except (SyntaxError, OSError):
            continue
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Assign)
                    and any(getattr(target, "id", "") == "TASK_META"
                            for target in node.targets)):
                continue
            try:
                meta = ast.literal_eval(node.value)
            except ValueError:
                continue
            marker = str((meta or {}).get("hypothesis") or "").strip()
            if marker:
                found.add((relative.parts[0], marker))
    return frozenset(found)


def outcomes(repo_root, plan_name):
    """Trial ids this plan actually spent a run on, or None if it never recorded any.

    A plan is a statement of intent. It says nothing about what happened, and for six days
    that silence read as failure: a wave planned and then killed -- by a restart, a quota
    wall, an interrupt -- left trials on disk that had never launched, `attempted` counted
    them against the idea's budget, and the service reported `0 proposals owed` every
    fifteen minutes while the backlog was full. Nothing was broken loudly enough to notice.

    `None` rather than an empty set when there is no record, because the two mean opposite
    things: a plan from before this file existed was probably run, while a plan with an
    empty record demonstrably was not.
    """
    path = (Path(repo_root) / "reasoning_core" / "task_search" / "plans" / "outcomes"
            / f"{plan_name}.yaml")
    if not path.is_file():
        return None
    try:
        return set(yaml.safe_load(path.read_text()) or {})
    except yaml.YAMLError:
        return None


def record_outcomes(repo_root, plan_name, results):
    """Merge `{trial id: status}` into this plan's durable record of what ran.

    Merged rather than replaced: a plan can be run more than once, in pieces, and what a
    later run does not cover is still spent. Kept beside the plans but in their own
    directory, because `attempted` globs `*.yaml` there and `next_round` globs
    `<wave>_r*.yaml` -- a sibling file would be read as a plan and would take a round
    number with it.
    """
    directory = Path(repo_root) / "reasoning_core" / "task_search" / "plans" / "outcomes"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{plan_name}.yaml"
    known = {}
    if path.is_file():
        try:
            known = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            known = {}
    known.update({str(trial): str(status) for trial, status in results.items()})
    temporary = path.with_suffix(".yaml.tmp")
    temporary.write_text(yaml.safe_dump(known, sort_keys=True))
    os.replace(temporary, path)
    return known


def attempted(repo_root):
    """Comparison key -> how many rounds have already been spent on it.

    A round is one plan that actually ran the idea, however many trials it spent doing
    so. Counting trials instead made the retry budget move whenever the fan-out changed:
    with two design choices and a baseline, one wave spent three trials and
    `--max-attempts 3` retired the idea after a single wave -- and asking for more
    generators per approach would have retired it in the middle of the first one. The
    number of attempts an idea is worth and the number of generators a wave asks for are
    separate questions, so they are separate numbers.

    A trial only counts once it has an outcome. Plans written before outcomes were
    recorded have no record and keep the old, conservative reading -- every trial counts
    as having run -- so fixing this cannot reopen a year of ideas that genuinely were
    tried.
    """
    root = Path(repo_root) / "reasoning_core" / "task_search" / "plans"
    counts = Counter()
    for path in sorted(root.glob("*.yaml")):
        try:
            plan = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        ran = outcomes(repo_root, str(plan.get("name") or path.stem))
        spent = set()
        for trial in plan.get("trials", ()):
            if ran is not None and str(trial.get("id") or "") not in ran:
                continue
            # `idea` is "<task name> (variant 2 of 3)", and the task name is what the
            # proposal was called before the variant suffix was appended.
            idea = str(trial.get("idea", "")).split(" (", 1)[0]
            name = _snake(idea) or _snake(Path(str(trial.get("owned_path", ""))).name)
            if name:
                spent.add(comparison_key(VARIANT_SUFFIX.sub("", name)))
        counts.update(spent)
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


def unimplemented(wave, repo_root, *, max_attempts=None, built=None, tried=None,
                  landed=None):
    """The proposals in one loaded wave that no task implements yet.

    `max_attempts` drops the ideas already tried that many times or more; None keeps them.
    `built`, `tried` and `landed` let a caller sweeping many waves scan the package once.
    """
    built = implemented(repo_root) if built is None else built
    tried = attempted(repo_root) if tried is None else tried
    landed = landed_proposals(repo_root) if landed is None else landed
    # A landed task carries the name its implementor chose, which is often not the name
    # the proposal used, so matching on names alone leaves the proposal owed forever.
    shipped = {marker for plan, marker in landed
               if plan.startswith(_snake(wave.get("name") or "\0") + "_r")}
    rows = []
    for proposal in wave.get("proposals") or ():
        name = _snake(proposal.get("name"))
        if not name:
            continue
        key = comparison_key(name)
        if key in built or str(proposal.get("id") or "\0") in shipped:
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
