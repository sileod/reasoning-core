"""Build procedural-choices: multiple-choice questions from the procedural pile or reasoning-gym.

Each row keeps a source prompt and its reference answer, plus up to 12 wrong options from
`Task.generate_distractors`: the task's own near misses first, then other answers of the same task and level,
kept only when the task's scorer rejects them and ranked by similarity to the reference. Nothing new is
generated, so the option count varies with how many distinct wrong answers a task has (2 for a yes/no task).
When every word of the reference occurs in the prompt, so must every word of an option: an option naming
things the prompt never mentions is eliminated without solving (prompt overlap picked the reference 93% of
the time on planning before this).

    python scripts/build_procedural_choices.py --out build/procedural_choices                      # reasoning_core
    python scripts/build_procedural_choices.py --out build/procedural_choices --source reasoning_gym
"""
import argparse, collections, json, random, re, signal, sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd
from huggingface_hub import hf_hub_download

# config name -> (repo, pinned revision, train shards, test shard)
SOURCES = {
    "reasoning_core": ("reasoning-core/procedural-pretraining-pile", "61e50209d687e835e97dbb029e5c40d91a0f585e",
                       ["train-00000", "train-00001"], "test-00000"),  # the rc14 tag
    "reasoning_gym": ("reasoning-core/reasoning-gym", "531e2156da7647069fc8c465099a920268ad2df9",
                      ["train-00000-of-00014", "train-00001-of-00014"], "test-00000-of-00001"),
}


class Timeout(Exception):
    pass


def _alarm(*_):
    raise Timeout


def shard(source, name):
    repo, rev, *_ = SOURCES[source]
    return pd.read_parquet(hf_hub_download(repo, f"data/{name}.parquet", repo_type="dataset", revision=rev))


def words(text):
    return set(re.findall(r"\w+", str(text).lower()))


def pick(gold, wrong, prompt, n):
    """The n most gold-like rejected answers, distinct up to case and spacing, grounded in the prompt if gold is."""
    seen, out = {" ".join(str(gold).lower().split())}, []
    grounded = words(gold) <= words(prompt)
    for w in wrong:
        key = " ".join(w.lower().split())
        if key not in seen and (not grounded or words(w) <= words(prompt)):
            seen.add(key); out.append(w)
    return out[:n]


def build_task(args):
    """Rows for one task: (source, name, shuffled rows, quota, distractor range, seed) -> (records, counters).
    Rows are tried in order until the quota is met; the same rows supply the per-level answer reservoirs."""
    source, name, rows, quota, (lo, hi), seed = args
    from reasoning_core.template import Entry
    if source == "reasoning_gym":
        from reasoning_core.integrations.reasoning_gym import Reasoning_Gym
        task = Reasoning_Gym()
    else:
        import reasoning_core
        task = reasoning_core.get_task(name)
    task.generate_example = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("no generation"))
    task._distractor_reservoir_size = 256
    signal.signal(signal.SIGPROF, _alarm)
    rng, out, n = random.Random(seed), [], collections.Counter()
    answers = collections.defaultdict(list)
    for r in rows:
        answers[r["level"]].append(r["answer"])
    for row in rows:
        if n["kept"] >= quota:
            break
        n["rows"] += 1
        task._answer_reservoir = rng.sample(answers[row["level"]], min(160, len(answers[row["level"]])))
        signal.setitimer(signal.ITIMER_PROF, 60)  # CPU seconds: a scorer can loop forever on odd input
        try:
            entry = Entry.from_dict(row)
            if task.score_answer(row["answer"], entry) != 1:
                n["gold_not_1"] += 1; continue
            wrong = pick(row["answer"], task.generate_distractors(entry, n=3 * hi, max_candidates=192), row["prompt"], hi)
            scores = [float(task.score_answer(w, entry)) for w in wrong]
        except Timeout:
            n["timeout"] += 1; continue
        except Exception:
            n["error"] += 1; continue
        finally:
            signal.setitimer(signal.ITIMER_PROF, 0)
        if len(wrong) < lo:
            n["too_few"] += 1; continue
        options = [(row["answer"], 1.0)] + list(zip(wrong, scores))
        rng.shuffle(options)
        out.append(dict(task=name, level=int(row["level"]), prompt=row["prompt"],
                        options=[o for o, _ in options], option_scores=[s for _, s in options],
                        label=[s for _, s in options].index(1.0), answer=row["answer"],
                        id=json.loads(row["metadata"]).get("_deduplication_key", "")))
        n["kept"] += 1
    return name, out, n


def build(source, frame, per_task, span, seed, workers, tasks=None):
    jobs = [(source, name, g.sample(frac=1, random_state=seed + i).to_dict("records"), per_task, span, seed + i)
            for i, (name, g) in enumerate(sorted(frame.groupby("task"))) if not tasks or name in tasks]
    records, stats = [], {}
    with ProcessPoolExecutor(workers) as ex:
        for name, out, n in ex.map(build_task, jobs):
            records += out
            stats[name] = dict(n)
            print(f"{name:32s} {dict(n)}", file=sys.stderr, flush=True)
    return records, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", choices=list(SOURCES), default="reasoning_core")
    ap.add_argument("--n", type=int, default=50_000)
    ap.add_argument("--test-n", type=int, default=5_000)
    ap.add_argument("--min-distractors", type=int, default=1)
    ap.add_argument("--max-distractors", type=int, default=12)
    ap.add_argument("--tasks", nargs="+")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    out = Path(a.out) / a.source; out.mkdir(parents=True, exist_ok=True)
    _, rev, train, test = SOURCES[a.source]
    stats = {}
    for split, n, names in (("train", a.n, train), ("test", a.test_n, [test])):
        if not n:
            continue
        frame = pd.concat([shard(a.source, s) for s in names], ignore_index=True)
        n_tasks = len(a.tasks) if a.tasks else frame.task.nunique()
        records, stats[split] = build(a.source, frame, -(-n // n_tasks), (a.min_distractors, a.max_distractors),
                                      a.seed, a.workers, a.tasks)
        random.Random(a.seed).shuffle(records)
        pd.DataFrame(records[:n]).to_parquet(out / f"{split}.parquet", index=False)
        print(split, len(records[:n]), file=sys.stderr)
    (out / "build_stats.json").write_text(json.dumps(dict(source=SOURCES[a.source][0], revision=rev, seed=a.seed,
                                                          distractors=[a.min_distractors, a.max_distractors],
                                                          stats=stats), indent=1))


if __name__ == "__main__":
    main()
