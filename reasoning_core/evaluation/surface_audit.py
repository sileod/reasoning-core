"""Generic surface auditor for multiple-choice data: can a model that never solves an item, and only sees
surface features of each option, pick the gold above chance?

Features are task-agnostic: option length and word count (relative to the other options), the share of
digits / punctuation / capitals, similarity to the other options (near-miss distractors make the gold
their medoid), position, and word overlap with the prompt. The prompt is split into blocks (blank-line
separated, as a task payload renders: facts, rules, hypothesis...), and overlap is taken per block position
-- first, last, best -- so a hypothesis-only bias shows without naming any field.

The model is pairwise (option a beats option b?), linear or gradient-boosted, and is evaluated
leave-one-group-out (groups = tasks), so what it finds is a shortcut shared across tasks.

    python -m reasoning_core.evaluation.surface_audit procedural_choices.parquet
"""
import re

import numpy as np

FEATURES = ("len_z", "len_rank", "words_z", "overlap", "novel_z", "medoid_z", "digit", "punct", "upper",
            "position", "overlap_first", "overlap_last", "overlap_best_block", "best_block_is_last")
REFERENCE = ("reasoning-core/procedural-choices", "8b19ab6a5b85aab38f7cf8dc13b9ffa35c56aac3")


def _words(text):
    return set(re.findall(r"\w+", text.lower()))


def _trigrams(text):
    text = text.lower()
    return {text[i:i + 3] for i in range(len(text) - 2)} or {text}


def _z(x):
    x = np.asarray(x, float)
    return (x - x.mean()) / x.std() if x.std() > 0 else x * 0


def blocks(prompt):
    return [b for b in re.split(r"\n\s*\n", prompt) if b.strip()] or [prompt]


def features(prompt, options):
    """One row of FEATURES per option."""
    n, words, parts = len(options), [_words(o) for o in options], [_words(b) for b in blocks(prompt)]
    tri = [_trigrams(o) for o in options]
    share = lambda w, p: len(w & p) / max(1, len(w))
    per_block = np.array([[share(w, p) for p in parts] for w in words])     # option x block
    medoid = [np.mean([len(tri[i] & tri[j]) / len(tri[i] | tri[j]) for j in range(n) if j != i]) for i in range(n)]
    length = [len(o) for o in options]
    frac = lambda o, f: sum(map(f, o)) / max(1, len(o))
    allp = set().union(*parts)
    return np.column_stack([
        _z(length), np.argsort(np.argsort(length)) / max(1, n - 1), _z([len(w) for w in words]),
        [share(w, allp) for w in words], _z([len(w - allp) for w in words]), _z(medoid),
        [frac(o, str.isdigit) for o in options], [frac(o, lambda c: not c.isalnum() and not c.isspace()) for o in options],
        [frac(o, str.isupper) for o in options], np.arange(n) / max(1, n - 1),
        per_block[:, 0], per_block[:, -1], per_block.max(1),
        (per_block.argmax(1) == len(parts) - 1).astype(float)])


def _pair(a, b, gbm):
    return np.concatenate([a - b, a, b]) if gbm else a - b


def _pairs(items, gbm):
    X, y = [], []
    for k, (F, gold) in enumerate(items):
        for j in range(len(F)):
            if j != gold:
                first = (k + j) % 2
                X.append(_pair(F[gold], F[j], gbm) if first else _pair(F[j], F[gold], gbm))
                y.append(bool(first))
    return np.array(X), np.array(y)


def fit(items, gbm=True):
    """items = [(features(prompt, options), gold index)]."""
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    X, y = _pairs(items, gbm)
    model = HistGradientBoostingClassifier(max_iter=200, random_state=0) if gbm else LogisticRegression(max_iter=2000, fit_intercept=False)
    return model.fit(X, y), gbm


def pick(fitted, Fs):
    """The option index the model ranks first, per item (Fs = list of feature matrices)."""
    model, gbm = fitted
    if not gbm:
        return np.array([int(np.argmax(F @ model.coef_[0])) for F in Fs])
    X = [_pair(F[i], F[j], gbm) for F in Fs for i in range(len(F)) for j in range(len(F)) if i != j]
    p, out, k = model.predict_proba(np.array(X))[:, 1], [], 0
    for F in Fs:
        n = len(F)
        out.append(int(np.argmax(p[k:k + n * (n - 1)].reshape(n, n - 1).sum(1))))
        k += n * (n - 1)
    return np.array(out)


