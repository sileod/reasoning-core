"""Evolve the implementor's notes with GEPA, scored past the gates.

Passing every gate means a task runs; it does not mean the task is worth training on. So a
trial scores in two bands. A failure earns up to 0.4 for how far down the gate order it got
(`FAILURE_PRECEDENCE`). A success earns 0.5 plus half the mean of five checks on fresh
examples generated from the candidate in the trial's sandbox:

- correct, wellposed: Jev's p(yes) that the reference answer is right and the prompt is
  unambiguous (AUROC 0.87 for `correct` on swapped answers, 2026-09-26);
- no_shortcut: 1 - Jev's p(a superficial shortcut finds the answer);
- hard_at_top: 1 - Jev's p(answerable at a glance) at the top level. Jev tracks absolute
  difficulty across tasks but not a ladder's slope, so this checks the top is not trivial
  and says nothing about spacing;
- novel: the share of registry tasks whose own nearest neighbour is closer than this
  candidate's (bge-m3 cosine). Raw cosine is useless as a score: registry neighbours sit at
  0.61-0.75 (p10-p90, 2026-10-16), so a rank against them is what separates.

What GEPA evolves is one block of notes appended to the implementor prompt
(`render_implementor_prompt(notes=...)`); every gate, the sandbox and the plan stay fixed.
The reflection model reads each trial's digest transcript, its judge scores and its
nearest task. Runs pass `record=False`, so an experiment never spends a proposal's
attempts, and plans live under the output directory, never in `plans/`.
"""
from __future__ import annotations

import hashlib
import json
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import yaml

from ..evaluation.judge import make_judge
from ..evaluation.judge_llm import LLMJudge
from ..evaluation.signals import DIMENSIONS, profile, sample
from . import embedding
from .backlog import comparison_key, implemented
from .digest import _transcript
from .implementation_runner import run_plan
from .plan_builder import build_plan, write_plan
from .sandbox import _minimal_environment, _sandbox_command
from .trajectory import read
from .validation import FAILURE_PRECEDENCE, _task_classes
from .wave_proposer import _snake

LEVELS = (0, 6)
PER_LEVEL = 4
JUDGED = tuple(d for d in DIMENSIONS if d.name in ("correct", "wellposed", "shortcut", "glance"))
ORDER = [status for status, _ in FAILURE_PRECEDENCE]
REPO_ROOT = Path(__file__).resolve().parents[2]

_GENERATE = r"""
import importlib, json, random, sys
module, name, levels, n = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), int(sys.argv[4])
task = getattr(importlib.import_module(module), name)()
for level in levels:
    random.seed(level)
    for _ in range(n):
        example = task.generate_example(level=level, timeout=10)
        print(json.dumps({"level": level, "prompt": example.prompt, "answer": str(example.answer)}))
"""


def proposals(repo_root, count, seed=0, archive=None):
    """`count` proposals no task implements yet, in a seeded order, from `archive` (the
    proposal archive by default; a GEPA test pool is a directory of the same files).

    A proposal whose name contains a shipped task's name is that task renamed --
    `grid_light_occlusion_delta` beside `light_occlusion_delta` scored novelty 0.015 -- and
    would only measure that it cannot be novel. Keys under 12 characters (`sort`, `parity`)
    are too common inside other names to say so.
    """
    built = implemented(repo_root)
    long_keys = [key for key in built if len(key) >= 12]
    archive = Path(archive or Path(repo_root) / "reasoning_core/task_search/proposals/archive")
    rows = []
    for path in sorted(archive.glob("*.yaml")):
        wave = yaml.safe_load(path.read_text()) or {}
        if wave.get("kind") != "sft_task_proposals":
            continue
        for proposal in wave.get("proposals") or ():
            name, summary = _snake(proposal.get("name")), str(proposal.get("summary", "")).strip()
            key = comparison_key(name)
            if name and summary and key not in built and not any(k in key for k in long_keys):
                built |= {key}   # two waves proposing one idea is one example
                rows.append({"name": name, "summary": summary,
                             "source": f"{wave.get('name')}/{proposal.get('id')}"})
    random.Random(seed).shuffle(rows)
    return rows[:count]


