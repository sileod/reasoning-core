#!/usr/bin/env python3
"""Build no-menu, answer-text eval legs, from tasksource multiple-choice annotations and MATH.

These are *contrast* legs, not preference legs: each item is one prompt plus a small fixed choice set
with exactly one gold, scored by mean token logprob per candidate (or a cross-encoder's logit). The
choices are NOT listed in the prompt, so there is no option-menu to format-match against.

    python scripts/build_contrastive_evals.py --tasks hellaswag siqa garage --output-dir data_cache/v14

Every multiple-choice leg goes through `tasksource.load_task` with each item's native options, so a
leg is one line in LEGS: its tasksource id, its prompt form and, where the data has a known lever,
a filter. Only evaluation splits are used (tasksource_dpo_pairs, the encoders' training data, draws
on train splits). Revisions are PINNED: `revision=None` resolves to whatever snapshot the hub
serves that day, which has already produced one stale-pool incident in this project.

Every build prints the three gates before the file is usable as a leg:
  1 GAMEABLE   -- answer leaked into the prompt; a shortest-answer picker beating chance; and the
                  surface auditor (surface_audit, fitted on procedural-choices, never on the leg)
                  beating chance by 5pt -- a warning, not a failure: it can fire on real knowledge cues
  2 INFORMATIVE-- a base model must score above chance (measured separately, see probe_leg_*)
  3 SENSITIVE  -- must move across aux arms (only measurable after a run)
Gate 1 is checked here because it is a property of the DATA and is cheap; a leg that fails it should
never reach a battery.
"""
from __future__ import annotations
import argparse, json, os, random, re
import numpy as np
from collections import defaultdict
from pathlib import Path

DC = Path(os.environ.get("EVAL_DATA_DIR", "data_cache"))

REVISIONS = {
    "tasksource/jevbench": "5f154ceb30bc8d5f7bda676a00071c4d7f22d35a",
    "tasksource/social_i_qa": "c5e31ad2d8d6b2aec4cf6491653a1fe1640dd647",
    "baber/piqa": "142f6d7367fd9877f0fb3b5734ea6a545f54cdd1",
    "allenai/qasc": "a34ba204eb9a33b919c10cc08f4f1c8dae5ec070",
    "tasksource/reclor": "0414b39bfc39b2d555b48fa245fc198744c46215",
    "allenai/ai2_arc": "210d026faf9955653af8916fad021475a3f00453",
    "Rowan/hellaswag": "218ec52e09a7e7462a5400043bb9a69a41d06b76",
    "allenai/sciq": "2c94ad3e1aafab77146f384e23536f97a4849815",
    "allenai/openbookqa": "388097ea7776314e93a529163e0fea805b8a6454",
    "tau/commonsense_qa": "94630fe30dad47192a8546eb75f094926d47e155",
    "allenai/winogrande": "01e74176c63542e6b0bcb004dcdea22d94fb67b5",
    "tasksource/mmlu": "3631b9bdbf8709d1ec3292625cc839e5b5448018",
    "tasksource/lsat-rc": "f0923a196e509340a94d1954e237ac95c65e6cf8",
    "Samsoup/cosmos_qa": "5511553160809abc4f9c11d12421ec0a9681ee75",
    "textmachinelab/quail": "2bd9d7f90a532fe1a910b70972cef5fda341c8fe",
    "cam-cst/cbt": "72b5c46b1248e3316360f0f2f0b2c39e773b68e4",
    "jeggers/riddle_sense": "42baa6f1630b798a7f9c26b8e0af25ed523f936d",
    "EleutherAI/hendrycks_math": "21a5633873b6a120296cce3e2df9d5550074f4a3",
}


def _load(name, *args, **kw):
    rev = REVISIONS[name]
    from datasets import load_dataset
    try:
        return load_dataset(name, *args, revision=rev, **kw)
    except Exception as e:
        # A wrong pin must NOT quietly become "whatever the hub serves today" -- that is the exact
        # staleness this pinning exists to prevent. Fail, and print the CURRENT sha to paste back in.
        try:
            from huggingface_hub import HfApi
            cur = HfApi().dataset_info(name).sha
        except Exception:
            cur = "<could not resolve>"
        raise SystemExit(f"[build] revision {rev} unusable for {name} ({type(e).__name__}). "
                         f"Current hub sha is {cur} -- update REVISIONS, do not run unpinned.")