def leave_group_out(items, groups, gbm=True, folds=10):
    """Per item: does a model fitted on the OTHER groups pick its gold?"""
    from sklearn.model_selection import GroupKFold
    hit = np.zeros(len(items), bool)
    for train, test in GroupKFold(n_splits=min(folds, len(set(groups)))).split(items, groups=groups):
        fitted = fit([items[i] for i in train], gbm)
        hit[test] = pick(fitted, [items[i][0] for i in test]) == np.array([items[i][1] for i in test])
    return hit


def gate(items, groups, seed=0, rounds=2, gbm=True):
    """Adversarial filter (AFLite-style), generic: per group, keep the items a leave-group-out surface model
    gets right only at the chance rate; the rest are all kept. Repeated `rounds` times, refitting on the
    survivors, so a shortcut the first model left behind is caught too. Returns a keep mask."""
    rng, keep = np.random.default_rng(seed), np.ones(len(items), bool)
    groups = np.asarray(groups)
    for _ in range(rounds):
        idx = np.flatnonzero(keep)
        hit = leave_group_out([items[i] for i in idx], groups[idx], gbm)
        for g in set(groups[idx]):
            mine = groups[idx] == g
            f, c = hit[mine].mean(), np.mean([1 / len(items[i][0]) for i in idx[mine]])
            if f > c:
                p = c / (1 - c) * (1 - f) / f          # after subsampling, the model is right at chance
                drop = idx[mine & hit][rng.random(int((mine & hit).sum())) >= p]
                keep[drop] = False
    return keep


def fit_reference(revision=REFERENCE[1], gbm=True):
    """The auditor fitted on all of procedural-choices (reasoning_core train), for scoring other data."""
    import pandas as pd
    from huggingface_hub import hf_hub_download
    d = pd.read_parquet(hf_hub_download(REFERENCE[0], "reasoning_core/train.parquet", repo_type="dataset", revision=revision))
    return fit([(features(p, [str(o) for o in opts]), int(g)) for p, opts, g in zip(d.prompt, d.options, d.label) if len(opts) >= 2], gbm)


def report(hit, groups, chance):
    """Per group: n, accuracy, chance, excess and its z."""
    import pandas as pd
    df = pd.DataFrame(dict(group=groups, hit=hit, chance=chance)).groupby("group").agg(
        n=("hit", "size"), acc=("hit", "mean"), chance=("chance", "mean"))
    df["excess"] = df.acc - df.chance
    df["z"] = df.excess / np.sqrt(df.chance * (1 - df.chance) / df.n)
    return df.sort_values("excess", ascending=False)


if __name__ == "__main__":
    import argparse
    import pandas as pd
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("parquet", help="rows with task, prompt, options, label (procedural-choices layout)")
    ap.add_argument("--linear", action="store_true")
    ap.add_argument("--gate", action="store_true", help="also report what survives the adversarial filter")
    a = ap.parse_args()
    d = pd.read_parquet(a.parquet)
    d = d[d.options.map(len) >= 2]
    items = [(features(p, [str(o) for o in opts]), int(g)) for p, opts, g in zip(d.prompt, d.options, d.label)]
    hit = leave_group_out(items, d.task.values, gbm=not a.linear)
    chance = 1 / d.options.map(len).values
    print(f"{len(items)} items, {d.task.nunique()} tasks | leave-task-out accuracy {hit.mean():.3f} vs chance {chance.mean():.3f}")
    df = report(hit, d.task.values, chance)
    print(f"tasks with excess > 10pt and z > 3: {int(((df.excess > .10) & (df.z > 3)).sum())} of {len(df)}")
    print(df.head(20).round(3).to_string())
    if a.gate:
        keep = gate(items, d.task.values, gbm=not a.linear)
        kept = [items[i] for i in np.flatnonzero(keep)]
        hit = leave_group_out(kept, d.task.values[keep], gbm=not a.linear)
        print(f"after the gate: kept {keep.mean():.1%} | fresh leave-task-out accuracy {hit.mean():.3f} vs chance {chance[keep].mean():.3f}")