def run(notes, items, *, out, repo_root, **options):
    """Implement `items` once each with `notes` in the prompt: [(record, owned path)]."""
    name = "gepa_" + hashlib.sha256(json.dumps([notes, items]).encode()).hexdigest()[:10]
    wave = {"kind": "sft_task_proposals", "name": name, "proposals": [
        {"id": f"G{i:03d}", "name": item["name"], "summary": item["summary"]}
        for i, item in enumerate(items)]}
    plan = build_plan(wave, name=name)
    plan_path = Path(out) / "plans" / f"{name}.yaml"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    write_plan(plan_path, plan)
    results = {r["trial_id"]: r for r in run_plan(
        plan_path, repo_root=repo_root, runs_root=Path(out) / "runs", notes=notes or None,
        record=False, **options)}
    return [(results.get(trial["id"], {"status": "orchestration_error"}), trial["owned_path"])
            for trial in plan["trials"]]


def examples(record, owned_path, levels=LEVELS, n=PER_LEVEL):
    """Fresh examples from a successful candidate, generated inside its own sandbox."""
    worktree = Path(record["worktree"])
    module, name = _task_classes(worktree, owned_path)[0]
    command = _sandbox_command(
        [sys.executable, "-c", _GENERATE, module, name, json.dumps(list(levels)), str(n)],
        worktree=worktree, owned_path=owned_path, runtime_root=worktree.parent / "gepa_runtime")
    done = subprocess.run(command, cwd=worktree, env=_minimal_environment(),
                          capture_output=True, text=True, timeout=300)
    return [json.loads(line) for line in done.stdout.splitlines() if line.startswith("{")]


def build_index(path, *, workers=8, seed=43):
    """Embed two level-0 prompts of every registry task once: the novelty reference."""
    import reasoning_core

    names = reasoning_core.list_tasks(include_generated=True)
    with ProcessPoolExecutor(workers) as pool:
        prompts = list(pool.map(_level0_prompts, names, [seed] * len(names)))
    kept = [(name, texts) for name, texts in zip(names, prompts) if texts]
    vectors = np.array([_mean(embedding.embed(texts)) for _, texts in kept])
    similarities = vectors @ vectors.T
    np.fill_diagonal(similarities, -1)
    np.savez(path, names=np.array([name for name, _ in kept]), vectors=vectors,
             neighbour=similarities.max(axis=1))


def _level0_prompts(name, seed):
    try:
        return [row["prompt"] for row in sample(name, 0, 2, seed)[1]]
    except Exception:  # noqa: BLE001 - a task that cannot generate has nothing to be near
        return []


def _mean(vectors):
    mean = np.mean(np.asarray(vectors), axis=0)
    return mean / np.linalg.norm(mean)


def nearest(index, prompts):
    """(name, cosine, novelty) of the registry task closest to these prompts."""
    similarities = index["vectors"] @ _mean(embedding.embed(prompts))
    best = int(np.argmax(similarities))
    cosine = float(similarities[best])
    return str(index["names"][best]), cosine, float(np.mean(index["neighbour"] > cosine))


def score(record, judged=(), near=None):
    """(score, the parts it was made of) for one trial; see the module docstring."""
    status = record.get("status")
    if status != "success":
        progress = (ORDER.index(status) + 1) / (len(ORDER) + 1) if status in ORDER else 0.0
        return 0.4 * progress, {"status": status}
    if not judged or near is None:
        return 0.5, {"status": status, "unscored": "no examples could be generated"}
    top = max(row["level"] for row in judged)
    parts = {
        "correct": np.mean([row["jev"]["correct"] for row in judged]),
        "wellposed": np.mean([row["jev"]["wellposed"] for row in judged]),
        "no_shortcut": 1 - np.mean([row["jev"]["shortcut"] for row in judged]),
        "hard_at_top": 1 - np.mean([row["jev"]["glance"] for row in judged
                                    if row["level"] == top]),
        "novel": near[2],
    }
    parts = {key: round(float(value), 3) for key, value in parts.items()}
    return 0.5 + 0.5 * float(np.mean(list(parts.values()))), {"status": status, **parts}