def _row(prompt, gold, distractors, rng, answer_cue=True):
    choices = [gold] + [d for d in distractors if d and d != gold]
    if len(choices) < 2:
        return None
    rng.shuffle(choices)
    return {"prompt": prompt.strip() + ("\nAnswer:" if answer_cue else ""), "answer": gold,
            "choices": choices, "answer_idx": choices.index(gold)}


def _items(d, splits):
    """(inputs, options, gold index) per labeled row, deduplicated on (inputs, option set); an item
    seen again with another gold is a conflict and dropped everywhere (MMLU repeats some questions)."""
    unique, conflicts = {}, set()
    for split in splits:
        for r in d.get(split, ()):
            opts = [str(r[k]).strip() for k in sorted(r, key=lambda k: int(k[6:]) if k[6:].isdigit() else -1)
                    if k.startswith("choice") and r[k] is not None]
            label = r["labels"]
            if label is None or not 0 <= int(label) < len(opts) or len(set(opts)) != len(opts) or not all(opts):
                continue
            key, gold = (r["inputs"].strip(), tuple(sorted(opts))), opts[int(label)]
            if key in unique and unique[key][1] != gold:
                conflicts.add(key)
            unique.setdefault(key, (opts, gold))
    return [(k[0], opts, gold) for k, (opts, gold) in unique.items() if k not in conflicts]


def tasksource_rows(task, rng, answer_cue=True, splits=("validation", "test"), **kw):
    """A tasksource multiple-choice task (catalog id, or an eval_only annotation by name), every
    native option kept. Only evaluation splits: nothing here may be in an encoder's training pairs."""
    if task.startswith("eval_only."):
        from tasksource import eval_only
        annotation = getattr(eval_only, task.split(".", 1)[1])
        from datasets import load_dataset
        configs = kw.pop("configs", None) or [annotation.config_name]
        dataset = {}
        for config in configs:
            raw = load_dataset(annotation.dataset_name, config, **{**annotation.load_dataset_kwargs, **kw})
            for split, rows in annotation(raw, gold_first=False, max_options=None).items():
                dataset.setdefault(split, []).extend(rows)
    else:
        from tasksource import load_task
        dataset = load_task(task, native_options=True, **kw)
    items = _items(dataset, splits)
    rng.shuffle(items)
    for prompt, opts, gold in items:
        yield _row(prompt, gold, [o for o in opts if o != gold], rng, answer_cue)


def _winogrande(n, rng):
    """The partial form: the sentence up to the blank is the prompt; each option fills the blank and
    the shared remainder is the candidate, so the options differ only in who fills it."""
    for r in tasksource_rows("winogrande/winogrande_xl", rng, answer_cue=False, revision=REVISIONS["allenai/winogrande"]):
        head, _, tail = r["prompt"].partition("_")
        if r["prompt"].count("_") == 1:
            yield _row(head, f"{r['answer']}{tail}", [f"{c}{tail}" for c in r["choices"] if c != r["answer"]],
                       rng, answer_cue=False)


def _overlap(r):
    """The option sharing the most words with the prompt."""
    words = lambda t: set(re.findall(r"\w+", t.lower()))
    return max(r["choices"], key=lambda c: len(words(c) & words(r["prompt"])))


def _most_frequent(r):
    """The option the prompt repeats most, counting whole words."""
    return max(r["choices"], key=lambda c: len(re.findall(rf"\b{re.escape(c.lower())}\b", r["prompt"].lower())))


def rebalance(rows, picker, rng):
    """Keep the items a lexical picker gets right only at the chance rate: CBT's gold is the word the
    passage repeats most in ~28% of items (chance 10%), GaRAGe's the passage sharing most question words
    in 46% (chance 25%). The other items are all kept."""
    rows = [r for r in rows if r]
    if not rows:
        return iter(())
    hit = [picker(r) == r["answer"] for r in rows]
    f, c = sum(hit) / len(rows), sum(1 / len(r["choices"]) for r in rows) / len(rows)
    keep = min(1.0, c / (1 - c) * (1 - f) / f) if f else 1.0   # share of lever items after subsampling = chance
    return (r for r, h in zip(rows, hit) if not h or rng.random() < keep)


