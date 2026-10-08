"""Answer a query over facts stated in a passage: select the facts matching a description, then
count, total, compare, take the spread of, or name the extreme of their values.

This is querying text as if it were a table. A passage states records (a delivery, an expense, a reading)
in varied sentences, mixed with numbers that are not the queried value (order numbers, days, ids) and, at
higher levels, small numbers written as words and corrections that overwrite an earlier fact. The
description can combine conditions, alternatives (A or B), exclusions (not A) and a threshold, so the work
is selection before the arithmetic. Schemas are everyday and abstract record types; none is a game log.
Level adds facts, conditions, exclusions and corrections.
"""
import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

PEOPLE = ["Amara", "Bruno", "Chen", "Dana", "Emil", "Farah", "Goran", "Hiro", "Ines", "Jonas", "Kofi", "Lucia",
          "Mateo", "Nadia", "Omar", "Priya"]
TOWNS = ["Alder", "Brook", "Cedar", "Dover", "Elm", "Fenwick", "Glen", "Hollow"]
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]

# A schema: record noun, categorical fields (values, phrase used in a description), the value (range, unit,
# question verb), sentence templates, and a distractor number that is never the queried value.
SCHEMAS = [
    dict(noun="delivery", plural="deliveries",
         fields={"courier": (PEOPLE, "by {}"), "goods": (["rice", "flour", "salt", "sugar", "beans"], "of {}"),
                 "town": (TOWNS, "to {}")},
         value=(5, 400, "kilograms"),
         say=["{courier} delivered {v} kilograms of {goods} to {town} (order {x}).",
              "Order {x}: {v} kilograms of {goods} went to {town}, carried by {courier}."],
         x=lambda r: f"#{r.randint(1000, 9999)}"),
    dict(noun="expense", plural="expenses",
         fields={"person": (PEOPLE, "by {}"), "category": (["food", "travel", "books", "tools", "rent"], "on {}"),
                 "month": (MONTHS, "in {}")},
         value=(3, 900, "euros"),
         say=["In {month}, {person} spent {v} euros on {category} (receipt {x}).",
              "Receipt {x} shows {person} paying {v} euros for {category} in {month}."],
         x=lambda r: f"{r.randint(10, 99)}-{r.randint(100, 999)}"),
    dict(noun="rainfall reading", plural="rainfall readings",
         fields={"station": (TOWNS, "at {}"), "month": (MONTHS, "in {}")},
         value=(2, 180, "millimetres"),
         say=["The {station} station, in service for {x} years, recorded {v} millimetres of rain in {month}.",
              "In {month}, {v} millimetres of rain fell at {station} (gauge {x})."],
         x=lambda r: r.randint(11, 60)),
    dict(noun="loan", plural="loans",
         fields={"member": (PEOPLE, "by {}"), "genre": (["poetry", "history", "science", "travel"], "of {} books"),
                 "branch": (TOWNS, "at the {} branch")},
         value=(2, 12, "books"),
         say=["{member} borrowed {v} {genre} books at the {branch} branch on day {x}.",
              "On day {x}, the {branch} branch lent {v} {genre} books to {member}."],
         x=lambda r: r.randint(2, 30)),
    dict(noun="harvest", plural="harvests",
         fields={"farm": (["North", "South", "East", "West", "Hill", "River"], "from the {} farm"),
                 "crop": (["apples", "pears", "plums", "cherries", "grapes"], "of {}"), "day": (DAYS, "on {}")},
         value=(4, 250, "crates"),
         say=["On {day}, the {farm} farm picked {v} crates of {crop} with {x} workers.",
              "{x} workers at the {farm} farm filled {v} crates of {crop} on {day}."],
         x=lambda r: r.randint(3, 40)),
    dict(noun="trip", plural="trips",
         fields={"driver": (PEOPLE, "by {}"), "vehicle": (["van", "truck", "bus", "car"], "in the {}"),
                 "day": (DAYS, "on {}")},
         value=(8, 600, "kilometres"),
         say=["On {day}, {driver} drove the {vehicle} {v} kilometres, leaving at {x}:00.",
              "{driver} took the {vehicle} out on {day} at {x}:00 and covered {v} kilometres."],
         x=lambda r: r.randint(5, 20)),
    dict(noun="object", plural="objects",
         fields={"color": (["red", "blue", "green", "white", "black"], "colored {}"),
                 "shape": (["cube", "sphere", "cone", "ring"], "shaped like a {}"),
                 "material": (["wood", "glass", "steel", "clay"], "made of {}")},
         value=(2, 500, "grams"),
         say=["Item {x} is a {color} {shape} made of {material} weighing {v} grams.",
              "A {material} {shape}, colored {color} and labelled {x}, weighs {v} grams."],
         x=lambda r: f"{r.choice('ABCDEFGH')}{r.randint(1, 99)}"),
]
REL = {"count": None, "sum": None, "max": "largest", "min": "smallest", "argmax": "largest", "argmin": "smallest",
       "range": None, "diff": None}


@dataclass
class FactQueryConfig(Config):
    n_facts: float = 5
    n_conditions: float = 1
    p_exclude: float = 0.0
    p_words: float = 0.0
    n_corrections: float = 0

    def apply_difficulty(self, level):
        self.n_facts += 2 * level
        self.n_conditions += 0.35 * level
        self.p_exclude = min(0.4, 0.1 * level)
        self.p_words = min(0.5, 0.15 * level)
        self.n_corrections += 0.3 * level


