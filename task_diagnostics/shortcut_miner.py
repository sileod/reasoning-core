#!/usr/bin/env python3
"""Mine simple prompt-only shortcut cues in reasoning-core datasets."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict

import numpy as np
from datasets import load_dataset
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


YESNO = re.compile(r"\b(yes|no|true|false|correct|incorrect)\b", re.I)
WS = re.compile(r"\s+")
NUM = re.compile(r"[-+]?\d+(?:\.\d+)?")
TOK = re.compile(r"(?u)\b[\w./+*<>=-]{2,}\b")


def norm_answer(x: object) -> str:
    s = WS.sub(" ", str(x or "").strip().lower())
    m = YESNO.search(s)
    if m:
        v = m.group(1).lower()
        return "yes" if v in {"yes", "true", "correct"} else "no"
    return s[:80]


def bucket(n: int) -> str:
    for hi in (0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610):
        if n <= hi:
            return f"le{hi}"
    return "gt610"


def metadata_dict(x: object) -> dict:
    if isinstance(x, str):
        try:
            x = json.loads(x)
        except Exception:
            return {}
    return x if isinstance(x, dict) else {}


def answer_shape(x: object) -> str:
    s = WS.sub(" ", str(x or "").strip().lower())
    if YESNO.fullmatch(s):
        return "bool"
    if NUM.fullmatch(s):
        return "number"
    if s.startswith("[") and s.endswith("]"):
        return "list"
    if "\n" in str(x or "") and "," in str(x or ""):
        return "csv"
    return f"text:{bucket(len(s.split()))}"


def target_label(ex: dict, args) -> tuple[str, str]:
    md = metadata_dict(ex.get("metadata"))
    if args.target == "answer":
        return "answer", norm_answer(ex.get("answer"))
    if args.target == "shape":
        return "shape", answer_shape(ex.get("answer"))
    ans = norm_answer(ex.get("answer"))
    if ans in {"yes", "no"}:
        return "answer_bool", ans
    for key in args.target_meta_keys:
        val = md.get(key)
        if isinstance(val, (str, bool, int)) and val is not None:
            return f"meta:{key}", str(val).lower()[:80]
    return "shape", answer_shape(ex.get("answer"))


def cue_text(prompt: str, metadata: object, args) -> str:
    cues = []
    if args.count_cues:
        nums = NUM.findall(prompt)
        cues += [
            f"count:chars:{bucket(len(prompt))}",
            f"count:tokens:{bucket(len(prompt.split()))}",
            f"count:lines:{bucket(prompt.count(chr(10)) + 1)}",
            f"count:numbers:{bucket(len(nums))}",
            f"count:digits:{bucket(sum(c.isdigit() for c in prompt))}",
            f"count:ops:{bucket(sum(prompt.count(c) for c in '+-*/%=<>'))}",
            f"count:brackets:{bucket(sum(prompt.count(c) for c in '()[]{}'))}",
        ]
    md = metadata_dict(metadata)
    for key in args.meta_keys:
        if key not in md:
            continue
        val = md[key]
        if isinstance(val, (int, float, str, bool)) and val is not None:
            val = bucket(int(val)) if isinstance(val, (int, float)) else str(val).lower()[:40]
            cues.append(f"meta:{key}:{val}")
    payload = md.get("payload")
    if args.payload_cues and isinstance(payload, dict):
        for field, text in payload.items():
            cues += [f"payload:{field}:{t.lower()}" for t in TOK.findall(str(text))]
    return prompt + ("\n" + " ".join(cues) if cues else "")


def iter_rows(args):
    ds = load_dataset(args.dataset, split=args.split, streaming=True)
    it = iter(ds)
    counts = Counter()
    modes = {m.strip() for m in args.modes.split(",") if m.strip()}
    if "verif" in modes:
        modes.add("verification")
    try:
        for seen, ex in enumerate(it, 1):
            task, mode = ex.get("task"), ex.get("mode")
            if mode not in modes or not task:
                if seen >= args.scan_limit:
                    break
                continue
            target, label = target_label(ex, args)
            key = (task, mode, target)
            if counts[key] >= args.per_task:
                if seen >= args.scan_limit:
                    break
                continue
            counts[key] += 1
            prompt = cue_text(str(ex.get("prompt") or ""), ex.get("metadata"), args)
            yield key, prompt, label
            if sum(counts.values()) >= args.max_examples or seen >= args.scan_limit:
                break
    finally:
        close = getattr(it, "close", None)
        if close:
            close()


def top_cues(vec, clf, labels, k=8):
    names = np.asarray(vec.get_feature_names_out())
    rows = []
    coef = clf.coef_ if len(labels) > 2 else np.vstack([-clf.coef_[0], clf.coef_[0]])
    for i, label in enumerate(labels):
        idx = np.argsort(coef[i])[-k:][::-1]
        rows.append(f"{label}: " + ", ".join(names[idx]))
    return " | ".join(rows[:3])


def score_group(key, rows, args):
    x, y = zip(*rows)
    labels, freq = zip(*Counter(y).most_common())
    n, n_labels = len(y), len(labels)
    majority = freq[0] / n
    if n < args.min_examples or min(Counter(y).values()) < 2:
        return None, f"too_few_or_singleton n={n} labels={n_labels}"
    if n_labels > args.max_labels:
        return None, f"high_cardinality n={n} labels={n_labels} majority={majority:.2f}"

    strat = y if min(Counter(y).values()) >= 2 else None
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=args.test_size, random_state=args.seed, stratify=strat
    )
    if len(set(y_tr)) < 2 or len(set(y_te)) < 2:
        return None, f"split_single_class n={n} labels={n_labels}"
    vec = CountVectorizer(
        lowercase=True,
        token_pattern=r"(?u)\b[\w:./+*<>=-]{2,}\b",
        ngram_range=(1, args.ngram),
        min_df=min(args.min_df, len(x_tr)),
        max_features=args.max_features,
        binary=True,
    )
    try:
        xtr = vec.fit_transform(x_tr)
    except ValueError as e:
        if "empty vocabulary" in str(e) or "min_df" in str(e):
            return None, f"no_usable_cues n={n} labels={n_labels}"
        raise
    xte = vec.transform(x_te)
    clf = LogisticRegression(
        C=args.c, max_iter=600, class_weight="balanced", random_state=args.seed
    )
    clf.fit(xtr, y_tr)
    pred = clf.predict(xte)
    acc = accuracy_score(y_te, pred)
    lift = acc - majority
    return {
        "task": key[0],
        "mode": key[1],
        "target": key[2],
        "n": n,
        "labels": n_labels,
        "majority": majority,
        "acc": acc,
        "lift": lift,
        "shortcutability": max(0.0, lift) / max(1e-9, 1.0 - majority),
        "cues": top_cues(vec, clf, clf.classes_, args.top_cues),
    }, None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", default="reasoning-core/procedural-pretraining-pile")
    p.add_argument("--split", default="train")
    p.add_argument("--modes", default="instruct,verif")
    p.add_argument("--max-examples", type=int, default=45_000)
    p.add_argument("--scan-limit", type=int, default=200_000)
    p.add_argument("--per-task", type=int, default=1_000)
    p.add_argument("--min-examples", type=int, default=40)
    p.add_argument("--max-labels", type=int, default=20)
    p.add_argument("--test-size", type=float, default=0.35)
    p.add_argument("--ngram", type=int, default=2)
    p.add_argument("--min-df", type=int, default=2)
    p.add_argument("--max-features", type=int, default=4_000)
    p.add_argument("--top-cues", type=int, default=6)
    p.add_argument("--count-cues", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--payload-cues", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--meta-keys", default="_level,difficulty")
    p.add_argument("--target", choices=["auto", "answer", "shape"], default="answer")
    p.add_argument("--target-meta-keys", default="label,is_scalar,solvable,task_type")
    p.add_argument("--c", type=float, default=0.5)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    args.meta_keys = [k.strip() for k in args.meta_keys.split(",") if k.strip()]
    args.target_meta_keys = [k.strip() for k in args.target_meta_keys.split(",") if k.strip()]

    groups = defaultdict(list)
    for key, prompt, answer in iter_rows(args):
        groups[key].append((prompt, answer))

    results, skipped = [], []
    for key, rows in sorted(groups.items()):
        res, why = score_group(key, rows, args)
        (results if res else skipped).append(res or (key, why))

    print("task\tmode\ttarget\tn\tlabels\tmajor\tacc\tlift\tshortcut\tcues")
    for r in sorted(results, key=lambda z: (z["shortcutability"], z["lift"]), reverse=True):
        print(
            f'{r["task"]}\t{r["mode"]}\t{r["target"]}\t{r["n"]}\t{r["labels"]}\t'
            f'{r["majority"]:.2f}\t{r["acc"]:.2f}\t{r["lift"]:+.2f}\t'
            f'{r["shortcutability"]:.2f}\t{r["cues"]}'
        )
    if skipped:
        print("\n# skipped")
        for (task, mode, target), why in skipped:
            print(f"{task}\t{mode}\t{target}\t{why}")


if __name__ == "__main__":
    main()
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)  # Avoid occasional pyarrow/datasets streaming finalizer aborts.
