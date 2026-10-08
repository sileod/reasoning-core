"""Is a new decision judge good enough to replace or join Jev? One fixed benchmark, any judge.

Every judge answers the SAME stored examples (rows written by `signals.collect`), so judges are
compared on identical states; answers are cached in OUT/answers.jsonl and a rerun or a new
judge only asks what is missing. What is measured, and why each is ground truth:

  correct   AUROC of p(correct) for the true reference vs a sibling's answer the matcher rejects
            (same task: same format, wrong content), overall and averaged within task -- a judge
            that only learned "this task's references look wrong" scores 0.5 within task.
  pick      accuracy choosing the reference among it and 3 sibling answers (chance 0.25).
  ladder    held-out fit of measured solve rates (zero-shot probe cache) from the judge's
            `glance` + prompt length: cell rho, within-task rho, ladder direction.
  retest    the judge asked twice: per-dimension Spearman, the ceiling on any of its signals.
  agree     per-dimension Spearman with every other judge.
  cost, latency, abstentions.

    python -m reasoning_core.evaluation.judge_bench --rows a.jsonl b.jsonl --judges jev,kev,pplx --out DIR
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import random
import time

import numpy as np

from .answer_audit import LABELS, matcher
from .judge import Question, make_judge
from .signal_report import ladder, spearman
from .signals import DIMENSIONS, MAX_STATE_CHARS, state_of
from .difficulty import curve


def auroc(pos, neg):
    pos, neg = np.asarray(pos, float), np.asarray(neg, float)
    if not len(pos) or not len(neg):
        return float("nan")
    return float(((pos[:, None] > neg[None]).sum() + 0.5 * (pos[:, None] == neg[None]).sum())
                 / (len(pos) * len(neg)))


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


def items(rows, by_task, seed):
    """The benchmark: (id, kind, state, questions, truth) for every probe of every row."""
    profile_qs = tuple(d.question_() for d in DIMENSIONS)
    correct_q = next(d for d in DIMENSIONS if d.name == "correct").question_()
    rng, out = random.Random(seed), []
    for i, row in enumerate(rows):
        rid = f"{row['task']}|{row['level']}|{i}"
        out.append((rid + "|profile", "profile", state_of(row), profile_qs, None))
        same = matcher(row)
        wrong = list(dict.fromkeys(str(r["answer"]) for r in by_task[row["task"]]
                                   if str(r["answer"]) != str(row["answer"])))
        rng.shuffle(wrong)
        wrong = [w for w in wrong[:12] if not same(w)][:3]
        if not wrong:
            continue
        out.append((rid + "|true", "correct", state_of(row), (correct_q,), 1))
        out.append((rid + "|false", "correct", state_of({**row, "answer": wrong[0]}), (correct_q,), 0))
        options = [str(row["answer"])] + wrong
        random.Random(rid).shuffle(options)
        labels = tuple(LABELS[:len(options)])
        state = (f"PROBLEM:\n{row['prompt']}\n\nCANDIDATE ANSWERS:\n"
                 + "\n".join(f"{l}) {o}" for l, o in zip(labels, options)))[:MAX_STATE_CHARS]
        pick = Question("pick", "Which candidate answer is the correct answer to the PROBLEM?", labels)
        out.append((rid + "|pick", "pick", state, (pick,), labels[options.index(str(row["answer"]))]))
    return out


def ask(judges, bench, cache_path, retest, workers):
    """Fill the answer cache: every (judge, item), plus a second pass over `retest` profiles."""
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            r = json.loads(line)
            cache[(r["judge"], r["id"])] = r
    todo = [(name, iid + suffix, state, qs) for name in judges for iid, kind, state, qs, _ in bench
            for suffix in ("",) + (("|again",) if kind == "profile" and int(iid.split("|")[2]) < retest
                                   else ()) if (name, iid + suffix) not in cache]

    def one(job):
        name, iid, state, qs = job
        start = time.time()
        reply = judges[name].evaluate(state, list(qs))
        return {"judge": name, "id": iid, "seconds": round(time.time() - start, 3),
                "probs": {q: (reply[q] or {}).get("probs") for q in reply},
                "abstain": [q for q in reply if not (reply[q] or {}).get("probs")]}

    with ThreadPoolExecutor(workers) as pool, cache_path.open("a") as out:
        for k, r in enumerate(pool.map(one, todo)):
            cache[(r["judge"], r["id"])] = r
            out.write(json.dumps(r) + "\n")
            if k % 200 == 0:
                print(f"[judge_bench] {k}/{len(todo)} asked", flush=True)
    return cache


def report(judges, rows, bench, cache, probe, probe_model):
    dims = {d.name: d for d in DIMENSIONS}
    value = lambda r, name: dims[name].value((r or {}).get("probs", {}).get(name))
    out = {}
    for j in judges:
        res = {}
        pos, neg, task_of = [], [], []
        for iid, kind, *_ , truth in bench:
            if kind == "correct" and truth == 0:
                t = value(cache.get((j, iid.rsplit("|", 1)[0] + "|true")), "correct")
                f = value(cache.get((j, iid)), "correct")
                if t is not None and f is not None:
                    pos.append(t), neg.append(f), task_of.append(iid.split("|")[0])
        res["correct_auroc"] = auroc(pos, neg)
        within = defaultdict(lambda: ([], []))
        for t, f, task in zip(pos, neg, task_of):
            within[task][0].append(t), within[task][1].append(f)
        per = [auroc(*v) for v in within.values() if len(v[0]) >= 3]
        res["correct_auroc_within_task"] = float(np.nanmean(per)) if per else None
        picks = [(cache.get((j, iid)) or {}).get("probs", {}).get("pick") for iid, kind, *_ in bench if kind == "pick"]
        truths = [truth for iid, kind, *_, truth in bench if kind == "pick"]
        hit = [max(p, key=p.get) == t for p, t in zip(picks, truths) if p]
        res["pick_acc"] = sum(hit) / len(hit) if hit else None
        res["pick_n"] = len(hit)
        prof = [(iid, cache.get((j, iid)), cache.get((j, iid + "|again")))
                for iid, kind, *_ in bench if kind == "profile"]
        res["retest_rho"] = {n: _rho([value(a, n) for _, a, b in prof if b], [value(b, n) for _, a, b in prof if b])
                             for n in dims}
        if probe:
            stored = [{**row, "signals": {j: {n: value(cache.get((j, iid)), n) for n in dims}}}
                      for row, (iid, *_rest) in zip(rows, [b for b in bench if b[1] == "profile"])]
            measured = {(t, lvl): rate for t, (points, holes) in curve(probe, probe_model).items()
                        if not holes for lvl, rate in points.items()}
            try:
                _, stats = ladder(stored, measured, judge=j, features=[f"{j}:glance", "log_prompt_chars"])
                res["ladder"] = stats
            except Exception as error:  # noqa: BLE001 - too few measured cells
                res["ladder"] = f"n/a: {error}"
        answered = [r for (jj, _), r in cache.items() if jj == j]
        res["seconds_median"] = float(np.median([r["seconds"] for r in answered])) if answered else None
        res["abstain_rate"] = sum(bool(r["abstain"]) for r in answered) / max(len(answered), 1)
        res["calls"] = len(answered)
        out[j] = res
    profiles = [iid for iid, kind, *_ in bench if kind == "profile"]
    out["agree"] = {f"{a}~{b}": {n: _rho([value(cache.get((a, i)), n) for i in profiles],
                                         [value(cache.get((b, i)), n) for i in profiles]) for n in dims}
                    for k, a in enumerate(judges) for b in list(judges)[k + 1:]}
    return out


def _rho(x, y):
    keep = [(a, b) for a, b in zip(x, y) if a is not None and b is not None]
    if len(keep) < 5:
        return None
    r = spearman(np.array([a for a, _ in keep]), np.array([b for _, b in keep]))
    return None if r != r else round(float(r), 3)


def text(res, judges):
    lines = ["judge      correct  within  pick   ladder(cell/within/dir)  retest(glance/correct)  s/call  abstain  calls"]
    for j in judges:
        r = res[j]
        lad = r.get("ladder")
        lad = (f"{lad['cell_rho']:+.2f}/{lad['within_task_rho']:+.2f}/{lad['direction']}"
               if isinstance(lad, dict) and lad.get("cell_rho") is not None else str(lad)[:22])
        rt = r["retest_rho"]
        lines.append(f"{j:<10} {r['correct_auroc']:.3f}   {r['correct_auroc_within_task'] or float('nan'):.3f}   "
                     f"{r['pick_acc'] or float('nan'):.3f}  {lad:<24} {rt['glance']}/{rt['correct']:<16} "
                     f"{r['seconds_median']:.2f}    {r['abstain_rate']:.3f}    {r['calls']}")
    for pair, rhos in res["agree"].items():
        lines.append(f"agree {pair}: " + ", ".join(f"{n} {v:+.2f}" for n, v in rhos.items() if v is not None))
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--rows", nargs="+", required=True, help="signals.collect JSONL files")
    p.add_argument("--judges", default="jev,pplx")
    p.add_argument("--out", required=True)
    p.add_argument("--per-task", type=int, default=8)
    p.add_argument("--retest", type=int, default=150, help="profiles asked twice")
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
    bench = items(rows, by_task, a.seed)
    print(f"[judge_bench] {len(rows)} rows from {len(by_task)} tasks -> {len(bench)} items", flush=True)
    cache = ask(judges, bench, out / "answers.jsonl", a.retest, a.workers)
    probe = json.loads(Path(a.probe).read_text()) if a.probe and Path(a.probe).exists() else None
    res = report(names, rows, bench, cache, probe, a.probe_model)
    (out / "report.json").write_text(json.dumps(res, indent=1))
    (out / "report.txt").write_text(text(res, names) + "\n")
    print(text(res, names))


if __name__ == "__main__":
    main()