def evaluate(notes, items, *, out, repo_root, index, judge, **options):
    """[(score, side info)] for `items` implemented under `notes`."""
    scored = []
    for record, owned_path in run(notes, items, out=out, repo_root=repo_root, **options):
        judged, near, info = [], None, {}
        if record.get("status") == "success":
            try:
                judged = examples(record, owned_path)
                for row in judged:
                    row["jev"] = profile(row, {"jev": judge}, JUDGED)["jev"]
                judged = [row for row in judged if None not in row["jev"].values()]
                near = nearest(index, [row["prompt"] for row in judged]) if judged else None
            except Exception as error:  # noqa: BLE001 - an unscorable success is still one
                info["scoring_error"] = f"{type(error).__name__}: {error}"[:300]
        value, parts = score(record, judged, near)
        if near:
            info["nearest_task"] = f"{near[0]} (cosine {near[1]:.2f})"
        if judged:
            worst = min(judged, key=lambda row: row["jev"]["correct"])
            info["least_trusted_example"] = {key: worst[key][:600] for key in ("prompt", "answer")}
        if record.get("worktree"):
            trial = Path(record["worktree"]).parent
            info["trajectory"] = _transcript(trial, read(trial))
        scored.append((value, {**parts, **info}))
    return scored


OBJECTIVE = ("Write notes appended to a coding agent's prompt so that the procedural "
             "reasoning tasks it implements pass every gate and are also correct, "
             "unambiguous, free of shortcuts, hard at the top level, and unlike existing tasks.")
BACKGROUND = ("Each example is a task proposal; the agent implements it as a Python generator "
              "under a fixed prompt plus these notes, in a sandbox, then automated gates and "
              "an LLM judge score it. Notes must be general advice that helps on unseen "
              "proposals, under 300 words; never restate the fixed prompt or name one task.")


def optimize(out, *, count=16, holdout=4, budget=40, minibatch=3, seed=0, jobs=4,
             test_pool=None, **options):
    """Run GEPA over the notes, then score the empty and the best notes on `test_pool`.

    `test_pool` is a directory of proposal waves GEPA never sees -- written by `propose
    --output` from briefs, so their ideas did not exist when the notes were evolved. It is
    the one measurement of whether the notes generalise rather than fit the training
    proposals; selection on `holdout` proposals is too small to say so.
    """
    from gepa.optimize_anything import (EngineConfig, GEPAConfig, ReflectionConfig,
                                        optimize_anything)

    out, repo_root = Path(out), REPO_ROOT
    out.mkdir(parents=True, exist_ok=True)
    index_path = out / "novelty_index.npz"
    if not index_path.exists():
        build_index(index_path)
    index, judge = dict(np.load(index_path)), make_judge("jev")
    items = proposals(repo_root, count, seed)
    reviewer = LLMJudge()

    def scored(notes, chosen):
        return evaluate(notes, chosen, out=out, repo_root=repo_root, index=index, judge=judge,
                        jobs=jobs, **options)

    def batch(pairs):
        results = {notes: iter(scored(notes, [item for candidate, item in pairs
                                              if candidate == notes]))
                   for notes in dict.fromkeys(notes for notes, _ in pairs)}
        return [next(results[notes]) for notes, _ in pairs]

    result = optimize_anything(
        "", batch_evaluator=batch, dataset=items[holdout:], valset=items[:holdout],
        objective=OBJECTIVE, background=BACKGROUND,
        config=GEPAConfig(
            engine=EngineConfig(run_dir=str(out / "gepa"), seed=seed, max_metric_calls=budget),
            reflection=ReflectionConfig(
                reflection_minibatch_size=minibatch,
                reflection_lm=lambda prompt: reviewer.complete(
                    "You improve instructions for autonomous coding agents.", prompt,
                    max_tokens=4096, temperature=0.7))))
    best = result.best_candidate
    (out / "best_notes.md").write_text(best + "\n")
    if test_pool:
        tests = proposals(repo_root, 10**6, seed, archive=test_pool)
        report = {label: [value for value, _ in scored(notes, tests)]
                  for label, notes in (("empty", ""), ("best", best))}
        report = {label: {"mean": float(np.mean(values)), "scores": values}
                  for label, values in report.items()}
        (out / "test_report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps({label: round(r["mean"], 3) for label, r in report.items()}))
    return best
