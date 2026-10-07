"""Answer numeric questions about a passage that states many numbers: count the facts matching a
description, total them, compare two of them, take the spread of a group, or the share left over.

Passages are game logs, census breakdowns, timelines and stock ledgers. Most numbers in a passage are
distractors for any one question, so the work is locating the right facts before the arithmetic.
Level adds facts and filter conditions.
"""
import itertools
import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

ORD = ["first", "second", "third", "fourth"]
NAMES = ["Adams", "Baker", "Cole", "Diaz", "Evans", "Ford", "Grant", "Hayes", "Ito", "Jones", "Khan", "Lopez",
         "Moore", "Novak", "Ortiz", "Park"]
TEAMS = ["Bears", "Hawks", "Lions", "Rams", "Jets", "Colts", "Sharks", "Wolves"]
ANCESTRY = ["German", "Irish", "Italian", "Polish", "English", "French", "Norwegian", "Dutch", "Swedish",
            "Scottish", "Greek", "Czech"]
PLACES = ["Ardena", "Belmar", "Corvel", "Dunmore", "Estrel", "Falkirk", "Galen", "Harrow"]
ACTORS = ["the Duke", "the Republic", "the Guild", "the League", "the Crown", "the Council"]
ACTS = ["founded a fort", "signed a treaty", "lost a battle", "built a bridge", "opened a port", "held a census",
        "raised a militia", "minted coins", "moved the capital"]
ITEMS = ["apples", "bricks", "cement", "lumber", "nails", "paint", "rope", "salt", "tiles", "wire"]
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
YARDS = {"field goal": (18, 58), "touchdown run": (1, 75), "touchdown pass": (2, 90)}


@dataclass
class PassageNumeracyConfig(Config):
    n_facts: float = 5
    n_conditions: float = 1

    def apply_difficulty(self, level):
        self.n_facts += 2.5 * level
        self.n_conditions += 0.4 * level


# ---- passage families: rows of categorical fields plus a value `v` --------------------------------
# keys: filterable fields; noun: (field naming the fact, its default); mods: field -> phrase for a value;
# ops: question templates ({desc} = plural description, {A}/{B} = one fact, {G} = groups, {t} = threshold).

def _sports(rng, n):
    teams = rng.sample(TEAMS, 2)
    team_of = {p: rng.choice(teams) for p in rng.sample(NAMES, rng.randint(3, 5))}
    rows = [{"player": p, "team": team_of[p], "kind": k, "quarter": rng.randrange(4), "v": rng.randint(*YARDS[k])}
            for p, k in ((rng.choice(list(team_of)), rng.choice(list(YARDS))) for _ in range(n))]
    rows.sort(key=lambda r: r["quarter"])
    text = " ".join(f"In the {ORD[r['quarter']]} quarter, {r['player']} of the {r['team']} "
                    f"{'kicked' if r['kind'] == 'field goal' else 'scored on'} a {r['v']}-yard {r['kind']}."
                    for r in rows)
    return text, rows, dict(
        keys=["player", "team", "kind", "quarter"], noun=("kind", "scoring play"),
        mods={"player": "by {}".format, "team": "by the {}".format, "quarter": lambda q: f"in the {ORD[q]} quarter"},
        thr="of more than {} yards",
        ops={"count": "How many {desc} were there?",
             "sum": "How many total yards came from {desc}?",
             "range": "How many yards longer was the longest of the {desc} than the shortest?",
             "diff": "How many yards longer was {A} than {B}?"})


def _ledger(rng, n):
    items = rng.sample(ITEMS, rng.randint(3, 5))
    rows = [{"item": rng.choice(items), "day": rng.randrange(7), "dir": rng.choice(["incoming", "outgoing"]),
             "v": rng.randint(5, 400)} for _ in range(n)]
    rows.sort(key=lambda r: r["day"])
    text = " ".join(f"On {DAYS[r['day']]}, the warehouse {'received' if r['dir'] == 'incoming' else 'sent out'} "
                    f"{r['v']} crates of {r['item']}." for r in rows)
    return text, rows, dict(
        keys=["item", "day", "dir"], noun=("dir", "shipment"),
        mods={"item": "of {}".format, "day": lambda d: f"on {DAYS[d]}"},
        thr="of more than {} crates",
        ops={"count": "How many {desc} were there?",
             "sum": "How many crates in total did the {desc} carry?",
             "range": "How many more crates did the largest of the {desc} carry than the smallest?",
             "diff": "How many more crates did {A} carry than {B}?"})


def _timeline(rng, n):
    actors = rng.sample(ACTORS, 3)
    pairs = rng.sample([(a, b) for a in actors for b in ACTS], min(n, 3 * len(ACTS)))
    start = rng.randint(1000, 1700)
    years = sorted(rng.sample(range(start, start + 15 * len(pairs)), len(pairs)))
    rows = [{"actor": a, "act": b, "v": y} for (a, b), y in zip(pairs, years)]
    text = " ".join(f"In {r['v']}, {r['actor']} {r['act']}." for r in rows)
    return f"A history of {rng.choice(PLACES)}. {text}", rows, dict(
        keys=["actor"], noun=(None, "event"), mods={"actor": "involving {}".format}, clause=True,
        ops={"count": "How many {desc} happened before {t}?",
             "range": "How many years passed between the first and the last of the {desc}?",
             "diff": "How many years passed between the year {A} and the year {B}?"})