def quail_clean(rows):
    """QuAIL without its two levers: every item offers "not enough information" (gold 11.5%), a
    label prior like FOLIO's neutral, so it is removed and its gold items dropped; and in 6.7% of items
    only the gold is copied verbatim from the passage, a copy detector's shortcut, so those go too."""
    for r in rows:
        p = r["prompt"].lower()
        others = [c for c in r["choices"] if c != r["answer"]]
        if "not enough information" in r["answer"].lower() or (
                r["answer"].lower() in p and not any(c.lower() in p for c in others)):
            continue
        yield _row(r["prompt"][:-len("\nAnswer:")], r["answer"],
                   [c for c in others if "not enough information" not in c.lower()], random.Random(r["prompt"]))


MMLU_MATH = ["abstract_algebra", "college_mathematics", "elementary_mathematics", "high_school_mathematics"]
cbt = lambda rows, rng: rebalance(rows, _most_frequent, rng)
# A retrieval passage that shares the question's words, or is shortest, is gold too often on some
# benchmarks (GaRAGe overlap 46%, FollowIR news21 41%, robust04 shortest 36%; chance 25%).
lexical = lambda rows, rng: rebalance(rebalance(rows, _overlap, rng), lambda r: min(r["choices"], key=len), rng)
# leg: (tasksource id, pinned source repo, keyword args, post-filter). answer_cue=False for continuations.
LEGS = {
    "siqa": ("social_i_qa", "tasksource/social_i_qa", {}, None),
    "piqa": ("piqa", "baber/piqa", {}, None),
    "qasc_closed": ("qasc", "allenai/qasc", {}, None),          # tasksource's QASC is closed-book: no facts
    "reclor": ("reclor", "tasksource/reclor", {}, None),
    "arc_challenge": ("ai2_arc/ARC-Challenge/challenge", "allenai/ai2_arc", {}, None),
    "arc_easy": ("ai2_arc/ARC-Easy/challenge", "allenai/ai2_arc", {}, None),
    "hellaswag": ("hellaswag", "Rowan/hellaswag", dict(answer_cue=False), None),
    "sciq": ("sciq", "allenai/sciq", {}, None),
    "openbookqa": ("openbookqa", "allenai/openbookqa", dict(answer_cue=False), None),
    "commonsenseqa": ("commonsense_qa", "tau/commonsense_qa", {}, None),
    "lsat_rc": ("lsat-rc", "tasksource/lsat-rc", {}, None),
    "cosmos_qa": ("cosmos_qa", "Samsoup/cosmos_qa", {}, None),
    "riddle_sense": ("riddle_sense", "jeggers/riddle_sense", {}, None),
    # Children's Book Test: 20 sentences, then a 21st with one word blanked; the answer names the
    # word after "Answer:", which moved with procedural data in the tasksource survey (2 seeds, 360M
    # base and instruct, OLMo-1B). Candidates fill the blank in place would score 0.9 and barely move.
    "cbt_cn": ("cbt/cn", "cam-cst/cbt", {}, cbt),
    "cbt_ne": ("cbt/ne", "cam-cst/cbt", {}, cbt),
    "quail_clean": ("quail", "textmachinelab/quail", {}, lambda rows, rng: quail_clean(rows)),
    # eval_only.mmlu maps its source validation/dev/test onto train/validation/test: all evaluation.
    "mmlu_math_cloze": ("eval_only.mmlu", "tasksource/mmlu",
                        dict(configs=MMLU_MATH, splits=("train", "validation", "test")), None),
    # Retrieval as multiple choice (encoder legs): passages judged non-answering for the same query.
    # These views pin their own sources; their single split is the benchmark itself.
    "garage": ("eval_only.garage__passage_choice", None, dict(splits=("train",)), lexical),
    **{f"followir_{s}{suffix}": (f"eval_only.followir_{s}__{view}", None, dict(splits=("train",)), lexical)
       for s in ("robust04", "core17", "news21") for suffix, view in (("", "choice"), ("_instr", "instruction_choice"))},
}


def build_leg(leg, n, rng):
    task, repo, kw, post = LEGS[leg]
    rows = tasksource_rows(task, rng, **kw, **({"revision": REVISIONS[repo]} if repo else {}))
    return post(rows, rng) if post else rows


MATH_TYPES = ("algebra", "counting_and_probability", "geometry", "intermediate_algebra", "number_theory",
              "prealgebra", "precalculus")


