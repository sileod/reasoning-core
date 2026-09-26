"""Are a task's difficulty levels sound? Three looks at every ladder in the registry.

- config: what `apply_difficulty` does to the fields between the lowest and highest level,
  and whether the level changes the problem at all: the same seed at the bottom and top
  level giving the same prompt is one rung. A generator may read `level` itself -- the
  occurrence count in calendar_recurrence -- so no field moving is not enough to say so.
- generation: `check_headroom` at every level -- the reference scores, generation is quick,
  prompts fit, and the pool is not a handful of instances.
- difficulty: the solve-rate curve read by `diagnose`, measured by a probe where the probe
  has every level, else predicted from Jev (`signal_report.ladder`). A predicted verdict is
  triage: on 82 probed ladders it matched the measured one 38 times (2026-09-26), reliably
  on too-hard and on direction (28/33), and it over-calls flat.

Only the first two touch the generator, and they are stored per task, so the difficulty
verdict can be redone as probes land.
"""
from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
import json
from pathlib import Path

from ..evaluation.difficulty import check_headroom, curve, diagnose
from .signal_report import ladder
from .signals import SAMPLE_SECONDS, write_rows

LEVELS = (0, 2, 4, 6)
SAMPLES = 8
SEEDS = 16   # a probabilistic knob (a share of instances) needs a few draws to show


def moved_fields(task, levels=LEVELS):
    """{field: [value at each level]} for the fields the level changes."""
    values = []
    for level in levels:
        task.config.set_level(level)
        values.append({k: v for k, v in task.config.to_dict().items() if k not in ("level", "seed")})
    task.config.set_level(levels[0])
    return {k: [v[k] for v in values] for k in values[0]
            if any(json.dumps(v[k], default=str) != json.dumps(values[0][k], default=str)
                   for v in values)}


def responds(task, levels=LEVELS, seeds=SEEDS):
    """Whether some seed renders a different prompt at the top level than at the bottom."""
    import random

    def prompt(seed, level):
        random.seed(seed)
        return task.generate_example(level=level, timeout=SAMPLE_SECONDS).prompt

    return any(prompt(seed, levels[0]) != prompt(seed, levels[-1]) for seed in range(seeds))


def inspect(task_name, levels=LEVELS, samples=SAMPLES):
    import reasoning_core

    record = {"task": task_name}
    try:
        task = reasoning_core.get_task(task_name)
        record["fields"] = json.loads(json.dumps(moved_fields(task, levels), default=str))
        record["responds"] = responds(task, levels)
    except Exception as error:  # noqa: BLE001 - a ladder that cannot be climbed is the finding
        return {**record, "error": f"{type(error).__name__}: {error}"[:300]}
    record["generation"] = {}
    for level in levels:
        try:
            record["generation"][str(level)] = check_headroom(task, levels=(level,),
                                                              samples=samples)[0]
        except Exception as error:  # noqa: BLE001 - one bad rung does not hide the others
            record["generation"][str(level)] = {"error": str(error)[:300]}
    return record


def collect(tasks, out, *, levels=LEVELS, samples=SAMPLES, workers=8,
            log=lambda line: print(line, flush=True)):
    """Inspect every task not already in `out` (JSONL); return every record held.

    Tasks run in worker processes, each generator on a main thread for its deadline signal.
    A task's own failure is part of its record; a worker dying breaks the whole pool, so the
    run stops there and the next one resumes. (Recycling workers with max_tasks_per_child
    hung the pool with every worker gone on Python 3.12.)
    """
    out = Path(out)
    records = {r["task"]: r for r in map(json.loads, out.read_text().splitlines())} \
        if out.exists() else {}
    todo = [name for name in tasks if name not in records]
    with ProcessPoolExecutor(workers) as pool:
        running = {pool.submit(inspect, name, levels, samples): name for name in todo}
        try:
            for future in as_completed(running):
                name = running[future]
                records[name] = future.result()
                write_rows(out, records.values())
                log(f"  {name}: {'; '.join(findings(records[name])) or 'ok'}")
        except BrokenProcessPool:
            log(f"  a worker died; rerun to resume the {sum(n not in records for n in todo)} "
                f"tasks left")
            pool.shutdown(cancel_futures=True)
    return list(records.values())


def findings(record, points=None, source="probe"):
    """What is wrong with one task's ladder, as short sentences; empty if nothing is."""
    if "error" in record:
        return [f"ladder: {record['error']}"]
    found = [f"L{level} generation: {m['error'].split(': ', 1)[-1]}"
             for level, m in record["generation"].items() if "error" in m]
    if not record["responds"]:
        found.append("static: the same seed gives the same problem at every level")
    if points and len(points) > 1:
        verdict = diagnose(dict(sorted(points.items())))
        if verdict:
            found.append(f"{source} {verdict[0]}: {verdict[1]}")
    return found


def curves(rows, cache, model, levels=LEVELS):
    """{task: (points, source)}: the probe's curve where it has every level, else Jev's,
    calibrated on the probe's complete curves."""
    measured = {task: points for task, (points, holes) in curve(cache, model).items()
                if not holes and set(levels) <= set(points)}
    predicted, _ = ladder(rows, {(t, level): rate for t, points in measured.items()
                                 for level, rate in points.items()},
                          features=["jev:glance", "log_prompt_chars"])
    by_task = defaultdict(dict)
    for (task, level), rate in predicted.items():
        if level in levels:
            by_task[task][level] = rate
    out = {task: (points, "jev") for task, points in by_task.items()}
    out.update({task: ({l: points[l] for l in levels}, "probe")
                for task, points in measured.items()})
    return out


def report(records, rows=(), cache=None, model="deepseek-v4-flash"):
    ladders = curves(rows, cache, model) if rows and cache else {}
    lines, counts = [], defaultdict(int)
    for record in sorted(records, key=lambda r: r["task"]):
        points, source = ladders.get(record["task"], (None, None))
        found = findings(record, points, source)
        for finding in found:
            counts[finding.split(":")[0]] += 1
        if found:
            lines.append(f"{record['task']}\n" + "".join(f"  {f}\n" for f in found).rstrip())
    summary = "".join(f", {k} {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1]))
    return "\n".join(lines + [f"{len(records)} tasks audited, {len(lines)} with findings{summary}"])