def _census(rng, n):
    groups = rng.sample(ANCESTRY, min(n, len(ANCESTRY) - 1))
    cuts = sorted(rng.sample(range(5, 995), len(groups)))
    shares = [b - a for a, b in zip([0] + cuts, cuts + [1000])]  # tenths of a percent; the last part is "other"
    rows = [{"group": g, "v": s / 10} for g, s in zip(groups, shares)]
    text = (f"In the {rng.randint(1950, 2020)} census, {rng.choice(PLACES)} had {rng.randint(2000, 90000)} residents. "
            + "; ".join(f"{_num(r['v'])}% were of {r['group']} ancestry" for r in rows) + ".")
    return text, rows, dict(
        keys=["group"], total=100, sets=True,
        ops={"sum": "What percentage of residents were of {G} ancestry?",
             "rest": "What percentage of residents were of none of these ancestries: {G}?",
             "diff": "How many more percentage points of residents were of {A} ancestry than of {B} ancestry?"})


FAMILIES = [_sports, _ledger, _timeline, _census]


def _num(x):
    return f"{round(x, 1):.1f}".rstrip("0").rstrip(".")


def _match(rows, cond, thr=None):
    return [r for r in rows if all(r[k] in vs for k, vs in cond.items()) and (thr is None or r["v"] > thr)]


def _join(words, conj="or"):
    return words[0] if len(words) == 1 else ", ".join(words[:-1]) + f" {conj} " + words[-1]


def _desc(fam, cond, plural=True, thr=None):
    nk, default = fam.get("noun", (None, "fact"))
    nouns = [default.replace("shipment", f"{v} shipment") if nk == "dir" else v for v in cond.get(nk, [])] or [default]
    noun = _join([w + "s" * plural for w in nouns])
    mods = [_join([fam["mods"][k](v) for v in vs]) for k, vs in cond.items() if k != nk]
    return " ".join([noun] + mods + ([fam["thr"].format(thr)] if thr is not None else []))


def _one(fam, rows, row):
    """Shortest description that picks out `row` alone, or None."""
    if fam.get("clause"):
        return f"{row['actor']} {row['act']}" if len(_match(rows, {"actor": [row["actor"]], "act": [row["act"]]})) == 1 else None
    if fam.get("sets"):
        return row["group"]
    for size in range(1, len(fam["keys"]) + 1):
        for keys in itertools.combinations(fam["keys"], size):
            cond = {k: [row[k]] for k in keys}
            if len(_match(rows, cond)) == 1:
                return "the " + _desc(fam, cond, plural=False)
    return None


def _question(rng, fam, rows, n_cond):
    op = rng.choice(list(fam["ops"]))
    if op == "diff":
        a, b = sorted(rng.sample(rows, 2), key=lambda r: -r["v"])
        A, B = _one(fam, rows, a), _one(fam, rows, b)
        if not A or not B or a["v"] == b["v"]:
            return None
        return op, fam["ops"][op].format(A=A, B=B), a["v"] - b["v"]
    if fam.get("sets"):  # census: a set of groups
        g = [r["group"] for r in rng.sample(rows, min(len(rows), rng.randint(1 + (op == "sum"), 1 + n_cond)))]
        got = sum(r["v"] for r in _match(rows, {"group": g}))
        return op, fam["ops"][op].format(G=_join(g, "or" if op == "sum" else "and")), \
            got if op == "sum" else fam["total"] - got
    keys = rng.sample(fam["keys"], min(n_cond, len(fam["keys"])))
    cond = {k: sorted({rng.choice(rows)[k] for _ in range(1 + (rng.random() < 0.25))}) for k in keys}
    thr = t = None
    if op == "count" and "thr" in fam and rng.random() < 0.4:
        thr = rng.choice(rows)["v"]
    if op == "count" and fam.get("clause"):
        t = rng.choice(rows)["v"] + 1
    hit = [r for r in _match(rows, cond, thr) if t is None or r["v"] < t]
    if not hit or (op == "range" and len(hit) < 2):
        return None
    value = {"count": len(hit), "sum": sum(r["v"] for r in hit),
             "range": max(r["v"] for r in hit) - min(r["v"] for r in hit)}[op]
    return op, fam["ops"][op].format(desc=_desc(fam, cond, thr=thr), t=t), value


class PassageNumeracy(DevTask):
    summary = ("Count, total, compare, take the spread of, or find the remainder of numbers stated in a passage "
               "full of distractor numbers -- game logs (yards), stock ledgers (crates), timelines (years), census "
               "breakdowns (percentages, one decimal) -- selected by one or more descriptive conditions.")
    task_version = 2

    def __init__(self, config=None):
        super().__init__(config=config or PassageNumeracyConfig())

    def generate_entry(self):
        c, rng = self.config, random
        while True:
            family = rng.choice(FAMILIES)
            text, rows, fam = family(rng, max(3, sround(c.n_facts)))
            q = _question(rng, fam, rows, max(1, sround(c.n_conditions)))
            if q:
                op, question, value = q
                return Entry({"passage": text, "question": question, "family": family.__name__[1:], "op": op},
                             _num(value))

    def render_prompt(self, m):
        fmt = "a number, at most one decimal, no % sign" if m["family"] == "census" else "an integer"
        return f"{m['passage']}\n{m['question']} Answer with {fmt}."

    def score_answer(self, answer, entry):
        got = re.sub(r"[,%\s]", "", str(answer)).rstrip(".")
        if not re.fullmatch(r"-?\d+(\.\d+)?", got):
            return 0.0
        return float(abs(float(got) - float(entry.answer)) < 1e-6)