def _join(words, conj="or"):
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + f" {conj} " + words[-1]


def _match(rows, cond, thr=None):
    return [r for r in rows if all((r[k] in vs) != neg for k, (vs, neg) in cond.items())
            and (thr is None or r["v"] > thr)]


def _desc(s, cond, thr=None, plural=True):
    mods = [("not " if neg else "") + s["fields"][k][1].format(_join(vs)) for k, (vs, neg) in cond.items()]
    unit = s["value"][2]
    return " ".join([s["plural"] if plural else s["noun"]] + mods + ([f"of more than {thr} {unit}"] if thr is not None else []))


def _one(s, rows, row):
    """The shortest description naming `row` alone, e.g. "the delivery of salt to Dover", or None."""
    keys = list(s["fields"])
    for size in range(1, len(keys) + 1):
        for start in range(len(keys)):
            ks = (keys[start:] + keys[:start])[:size]
            cond = {k: ([row[k]], False) for k in ks}
            if len(_match(rows, cond)) == 1:
                return "the " + _desc(s, cond, plural=False)
    return None


def _num(v, rng, p_words):
    return WORDS[v] if v < len(WORDS) and rng.random() < p_words else str(v)


class FactQuery(DevTask):
    summary = ("Answer an aggregate question (count, total, extreme value, which one, spread, difference) about "
               "records stated in prose, selecting them by conditions with alternatives, exclusions and thresholds, "
               "past distractor numbers, number words and later corrections.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or FactQueryConfig())

    def generate_entry(self):
        c, rng = self.config, random
        while True:
            s = rng.choice(SCHEMAS)
            pools = {k: rng.sample(vals, min(len(vals), rng.randint(2, 4))) for k, (vals, _) in s["fields"].items()}
            lo, hi, unit = s["value"]
            rows = [{**{k: rng.choice(p) for k, p in pools.items()}, "v": rng.randint(lo, hi)}
                    for _ in range(max(3, sround(c.n_facts)))]
            sentences = [rng.choice(s["say"]).format(**{**r, "v": _num(r["v"], rng, c.p_words)}, x=s["x"](rng)) for r in rows]
            for _ in range(sround(c.n_corrections)):   # an earlier fact is overwritten; questions see the new value
                r = rng.choice(rows)
                name = _one(s, rows, r)
                new = rng.randint(lo, hi)
                if name and new != r["v"]:
                    sentences.append(f"Correction: {name} was {new} {unit}, not {r['v']}.")
                    r["v"] = new
            q = self._question(rng, s, rows, pools, c)
            if q:
                question, answer, kind = q
                return Entry({"passage": " ".join(sentences), "question": question, "kind": kind}, str(answer))

    def _question(self, rng, s, rows, pools, c):
        op = rng.choice(list(REL))
        unit = s["value"][2]
        if op == "diff":
            a, b = sorted(rng.sample(rows, 2), key=lambda r: -r["v"])
            A, B = _one(s, rows, a), _one(s, rows, b)
            if not A or not B or a["v"] == b["v"]:
                return None
            return f"By how many {unit} does {A} exceed {B}?", a["v"] - b["v"], "number"
        keys = rng.sample(list(pools), min(len(pools), max(1, sround(c.n_conditions))))
        target = rng.choice(list(pools)) if op in ("argmax", "argmin") else None
        keys = [k for k in keys if k != target]
        cond = {}
        for k in keys:
            vals = rng.sample(pools[k], 1 + (rng.random() < 0.3 and len(pools[k]) > 2))
            cond[k] = (vals, rng.random() < c.p_exclude)
        thr = rng.choice(rows)["v"] if op == "count" and rng.random() < 0.3 else None
        hit = _match(rows, cond, thr)
        if not hit or (op in ("range", "argmax", "argmin") and len(hit) < 2):
            return None
        desc = _desc(s, cond, thr)
        vals = [r["v"] for r in hit]
        if op == "count":
            return f"How many {desc} are there?", len(hit), "number"
        if op == "sum":
            return f"What is the total number of {unit} across the {desc}?", sum(vals), "number"
        if op in ("max", "min"):
            return f"What is the {REL[op]} number of {unit} among the {desc}?", (max if op == "max" else min)(vals), "number"
        if op == "range":
            return f"How many {unit} separate the largest and the smallest of the {desc}?", max(vals) - min(vals), "number"
        best = (max if op == "argmax" else min)(vals)
        winners = {r[target] for r in hit if r["v"] == best}
        if vals.count(best) > 1 or len(winners) != 1:
            return None
        field = target if target not in ("goods", "crop", "category", "genre") else "kind"
        return (f"Among the {desc}, which {target} has the single {REL[op]} number of {unit}?",
                winners.pop(), f"the {field}")

    def render_prompt(self, m):
        fmt = "an integer" if m["kind"] == "number" else "only the name, exactly as written in the text"
        return f"{m['passage']}\n{m['question']} Answer with {fmt}."

    def score_answer(self, answer, entry):
        got = str(answer).strip().strip(".").strip()
        if re.fullmatch(r"-?\d+", entry.answer):
            got = got.replace(",", "")
            return float(re.fullmatch(r"-?\d+", got) is not None and int(got) == int(entry.answer))
        return float(got.lower().removeprefix("the ").strip() == entry.answer.lower())