def _boxed(solution):
    i = solution.rfind("\\boxed{")
    if i < 0:
        return None
    depth, j = 0, i + len("\\boxed{")
    for k in range(j, len(solution)):
        depth += {"{": 1, "}": -1}.get(solution[k], 0)
        if depth < 0:
            return solution[j:k].strip()
    return None


def _math_rows(levels=("Level 1", "Level 2")):
    for t in MATH_TYPES:
        for split in ("test", "train"):
            for r in _load("EleutherAI/hendrycks_math", t, split=split):
                a = _boxed(r["solution"])
                if r["level"] in levels and a:
                    yield r["problem"], a, r["type"], r["level"]


def build_math_l12(n, rng):
    """MATH levels 1-2, answer likelihood (qa_nll, as gsm8k): the final boxed answer after the problem."""
    rows = list(_math_rows())
    rng.shuffle(rows)
    for problem, answer, *_ in rows[:n]:
        yield {"prompt": f"Problem: {problem.strip()}\nAnswer:", "answer": answer}


def build_math_l12_mc(n, rng):
    """MATH levels 1-2 as a no-menu choice: the gold boxed answer against 3 boxed answers of other
    problems of the same type and level, so the contrast needs the problem, not the answer's look."""
    rows = list(_math_rows())
    rng.shuffle(rows)
    pool = defaultdict(list)
    for problem, answer, typ, lvl in rows:
        pool[typ, lvl].append(answer)
    for problem, answer, typ, lvl in rows[:n]:
        others = list(dict.fromkeys(a for a in pool[typ, lvl] if a != answer))
        yield _row(f"Problem: {problem.strip()}", answer, rng.sample(others, min(3, len(others))), rng)


def _jev_option(key, desc):
    """The decider's own option rendering (typed_encoders.formatting.format_option): the description,
    prefixed by its key unless the key is a dummy index (A, option_3, (b))."""
    desc = (desc if isinstance(desc, str) else json.dumps(desc, ensure_ascii=False)).strip() if desc is not None else ""
    key = str(key).strip()
    dummy = key.lower().startswith(("option_", "k_", "choice_", "item_")) or (len(key) == 1 and key.isalpha()) \
        or (key.startswith("(") and key.endswith(")") and len(key) <= 4)
    return key if not desc or desc.lower() == key.lower() else desc if dummy else f"{key}: {desc}"


def _jevbench(n, rng, max_chars=4000, max_options=10):
    """jevbench test (22 natural typed-decision tasks), n rows per task (--n 1100 = 50 each). Prompt = state, blank line, the
    question's instructions -- the decider's (state, question) split. Choice option sets are capped at the gold
    and 9 others seeded by row id (as EXP-0018); yes/no and score questions offer their criteria descriptions."""
    by_task = defaultdict(list)
    for r in _load("tasksource/jevbench", split="test"):
        q, label = json.loads(r["question"]), r["label"]
        crit = q.get("criteria") or {}
        if q["type"] == "choice":
            keys = list(crit)
            if len(keys) > max_options:
                keys = [label] + random.Random(r["id"]).sample([k for k in keys if k != label], max_options - 1)
                keys = [k for k in crit if k in keys]                       # source order
            choices, gold = [_jev_option(k, crit[k]) for k in keys], keys.index(label)
        elif q["type"] == "noul":
            choices = [_jev_option(k, crit.get(k, crit.get(k.title(), k.title()))) for k in ("false", "true")]
            gold = int(label in ("1", "true", "True"))
        else:                                                               # score: ordinal descriptions
            choices, gold = [str(c) for c in crit], int(label)
        state = r["state"] if not r["state"].startswith('"') else json.loads(r["state"])
        prompt = f"{state}\n\n{q['instructions']}"
        if len(prompt) <= max_chars and len(set(choices)) == len(choices):
            by_task[r["task"]].append({"prompt": prompt, "answer": choices[gold], "choices": choices,
                                       "answer_idx": gold, "task": r["task"], "id": r["id"], "type": q["type"]})
    rows = [x for t in sorted(by_task) for x in rng.sample(by_task[t], min(n, len(by_task[t])))]
    rng.shuffle(rows)
    return rows


