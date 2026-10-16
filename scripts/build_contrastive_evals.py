#!/usr/bin/env python3
"""Build no-menu, answer-text eval legs from pinned public NLU datasets and MMLU.

These are *contrast* legs, not preference legs: each item is one prompt plus a small fixed choice set
with exactly one gold, scored by mean token logprob per candidate. That makes them directly comparable
to arc_easy / balanced_copa, and it is the shape that survived the leak critique -- the choices are
NOT listed in the prompt, so there is no option-menu to format-match against.

    python scripts/build_contrastive_evals.py --tasks boolq siqa wic piqa reclor

Revisions are PINNED. `load_dataset(..., revision=None)` silently resolves to whatever snapshot the
hub serves that day, which has already produced one stale-pool incident in this project.

Every build prints the three gates before the file is usable as a leg:
  1 GAMEABLE   -- answer leaked into the prompt; a shortest-answer picker beating chance
  2 INFORMATIVE-- a base model must score above chance (measured separately, see probe_leg_*)
  3 SENSITIVE  -- must move across aux arms (only measurable after a run)
Gate 1 is checked here because it is a property of the DATA and is cheap; a leg that fails it should
never reach a battery.
"""
from __future__ import annotations
import argparse, json, os, random, re
from collections import defaultdict
from itertools import islice, zip_longest
from pathlib import Path

DC = Path(os.environ.get("EVAL_DATA_DIR", "data_cache"))

