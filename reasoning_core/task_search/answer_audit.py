"""Find generators whose reference answers are wrong: a cheap screen, then two blind solves.

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
from pathlib import Path
import re

from .judge_llm import LLMJudge

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


def suspects(rows, *, per_task=2, below=0.5, judge="jev"):
    """Each task's least plausible examples by `judge`'s p(correct), under `below`."""
    by_task = {}
    for row in rows:
        p = ((row.get("signals") or {}).get(judge) or {}).get("correct")
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
    return found[-1].strip() if found else None


def adjudicate(row, solver, judge="jev"):
    """WRONG when two blind solves agree with each other and not with the reference;
    CORRECT when either matches it; UNSURE otherwise."""
    solves = [solve(solver, row["prompt"]) for _ in range(2)]
    said = [s for s in solves if s is not None]
    right = matcher(row)
    if any(right(s) for s in said):
        verdict = "CORRECT"
    elif len(said) == 2 and normalized(said[0]) == normalized(said[1]):
        verdict = "WRONG"
    else:
        verdict = "UNSURE"
    return {"task": row["task"], "level": row["level"], "index": row["index"],
            "p_correct": row["signals"][judge]["correct"], "reference": row["answer"],
            "solves": solves, "verdict": verdict}


def audit(rows, out, *, per_task=2, below=0.5, workers=4, solver=None, log=print):
    """Adjudicate the suspects not already in `out` (JSONL); return every verdict held."""
    out = Path(out)
    solver = solver or LLMJudge()
    done = ([json.loads(line) for line in out.read_text().splitlines()]
            if out.exists() else [])
    seen = {(v["task"], v["level"], v["index"]) for v in done}
    todo = [row for row in suspects(rows, per_task=per_task, below=below)
            if (row["task"], row["level"], row["index"]) not in seen]
    log(f"{len(todo)} suspects to adjudicate, {len(done)} already judged")
    with ThreadPoolExecutor(workers) as pool, out.open("a") as sink:
        for verdict in pool.map(lambda row: adjudicate(row, solver), todo):
            sink.write(json.dumps(verdict, sort_keys=True) + "\n")
            sink.flush()
            done.append(verdict)
            if verdict["verdict"] == "WRONG":
                log(f"  WRONG {verdict['task']} L{verdict['level']}: reference "
                    f"{verdict['reference']!r}, both solves {verdict['solves'][0]!r}")
    return done
