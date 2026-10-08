"""Is a new decision judge good enough to replace or join the default? One fixed benchmark, any judge.

Every judge answers the SAME stored examples (rows written by `signals.collect`), so judges are
compared on identical states. Answers are cached in OUT/answers.jsonl under a hash of the state and
questions, so a rerun, a new judge or a changed item asks only what is missing. Ground truths:

  sibling   AUROC of p(correct): the true reference vs another example's reference from the same task
            and, where one exists, the same level (same format and size, wrong content). Overall and
            averaged within task: a judge that only learned "this task's references look wrong" is
            0.5 within task. Cross-level siblings are easier (a level-6 answer is bigger), so they
            are only a fallback.
  near      the same AUROC against a near miss: the task's own `generate_distractors`, a wrong
            answer the task's scorer rejects but built to look right. The generator bugs an answer
            audit hunts look like this, not like a sibling.
  pick      accuracy choosing the reference among it and 3 sibling answers (chance 0.25).
  ladder    held-out fit of measured solve rates (zero-shot probe cache) from the judge's
            `glance` + prompt length: cell rho, within-task rho, ladder direction.
  retest    the judge asked twice: per-dimension Spearman (deciders are deterministic: 1.0).
  agree     per-dimension Spearman with every other judge.
  cost, latency, abstentions.

    python -m reasoning_core.evaluation.judge_bench --rows a.jsonl b.jsonl --judges jev,pplx --out DIR
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np

from .answer_audit import LABELS, matcher
from .difficulty import curve
from .judge import Question, make_judge
from .signal_report import ladder, spearman
from .signals import DIMENSIONS, MAX_STATE_CHARS, state_of


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None]).sum() + 0.5 * (pos[:, None] == neg[None]).sum())
                 / (len(pos) * len(neg)))


def key(state, questions):
    spec = "|".join(f"{q.name}:{','.join(q.choices)}" for q in questions)
    return hashlib.sha1((state + "\x00" + spec).encode()).hexdigest()[:16]


def load(paths, per_task, seed):
    """Up to `per_task` stored examples per task, spread over levels, reproducibly."""
    by_task = defaultdict(list)
    for path in paths:
        for line in Path(path).read_text().splitlines():
            row = json.loads(line)
            if "prompt" in row and row.get("answer") not in (None, ""):
                by_task[row["task"]].append(row)
    rng, rows = random.Random(seed), []
    for task in sorted(by_task):
        rng.shuffle(by_task[task])
        rows += sorted(by_task[task][:per_task], key=lambda r: r["level"])
    return rows, by_task


def _near_miss(row):
    """One wrong answer the task's own scorer rejects, or None (rg tasks, generators without one)."""
    try:
        import reasoning_core
        from reasoning_core.template import Entry
        found = reasoning_core.get_task(row["task"]).generate_distractors(
            Entry.from_dict(row), n=1, max_candidates=16)
    except Exception:  # noqa: BLE001 - no distractor, no near-miss item
        return None
    return str(found[0]) if found else None


def items(rows, by_task, seed, near=True):
    """The benchmark: one dict per question put to a judge, keyed by row and kind."""
    profile_qs = tuple(d.question_() for d in DIMENSIONS)
    correct_q = (next(d for d in DIMENSIONS if d.name == "correct").question_(),)
    rng, out = random.Random(seed), []

    def add(rid, kind, state, qs, truth=None):
        out.append({"rid": rid, "kind": kind, "state": state, "qs": qs, "truth": truth, "key": key(state, qs)})

    for i, row in enumerate(rows):
        rid = f"{row['task']}|{row['level']}|{i}"
        add(rid, "profile", state_of(row), profile_qs)
        add(rid, "true", state_of(row), correct_q, 1)
        same = matcher(row)
        siblings = [r for r in by_task[row["task"]] if str(r["answer"]) != str(row["answer"])]
        rng.shuffle(siblings)
        siblings.sort(key=lambda r: r["level"] != row["level"])   # same level first, stable
        wrong = [w for w in dict.fromkeys(str(r["answer"]) for r in siblings[:24]) if not same(w)][:3]
        if wrong:
            add(rid, "sibling", state_of({**row, "answer": wrong[0]}), correct_q, 0)
            options = [str(row["answer"])] + wrong
            random.Random(rid).shuffle(options)
            labels = tuple(LABELS[:len(options)])
            state = (f"PROBLEM:\n{row['prompt']}\n\nCANDIDATE ANSWERS:\n"
                     + "\n".join(f"{l}) {o}" for l, o in zip(labels, options)))[:MAX_STATE_CHARS]
            pick = Question("pick", "Which candidate answer is the correct answer to the PROBLEM?", labels)
            add(rid, "pick", state, (pick,), labels[options.index(str(row["answer"]))])
        miss = _near_miss(row) if near else None
        if miss and not same(miss):
            add(rid, "near", state_of({**row, "answer": miss}), correct_q, 0)
    return out