REVISIONS = {
    "google/boolq": "35b264d03638db9f4ce671b711558bf7ff0f80d5",
    "lighteval/siqa": "54c6a1f8cb6daf4f5abf24a601852612fb35eb25",
    "aps/super_glue": "3de24cf8022e94f4ee4b9d55a6f539891524d646",
    # ybisk/piqa is a script dataset (needs trust_remote_code and will not pin); baber/piqa is
    # the same data as parquet, so it loads under a pinned revision like everything else.
    "baber/piqa": "142f6d7367fd9877f0fb3b5734ea6a545f54cdd1",
    "tasksource/reclor": "0414b39bfc39b2d555b48fa245fc198744c46215",
    "allenai/qasc": "a34ba204eb9a33b919c10cc08f4f1c8dae5ec070",
    "EleutherAI/hendrycks_math": "21a5633873b6a120296cce3e2df9d5550074f4a3",
    "cais/mmlu": "c30699e8356da336a370243923dbaf21066bb9fe",
    "tasksource/lsat-rc": "f0923a196e509340a94d1954e237ac95c65e6cf8",
    "Samsoup/cosmos_qa": "5511553160809abc4f9c11d12421ec0a9681ee75",
    "textmachinelab/quail": "2bd9d7f90a532fe1a910b70972cef5fda341c8fe",
    "cam-cst/cbt": "72b5c46b1248e3316360f0f2f0b2c39e773b68e4",
    "jeggers/riddle_sense": "42baa6f1630b798a7f9c26b8e0af25ed523f936d",
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


def _row(prompt, gold, distractors, rng):
    choices = [gold] + [d for d in distractors if d and d != gold]
    if len(choices) < 2:
        return None
    rng.shuffle(choices)
    return {"prompt": prompt.strip() + "\nAnswer:", "answer": gold,
            "choices": choices, "answer_idx": choices.index(gold)}


def build_boolq(n, rng):
    """Passage + question -> yes/no. Contrast is minimal by construction: same passage, two answers."""
    for r in _load("google/boolq", split="validation").select(range(min(n, 3270))):
        yield _row(f"{r['passage']}\nQuestion: {r['question']}?", "yes" if r["answer"] else "no",
                   ["no" if r["answer"] else "yes"], rng)


def build_siqa(n, rng):
    """Social commonsense: context+question, 3 plausible answers. The distractors are human-written."""
    d = _load("lighteval/siqa", split="validation")
    for r in d.select(range(min(n, len(d)))):
        opts = [r["answerA"], r["answerB"], r["answerC"]]
        gold = opts[int(r["label"]) - 1]
        yield _row(f"{r['context']}\nQuestion: {r['question']}", gold,
                   [o for o in opts if o != gold], rng)


def build_wic(n, rng):
    """Word-in-context: same word, two sentences, same sense or not. Minimal pair by design."""
    d = _load("aps/super_glue", "wic", split="validation")
    for r in d.select(range(min(n, len(d)))):
        p = (f"Sentence 1: {r['sentence1']}\nSentence 2: {r['sentence2']}\n"
             f"Question: is '{r['word']}' used with the same meaning in both sentences?")
        gold = "yes" if r["label"] == 1 else "no"
        yield _row(p, gold, ["no" if gold == "yes" else "yes"], rng)


def build_piqa(n, rng):
    """Physical commonsense: a goal and two procedures, one workable. Length-matched by construction."""
    d = _load("baber/piqa", split="validation")
    for r in d.select(range(min(n, len(d)))):
        opts = [r["sol1"], r["sol2"]]
        gold = opts[int(r["label"])]          # label is a STRING in this mirror
        yield _row(f"Goal: {r['goal']}", gold, [o for o in opts if o != gold], rng)


def build_reclor(n, rng):
    """Logical reading comprehension (LSAT/GMAT). The hardest of the five; 4 options."""
    d = _load("tasksource/reclor", split="validation")
    for r in d.select(range(min(n, len(d)))):
        opts = list(r["answers"])
        gold = opts[int(r["label"])]
        yield _row(f"{r['context']}\nQuestion: {r['question']}", gold,
                   [o for o in opts if o != gold], rng)


def build_mmlu_all_nomenu_cloze(n, rng):
    """All MMLU subjects, interleaved; candidates are text and never appear as a menu."""
    unique, conflicts = {}, set()
    for row in _load("cais/mmlu", "all", split="test"):
        question = str(row["question"]).strip()
        choices = [str(c).strip() for c in row["choices"]]
        index = int(row["answer"])
        if not 0 <= index < len(choices):
            raise ValueError("MMLU gold index is outside the candidate list")
        gold = choices[index]
        if (not question or not gold or len(choices) < 2
                or len(set(choices)) != len(choices) or any(not c for c in choices)):
            continue
        key = question, tuple(sorted(choices))
        if key in unique and unique[key][1] != gold:
            conflicts.add(key)
        unique.setdefault(key, (row, gold, choices))
    subjects = defaultdict(list)
    for key, (row, gold, choices) in unique.items():
        if key not in conflicts:
            item = _row(key[0], gold, [c for c in choices if c != gold], rng)
            item["subject"] = row["subject"]
            subjects[row["subject"]].append(item)
    pools = [subjects[name] for name in sorted(subjects)]
    for pool in pools:
        rng.shuffle(pool)
    interleaved = (row for tier in zip_longest(*pools) for row in tier if row is not None)
    yield from islice(interleaved, n)


def _reclor_all():
    """Validation then train: nothing here is trained on, so train items are eval items too."""
    for split in ("validation", "train"):
        yield from _load("tasksource/reclor", split=split)


def build_reclor_full(n, rng, context=True):
    """ReClor over both splits; context=False keeps only the question, which measures how much of
    the leg is answerable from the options alone (the authors' EASY/HARD bias, per item)."""
    for r in islice(_reclor_all(), n):
        opts = list(r["answers"])
        gold = opts[int(r["label"])]
        prompt = f"{r['context']}\nQuestion: {r['question']}" if context else f"Question: {r['question']}"
        yield _row(prompt, gold, [o for o in opts if o != gold], rng)


def build_qasc(n, rng, facts=True, noleak=False):
    """Two-fact science composition, 8 options. facts=True states both facts (composition);
    facts=False is the closed-book form (recall). The gold is copied verbatim from the facts in 74% of
    items, so facts=True fails gate 1; noleak=True keeps only the items where it is not."""
    for split in ("validation", "train"):
        for r in _load("allenai/qasc", split=split):
            opts = list(r["choices"]["text"])
            gold = opts[r["choices"]["label"].index(r["answerKey"])]
            if noleak and gold.lower() in f"{r['fact1']} {r['fact2']}".lower():
                continue
            prompt = (f"Fact 1: {r['fact1']}\nFact 2: {r['fact2']}\n" if facts else "") + f"Question: {r['question']}"
            yield _row(prompt, gold, [o for o in opts if o != gold], rng)


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


TASKSOURCE = {"lsat_rc": ("lsat-rc", "tasksource/lsat-rc"), "cosmos_qa": ("cosmos_qa", "Samsoup/cosmos_qa"),
              "quail": ("quail", "textmachinelab/quail"),
              # Children's Book Test: 20 sentences, then a 21st with one word blanked; the answer names the
              # word after "Answer:", which moved with procedural data in the tasksource survey (2 seeds, 360M
              # base and instruct, OLMo-1B). Candidates fill the blank in place would score 0.9 and barely move.
              "cbt_cn": ("cbt/cn", "cam-cst/cbt"), "cbt_ne": ("cbt/ne", "cam-cst/cbt"),
              "riddle_sense": ("riddle_sense", "jeggers/riddle_sense")}


def build_tasksource_mc(n, rng, leg):
    """A tasksource MultipleChoice task, every split pooled (none is trained on) and deduplicated:
    quail ships its validation set again as test."""
    from tasksource import load_task
    task, repo = TASKSOURCE[leg]
    d, seen = load_task(task, revision=REVISIONS[repo]), set()
    for split in ("validation", "test", "train"):
        for r in d.get(split, ()):
            opts = [r[k] for k in sorted(r) if k.startswith("choice")]
            key = (r["inputs"], *opts)
            if key in seen:
                continue
            seen.add(key)
            gold = opts[int(r["labels"])]
            yield _row(f"{r['inputs']}", gold, [o for o in opts if o != gold], rng)


def build_quail_clean(n, rng):
    """QuAIL without its two levers: every item offers "not enough information" (gold 11.5%), a
    label prior like FOLIO's neutral, so it is removed and its gold items dropped; and in 6.7% of items
    only the gold is copied verbatim from the passage, a copy detector's shortcut, so those go too."""
    for r in build_tasksource_mc(n, rng, "quail"):
        p = r["prompt"].lower()
        others = [c for c in r["choices"] if c != r["answer"]]
        if "not enough information" in r["answer"].lower() or (
                r["answer"].lower() in p and not any(c.lower() in p for c in others)):
            continue
        yield _row(r["prompt"][:-len("\nAnswer:")], r["answer"],
                   [c for c in others if "not enough information" not in c.lower()], rng)


BUILDERS = {"boolq": build_boolq, "siqa": build_siqa, "wic": build_wic,
            "piqa": build_piqa, "reclor": build_reclor,
            "reclor_full": build_reclor_full,
            "reclor_noctx": lambda n, rng: build_reclor_full(n, rng, context=False),
            "qasc_facts": build_qasc, "qasc_closed": lambda n, rng: build_qasc(n, rng, facts=False),
            "qasc_facts_noleak": lambda n, rng: build_qasc(n, rng, noleak=True),
            "math_l12": build_math_l12, "math_l12_mc": build_math_l12_mc,
            "mmlu_all_nomenu_cloze": build_mmlu_all_nomenu_cloze,
            "quail_clean": build_quail_clean,
            **{leg: (lambda n, rng, leg=leg: build_tasksource_mc(n, rng, leg)) for leg in TASKSOURCE},
            **{leg: (lambda n, rng, leg=leg: build_cbt(n, rng, leg)) for leg in ("cbt_cn", "cbt_ne")}}


def _most_frequent(r):
    """The option the prompt repeats most, counting whole words."""
    return max(r["choices"], key=lambda c: len(re.findall(rf"\b{re.escape(c.lower())}\b", r["prompt"].lower())))


def build_cbt(n, rng, leg):
    """CBT without its frequency lever: the gold is the candidate the passage repeats most in ~28% of items
    (chance 10%), so those items are kept only at the chance rate. Models do not use the lever (their picks
    agree with it 18-31%), but a leg a word counter beats by 15+ points fails gate 1."""
    rows = [r for r in build_tasksource_mc(n, rng, leg) if r]
    hit = [_most_frequent(r) == r["answer"] for r in rows]
    f, c = sum(hit) / len(rows), 1 / len(rows[0]["choices"])
    keep = min(1.0, c / (1 - c) * (1 - f) / f)   # share of lever items after subsampling = chance
    for r, h in zip(rows, hit):
        if not h or rng.random() < keep:
            yield r


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
    short = sum(min(r["choices"], key=len) == r["answer"] for r in rows) / len(rows)
    chance = sum(1 / len(r["choices"]) for r in rows) / len(rows)
    dlen = (sum(len(r["answer"]) for r in rows) / len(rows)
            - sum(sum(len(c) for c in r["choices"]) / len(r["choices"]) for r in rows) / len(rows))
    return {"leak": leak, "binary": binary, "extractive": extractive, "most_frequent_picker": freq, "shortest_picker": short, "chance": chance,
            "shortest_excess_pt": 100 * (short - chance), "gold_len_delta_chars": dlen}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tasks", nargs="+", choices=sorted(BUILDERS), default=sorted(BUILDERS))
    ap.add_argument("--n", type=int, default=600)
    ap.add_argument("--max-prompt-chars", type=int, default=1400,
                    help="drop items whose prompt is too long for the battery's max_length")
    ap.add_argument("--seed", type=int, default=43)
    ap.add_argument("--output-dir", type=Path, default=DC,
                    help="Write new legs here; existing files are never overwritten")
    a = ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for task in a.tasks:
        out = a.output_dir / f"{task}_eval.jsonl"
        if out.exists():
            raise FileExistsError(out)
    for t in a.tasks:
        rng = random.Random(a.seed)
        rows = [r for r in BUILDERS[t](a.n * 2, rng) if r]
        rows = [r for r in rows if len(r["prompt"]) <= a.max_prompt_chars][:a.n]
        if not rows:
            print(f"[build] {t}: NO rows survived; skipped"); continue
        out = a.output_dir / f"{t}_eval.jsonl"
        with out.open("x") as file:
            file.write("".join(json.dumps(r) + "\n" for r in rows))
        if "choices" not in rows[0]:  # qa_nll leg: no options to game
            print(f"[build] {t:<7} n={len(rows):<5} qa_nll (no choices) -> {out}"); continue
        g = gate1(rows)
        lever = g["most_frequent_picker"] - g["chance"] if g["extractive"] else 0
        flag = ("  <-- FAILS GATE 1" if g["leak"] > 0.10 or g["shortest_excess_pt"] > 10 or lever > 0.10 else "")
        print(f"[build] {t:<7} n={len(rows):<5} leak={'n/a (binary)' if g['binary'] else f"n/a (extractive; most-frequent-picker {g['most_frequent_picker']:.1%})" if g['extractive'] else format(g['leak'],'.1%')} "
              f"shortest-picker={g['shortest_picker']:.1%} (chance {g['chance']:.1%}, "
              f"excess {g['shortest_excess_pt']:+.1f}pt) gold_len_delta={g['gold_len_delta_chars']:+.0f}ch"
              f" -> {out}{flag}")


if __name__ == "__main__":
    main()
