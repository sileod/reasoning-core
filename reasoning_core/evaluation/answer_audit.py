"""Find generators whose reference answers are wrong: a cheap screen, then two blind solves.

The screen is Jev twice. `correct` (from `signals`) asks yes or no about the reference;
`choice` asks it to pick the reference out from wrong answers the task's own scorer rejects
(`Task.generate_distractors`). On 494 claims, half with a sibling's wrong answer swapped in,
their AUROCs were 0.866 and 0.909 and their product's 0.916 (2026-09-26), so suspects are
ranked by the product.

A generator can be wrong in a way no gate sees -- self-consistent, reproducible, and wrong
on the instances a sample file happens not to show. Recomputing every answer with a
reasoning model is too slow to run across the registry; Jev's p(correct) costs a fraction
of a cent and ranks a right reference answer above a sibling's wrong one with AUROC 0.87
(2026-09-26, 83 pairs). It cannot do arithmetic, so it only chooses what gets recomputed.

The recomputation never sees the reference. Shown it, a reviewer argues with it, and a
second reader shown the first one's sentence agrees: that version confirmed 9 of 21
suspects, and of three checked by hand one was a real bug (congruence_system answering
1001034 for x = 42 mod 96, 10 mod 32) and two were the reviewer's own arithmetic. Two
independent solves that reach the same answer, different from the reference, are much
harder to produce by accident.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import random
import re

from .judge import Question
from .judge_jev import JevJudge
from .judge_llm import LLMJudge
from .signals import MAX_STATE_CHARS, write_rows

SOLVE = """Solve the problem. Work it out step by step, following only the rules the
problem states. Then give your final answer on the last line, in exactly the form the
problem asks for, as:
FINAL: <answer>"""
# A reasoner spends most of its budget thinking; recomputing a Borda count over eleven
# candidates does not fit in the gates' 512.
SOLVE_TOKENS = 8192
SOLVE_TEMPERATURE = 0.7   # two draws, so two samples rather than one answer read twice


def normalized(answer):
    return re.sub(r"[\s.]+$", "", re.sub(r"\s+", " ", str(answer).strip().lower()))


def compact(answer):
    """The answer with spacing, markup and grouping stripped: equal compact forms differ
    only in how they are written."""
    return re.sub(r"[\s`*{}\[\]()]", "", str(answer)).lower()


def matcher(row):
    """answer -> bool. The task's own scorer when the stored example still earns its reference
    a full score (so `8, 17` matches `8,17` the way the task means it), else text equality."""
    reference = normalized(row["answer"])
    try:
        import reasoning_core
        from reasoning_core.template import Entry

        task = reasoning_core.get_task(row["task"])
        entry = Entry.from_dict(row)
        if row.get("metadata") and task.score_answer(row["answer"], entry) == 1:
            return lambda said: _score(task, said, entry) == 1
    except Exception:  # noqa: BLE001 - a task that cannot score falls back to text
        pass
    return lambda said: normalized(said) == reference


def _score(task, said, entry):
    try:
        return task.score_answer(said, entry)
    except Exception:  # noqa: BLE001 - a scorer crashing on a stranger's answer is a miss
        return 0


DISTRACTORS = 3
LABELS = "ABCD"


def choose(row, distractors, judge):
    """Jev's probability on the reference among it and `distractors`, in a fixed shuffle."""
    options = [str(row["answer"])] + distractors[:DISTRACTORS]
    random.Random(row["prompt"]).shuffle(options)
    labels = tuple(LABELS[:len(options)])
    state = (f"PROBLEM:\n{row['prompt']}\n\nCANDIDATE ANSWERS:\n"
             + "\n".join(f"{label}) {option}" for label, option in zip(labels, options)))
    question = Question("pick", "Which candidate answer is the correct answer to the PROBLEM?",
                        labels)
    probs = judge.evaluate(state[:MAX_STATE_CHARS], [question])["pick"]["probs"]
    return None if probs is None else probs[labels[options.index(str(row["answer"]))]]