def ask(judges, bench, cache_path, retest, workers):
    """Fill the answer cache: every (judge, item), plus a second pass over the first `retest` profiles."""
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            r = json.loads(line)
            cache[(r["judge"], r["key"])] = r
    again = [dict(b, key=b["key"] + "|again") for b in [b for b in bench if b["kind"] == "profile"][:retest]]
    todo = list({(name, b["key"]): (name, b) for name in judges for b in bench + again
                 if (name, b["key"]) not in cache}.values())

    def one(job):
        name, b = job
        start = time.time()
        reply = judges[name].evaluate(b["state"], list(b["qs"]))
        return {"judge": name, "key": b["key"], "id": f"{b['rid']}|{b['kind']}",
                "seconds": round(time.time() - start, 3),
                "probs": {q: (reply[q] or {}).get("probs") for q in reply},
                "abstain": [q for q in reply if not (reply[q] or {}).get("probs")]}

    with ThreadPoolExecutor(workers) as pool, cache_path.open("a") as out:
        for k, r in enumerate(pool.map(one, todo)):
            cache[(r["judge"], r["key"])] = r
            out.write(json.dumps(r) + "\n")
            if k % 500 == 0:
                print(f"[judge_bench] {k}/{len(todo)} asked", flush=True)
    return cache


def report(judges, rows, bench, cache, probe, probe_model, retest):
    dims = {d.name: d for d in DIMENSIONS}
    by = {(b["rid"], b["kind"]): b for b in bench}
    profiles = [b for b in bench if b["kind"] == "profile"]
    out = {}
    for j in judges:
        got = lambda b, suffix="": cache.get((j, b["key"] + suffix)) if b else None
        value = lambda r, name: dims[name].value(((r or {}).get("probs") or {}).get(name))
        res = {}
        for kind in ("sibling", "near"):
            pos, neg, task_of = [], [], []
            for b in bench:
                if b["kind"] == kind:
                    t, f = value(got(by.get((b["rid"], "true"))), "correct"), value(got(b), "correct")
                    if t is not None and f is not None:
                        pos.append(t), neg.append(f), task_of.append(b["rid"].split("|")[0])
            within = defaultdict(lambda: ([], []))
            for t, f, task in zip(pos, neg, task_of):
                within[task][0].append(t), within[task][1].append(f)
            per = [auroc(*v) for v in within.values() if len(v[0]) >= 3]
            res[kind] = {"auroc": auroc(pos, neg), "within_task": float(np.nanmean(per)) if per else None,
                         "n": len(pos)}
        hit = [max(p, key=p.get) == b["truth"] for b in bench if b["kind"] == "pick"
               for p in [((got(b) or {}).get("probs") or {}).get("pick")] if p]
        res["pick"] = {"acc": sum(hit) / len(hit) if hit else None, "n": len(hit)}
        twice = [(got(b), got(b, "|again")) for b in profiles[:retest]]
        res["retest_rho"] = {n: _rho([value(a, n) for a, b in twice if b], [value(b, n) for a, b in twice if b])
                             for n in dims}
        if probe:
            stored = [{**row, "signals": {j: {n: value(got(b), n) for n in dims}}} for row, b in zip(rows, profiles)]
            measured = {(t, lvl): rate for t, (points, holes) in curve(probe, probe_model).items()
                        if not holes for lvl, rate in points.items()}
            try:
                res["ladder"] = ladder(stored, measured, judge=j, features=[f"{j}:glance", "log_prompt_chars"])[1]
            except Exception as error:  # noqa: BLE001 - too few measured cells
                res["ladder"] = f"n/a: {error}"
        answered = [r for (jj, _), r in cache.items() if jj == j]
        res["seconds_median"] = float(np.median([r["seconds"] for r in answered])) if answered else None
        res["abstain_rate"] = sum(bool(r["abstain"]) for r in answered) / max(len(answered), 1)
        res["calls"] = len(answered)
        out[j] = res
    value = lambda r, name: dims[name].value(((r or {}).get("probs") or {}).get(name))
    out["agree"] = {f"{a}~{b}": {n: _rho([value(cache.get((a, p["key"])), n) for p in profiles],
                                         [value(cache.get((b, p["key"])), n) for p in profiles]) for n in dims}
                    for k, a in enumerate(judges) for b in list(judges)[k + 1:]}
    return out