BUILDERS = {"math_l12": build_math_l12, "math_l12_mc": build_math_l12_mc, "winogrande": _winogrande, "jevbench": lambda n, rng: _jevbench(n // 44, rng),          # called with 2 * --n
            **{leg: (lambda n, rng, leg=leg: build_leg(leg, n, rng)) for leg in LEGS}}


def gate1(rows):
    """GAMEABLE checks on the data alone: answer leaked into the prompt, and shortest-picker excess."""
    # For a binary yes/no leg the substring test is vacuous -- "no" occurs inside ordinary words in
    # any passage -- so it is skipped there and the shortest-picker excess carries gate 1 instead.
    binary = all(set(x.lower() for x in r["choices"]) == {"yes", "no"} for r in rows)
    # Extractive legs (CBT) draw every option from the prompt, so "gold appears in the prompt" is always
    # true and says nothing; the lever there is picking the option the prompt repeats most, reported instead.
    within = lambda r: all(c.lower() in r["prompt"].lower() for c in r["choices"])
    extractive = not binary and sum(map(within, rows)) / len(rows) > 0.9
    leak = 0.0 if binary or extractive else sum(r["answer"].lower() in r["prompt"].lower() for r in rows) / len(rows)
    freq = sum(_most_frequent(r) == r["answer"] for r in rows) / len(rows)
    overlap = sum(_overlap(r) == r["answer"] for r in rows) / len(rows)
    short = sum(min(r["choices"], key=len) == r["answer"] for r in rows) / len(rows)
    chance = sum(1 / len(r["choices"]) for r in rows) / len(rows)
    dlen = (sum(len(r["answer"]) for r in rows) / len(rows)
            - sum(sum(len(c) for c in r["choices"]) / len(r["choices"]) for r in rows) / len(rows))
    return {"leak": leak, "binary": binary, "extractive": extractive, "most_frequent_picker": freq,
            "overlap_picker": overlap, "shortest_picker": short, "chance": chance,
            "shortest_excess_pt": 100 * (short - chance), "gold_len_delta_chars": dlen}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", choices=sorted(BUILDERS), default=sorted(BUILDERS))
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--max-prompt-chars", type=int, default=1400,
                    help="drop items whose prompt is too long for the battery's max_length")
    ap.add_argument("--max-choice-chars", type=int, default=None,
                    help="drop items with a longer option (retrieval passages)")
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--output-dir", type=Path, default=DC,
                    help="Write new legs here; existing files are never overwritten")
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for task in a.tasks:
        out = a.output_dir / f"{task}_eval.jsonl"
        if out.exists():
            raise FileExistsError(out)
    surface = None                                    # fitted on first use: the procedural-choices auditor
    for t in a.tasks:
        rng = random.Random(a.seed)
        rows = [r for r in BUILDERS[t](a.n * 2, rng) if r and len(r["prompt"]) <= a.max_prompt_chars
                and (a.max_choice_chars is None or max(map(len, r.get("choices", [""]))) <= a.max_choice_chars)][:a.n]
        if not rows:
            print(f"[build] {t}: NO rows survived; skipped"); continue
        out = a.output_dir / f"{t}_eval.jsonl"
        with out.open("x") as file:
            file.write("".join(json.dumps(r) + "\n" for r in rows))
        if "choices" not in rows[0]:  # qa_nll leg: no options to game
            print(f"[build] {t:<7} n={len(rows):<5} qa_nll (no choices) -> {out}"); continue
        g = gate1(rows)
        lever = max(g["most_frequent_picker"] if g["extractive"] else 0, g["overlap_picker"]) - g["chance"]
        if surface is None:
            from reasoning_core.evaluation.surface_audit import features, fit_reference, pick
            surface = fit_reference()
        g["surface_picker"] = float(np.mean(pick(surface, [features(r["prompt"], r["choices"]) for r in rows])
                                            == np.array([r["answer_idx"] for r in rows])))
        flag = ("  <-- FAILS GATE 1" if g["leak"] > 0.10 or g["shortest_excess_pt"] > 10 or lever > 0.15 else
                "  <-- surface model" if g["surface_picker"] - g["chance"] > 0.05 else "")
        print(f"[build] {t:<16} n={len(rows):<5} leak={'n/a (binary)' if g['binary'] else 'n/a (extractive)' if g['extractive'] else format(g['leak'],'.1%')} "
              f"shortest={g['shortest_picker']:.1%} surface={g['surface_picker']:.1%} overlap={g['overlap_picker']:.1%} most-frequent={g['most_frequent_picker']:.1%} "
              f"(chance {g['chance']:.1%}) gold_len_delta={g['gold_len_delta_chars']:+.0f}ch -> {out}{flag}")


if __name__ == "__main__":
    main()