def add_choice(rows, path, *, workers=8, log=lambda line: print(line, flush=True)):
    """Fill `jev:choice` on every row lacking it, and save. Distractors are drawn on the main
    thread, since a generator's deadline is a signal; only the judge calls are pooled."""
    import reasoning_core
    from reasoning_core.template import Entry

    judge, tasks, pending = JevJudge(), {}, []
    with ThreadPoolExecutor(workers) as pool:
        for row in rows:
            jev = (row.get("signals") or {}).get("jev") or {}
            if "prompt" not in row or "choice" in jev or not row.get("metadata"):
                continue
            try:
                task = tasks.get(row["task"]) or tasks.setdefault(
                    row["task"], reasoning_core.get_task(row["task"]))
                distractors = task.generate_distractors(Entry.from_dict(row), n=DISTRACTORS,
                                                        max_candidates=16)
            except Exception:  # noqa: BLE001 - no distractors, no choice question
                continue
            if distractors:
                pending.append((jev, pool.submit(choose, row, distractors, judge)))
        for jev, future in pending:
            if future.result() is not None:
                jev["choice"] = future.result()
    write_rows(Path(path), rows)
    log(f"choice asked of {len(pending)} examples")


def plausibility(row, judge="jev"):
    """p(correct) times p(choice) where both exist, else whichever does."""
    values = [v for k, v in ((row.get("signals") or {}).get(judge) or {}).items()
              if k in ("correct", "choice") and v is not None]
    return None if not values else float(math.prod(values))


def suspects(rows, *, per_task=2, below=0.5, judge="jev"):
    """Each task's least plausible examples, under `below`."""
    by_task = {}
    for row in rows:
        p = plausibility(row, judge)
        if "prompt" in row and p is not None and p < below:
            by_task.setdefault(row["task"], []).append((p, row))
    return [row for scored in by_task.values()
            for _, row in sorted(scored, key=lambda pair: pair[0])[:per_task]]


def solve(solver, prompt):
    try:
        text = solver.complete(SOLVE, prompt, max_tokens=SOLVE_TOKENS,
                               temperature=SOLVE_TEMPERATURE) or ""
    except Exception:  # noqa: BLE001 - an unreachable solver is a missing vote
        return None
    found = re.findall(r"FINAL:\s*(.+)", text)
    return found[-1].strip().strip("*`").strip() if found else None


def decide(row, solves):
    """CORRECT when a solve earns the reference's score; STRICT when both solves agree and
    differ from the reference only in formatting the task's scorer refuses; WRONG when they
    agree on something else; UNSURE otherwise."""
    said = [s for s in solves if s is not None]
    right = matcher(row)
    if any(right(s) for s in said):
        return "CORRECT"
    if len(said) == 2 and normalized(said[0]) == normalized(said[1]):
        return "STRICT" if compact(said[0]) == compact(row["answer"]) else "WRONG"
    return "UNSURE"


def adjudicate(row, solver, judge="jev"):
    solves = [solve(solver, row["prompt"]) for _ in range(2)]
    return {"task": row["task"], "level": row["level"], "index": row["index"],
            "plausibility": plausibility(row, judge), "reference": row["answer"],
            "solves": solves, "verdict": decide(row, solves)}


def audit(rows, out, *, per_task=2, below=0.5, workers=4, solver=None,
          log=lambda line: print(line, flush=True)):
    """Adjudicate the suspects not already in `out` (JSONL); return every verdict held."""
    out = Path(out)
    solver = solver or LLMJudge()
    done = ([json.loads(line) for line in out.read_text().splitlines()]
            if out.exists() else [])
    by_key = {(row["task"], row["level"], row.get("index")): row for row in rows}
    for verdict in done:   # verdicts follow the current rule; the solves are what is kept
        row = by_key.get((verdict["task"], verdict["level"], verdict["index"]))
        if row:
            verdict["verdict"] = decide(row, [str(s).strip("*`").strip() if s else s
                                              for s in verdict["solves"]])
    seen = {(v["task"], v["level"], v["index"]) for v in done}
    todo = [row for row in suspects(rows, per_task=per_task, below=below)
            if (row["task"], row["level"], row["index"]) not in seen]
    log(f"{len(todo)} suspects to adjudicate, {len(done)} already judged")
    write_rows(out, done)
    with ThreadPoolExecutor(workers) as pool, out.open("a") as sink:
        for verdict in pool.map(lambda row: adjudicate(row, solver), todo):
            sink.write(json.dumps(verdict, sort_keys=True) + "\n")
            sink.flush()
            done.append(verdict)
            if verdict["verdict"] == "WRONG":
                log(f"  WRONG {verdict['task']} L{verdict['level']}: reference "
                    f"{verdict['reference']!r}, both solves {verdict['solves'][0]!r}")
    return done