def _rho(x, y):
    keep = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(keep) < 5:
        return None
    r = spearman(np.array([a for a, _ in keep]), np.array([b for _, b in keep]))
    return None if r != r else round(float(r), 3)


def text(res, judges):
    f = lambda v: "  -  " if v is None or v != v else f"{v:.3f}"
    lines = ["judge   sibling within | near  within (n) | pick  | ladder cell/within/dir | s/call abstain"]
    for j in judges:
        r, lad = res[j], res[j].get("ladder")
        lad = (f"{lad['cell_rho']:+.2f}/{lad['within_task_rho']:+.2f}/{lad['direction']}"
               if isinstance(lad, dict) and lad.get("cell_rho") is not None else str(lad)[:22])
        lines.append(f"{j:<7} {f(r['sibling']['auroc'])}  {f(r['sibling']['within_task'])} | "
                     f"{f(r['near']['auroc'])} {f(r['near']['within_task'])} ({r['near']['n']}) | "
                     f"{f(r['pick']['acc'])} | {lad:<22} | {r['seconds_median']:.2f}   {r['abstain_rate']:.3f}")
    for pair, rhos in res["agree"].items():
        lines.append(f"agree {pair}: " + ", ".join(f"{n} {v:+.2f}" for n, v in rhos.items() if v is not None))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rows", nargs="+", required=True, help="signals.collect JSONL files")
    p.add_argument("--judges", default="jev,pplx")
    p.add_argument("--out", required=True)
    p.add_argument("--per-task", type=int, default=8)
    p.add_argument("--retest", type=int, default=50, help="profiles asked twice")
    p.add_argument("--no-near", action="store_true", help="skip near-miss items (no generator calls)")
    p.add_argument("--probe", default="reasoning_core/reports/build/zeroshot.json")
    p.add_argument("--probe-model", default="deepseek-v4-flash")
    p.add_argument("--workers", type=int, default=16)
    p.add_argument("--seed", type=int, default=0)
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = a.judges.split(",")
    judges = {n: make_judge(n) for n in names}
    rows, by_task = load(a.rows, a.per_task, a.seed)
    bench = items(rows, by_task, a.seed, near=not a.no_near)
    kinds = {k: sum(b["kind"] == k for b in bench) for k in ("profile", "sibling", "near", "pick")}
    print(f"[judge_bench] {len(rows)} rows from {len(by_task)} tasks -> {kinds}", flush=True)
    cache = ask(judges, bench, out / "answers.jsonl", a.retest, a.workers)
    probe = json.loads(Path(a.probe).read_text()) if a.probe and Path(a.probe).exists() else None
    res = report(names, rows, bench, cache, probe, a.probe_model, a.retest)
    (out / "report.json").write_text(json.dumps(res, indent=1))
    (out / "report.txt").write_text(text(res, names) + "\n")
    print(text(res, names))


if __name__ == "__main__":
    main()
