"""Give the probability, as a percentage to one decimal place, of a composed event about a random process, optionally
given a composed observation.

Three processes: draws from an urn (2-4 colours, 2-5 draws, replacement set draw by draw, so draws are
dependent), independent coins and dice with stated biases, and a two-stage process where a coin picks the bag
that is then drawn from (a hidden cause, so "which bag was used" given the draws is Bayesian inversion). An
event is a random formula -- and, or, not, if-then-otherwise -- over atomic facts about the outcome (a draw's
colour, counts, orderings, sums, the hidden choice), as general as most_probable_evidence's observation but
over dependent, multi-valued variables. Probabilities are exact by enumerating outcomes. Rejected: atoms that
do not affect the event, events certain or impossible, answers the setup states (a bias, a colour's share),
observations that do not change the answer, 50%, and answers that round to 0.0% or 100.0% or sit within 0.025 point
of a rounding boundary (every gold label has a margin on both sides). A percentage, not a fraction: its first token
carries the gist (about how likely), where a reduced fraction like 1506/1675 makes the model commit to bookkeeping digits
before any sign of the magnitude. One decimal, not an integer: a wrong method (kept-out draws treated as put back) still
rounds to the right integer 35% of the time but to the right tenth 5% of the time (2% for exact fractions).
Level adds variables, formula depth, conditioning and the two-stage process.
"""
import itertools
import random
import re
from dataclasses import dataclass
from fractions import Fraction as F

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

COLORS = ["red", "blue", "green", "yellow"]
ORD = ["first", "second", "third", "fourth", "fifth"]
NUM = ["no", "one", "two", "three", "four", "five"]
BIASES = [F(1, 4), F(1, 3), F(2, 5), F(3, 5), F(2, 3), F(3, 4), F(1, 5), F(4, 5)]


@dataclass
class OutcomeProbabilityConfig(Config):
    n_vars: float = 2
    depth: float = 1
    p_observe: float = 0.0
    p_two_stage: float = 0.0
    max_count: float = 4

    def apply_difficulty(self, level):
        self.n_vars = min(5, self.n_vars + 0.5 * level)
        self.depth += 0.5 * level
        self.p_observe = min(0.6, 0.12 * level)
        self.p_two_stage = min(0.35, 0.08 * level)
        self.max_count += level


def _draws(colors, counts, back, n):
    """{sequence: probability} for n draws with a draw-by-draw replacement schedule."""
    out = {}
    for seq in itertools.product(colors, repeat=n):
        left, p = dict(counts), F(1)
        for i, c in enumerate(seq):
            if left[c] <= 0:
                p = F(0)
                break
            p *= F(left[c], sum(left.values()))
            if i < n - 1 and not back[i]:
                left[c] -= 1
        if p:
            out[seq] = p
    return out


def _draw_atoms(rng, colors, n, item, at=lambda w: w):
    """Atomic facts about a draw sequence, read from a world through `at`."""
    atoms = []
    for i in range(n):
        for c in colors:
            atoms.append((f"the {ORD[i]} {item} drawn is {c}", lambda w, i=i, c=c: at(w)[i] == c))
    for c in colors:
        for k in range(1, n + 1):
            atoms.append((f"at least {NUM[k]} {item}{'s' * (k > 1)} drawn {'are' if k > 1 else 'is'} {c}",
                          lambda w, c=c, k=k: at(w).count(c) >= k))
        atoms.append((f"exactly one {item} drawn is {c}", lambda w, c=c: at(w).count(c) == 1))
    for x, y in itertools.permutations(colors, 2):
        atoms.append((f"a {x} {item} is drawn before any {y} one",
                      lambda w, x=x, y=y: x in at(w) and (y not in at(w) or at(w).index(x) < at(w).index(y))))
    atoms.append((f"all {item}s drawn have the same colour", lambda w: len(set(at(w))) == 1))
    return atoms


def _schedule(rng, n, item):
    back = [rng.random() < 0.5 for _ in range(n - 1)]
    if len(set(back)) == 1:
        how = f"each {item} is {'put back' if back[0] else 'kept out'} before the next draw"
    else:
        how = "; ".join(f"the {ORD[i]} is {'put back' if b else 'kept out'}" for i, b in enumerate(back))
    return back, how


def _stock(counts, item):
    parts = [f"{v} {c}" for c, v in counts.items()]
    return (", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]) + f" {item}s"


def _urn(rng, c):
    n, k = max(2, sround(c.n_vars)), rng.randint(2, min(4, 1 + sround(c.n_vars)))
    colors = rng.sample(COLORS, k)
    counts = {col: rng.randint(1, max(2, sround(c.max_count))) for col in colors}
    back, how = _schedule(rng, n, "marble")
    worlds = _draws(colors, counts, back, n)
    text = f"A bag contains {_stock(counts, 'marble')}. {NUM[n].capitalize()} marbles are drawn at random: {how}."
    return text, worlds, _draw_atoms(rng, colors, n, "marble"), _shares(counts)


def _trials(rng, c):
    m = max(2, sround(c.n_vars))
    kinds = [rng.choice(["coin", "coin", "die"]) for _ in range(m)]
    names, spaces, lines, atoms = [], [], [], []
    for i, kind in enumerate(kinds):
        name = f"{kind} {'ABCDE'[i]}"
        names.append(name)
        if kind == "coin":
            p = rng.choice(BIASES)
            spaces.append({"H": p, "T": 1 - p})
            lines.append(f"{name[0].upper()}{name[1:]} lands heads with probability {p}.")
            atoms.append((f"{name} lands heads", lambda w, i=i: w[i] == "H"))
        else:
            sides = rng.choice([4, 6])
            spaces.append({v: F(1, sides) for v in range(1, sides + 1)})
            lines.append(f"{name[0].upper()}{name[1:]} is a fair {sides}-sided die.")
            t = rng.randint(2, sides)
            atoms += [(f"{name} shows an even number", lambda w, i=i: w[i] % 2 == 0),
                      (f"{name} shows at least {t}", lambda w, i=i, t=t: w[i] >= t)]
    dice = [i for i, k in enumerate(kinds) if k == "die"]
    coins = [i for i, k in enumerate(kinds) if k == "coin"]
    if len(dice) >= 2:
        s = rng.randint(4, 9)
        atoms.append((f"the dice total at least {s}", lambda w, s=s: sum(w[i] for i in dice) >= s))
    if len(coins) >= 2:
        k = rng.randint(1, len(coins))
        atoms.append((f"at least {NUM[k]} coin{'s' * (k > 1)} land{'s' * (k == 1)} heads",
                      lambda w, k=k: sum(w[i] == "H" for i in coins) >= k))
    worlds = {}
    for combo in itertools.product(*(list(sp.items()) for sp in spaces)):
        p = F(1)
        for _, q in combo:
            p *= q
        worlds[tuple(v for v, _ in combo)] = p
    stated = {q for sp in spaces for q in sp.values()}
    return "All of these are tossed or rolled once, independently. " + " ".join(lines), worlds, atoms, stated


def _two_stage(rng, c):
    n = max(2, min(3, sround(c.n_vars)))
    colors = rng.sample(COLORS, 2)
    bags = [{col: rng.randint(1, max(2, sround(c.max_count))) for col in colors} for _ in range(2)]
    if bags[0] == bags[1]:
        bags[1][colors[0]] += 1
    p = rng.choice(BIASES)
    back, how = _schedule(rng, n, "marble")
    worlds = {}
    for b, pb in ((0, p), (1, 1 - p)):
        for seq, q in _draws(colors, bags[b], back, n).items():
            worlds[(b, seq)] = pb * q
    text = (f"Bag 1 contains {_stock(bags[0], 'marble')}; bag 2 contains {_stock(bags[1], 'marble')}. A coin that "
            f"lands heads with probability {p} is tossed: on heads bag 1 is used, otherwise bag 2. {NUM[n].capitalize()} "
            f"marbles are then drawn at random from that bag: {how}.")
    atoms = [("bag 1 was used", lambda w: w[0] == 0)] + _draw_atoms(rng, colors, n, "marble", at=lambda w: w[1])
    return text, worlds, atoms, {p, 1 - p} | _shares(bags[0]) | _shares(bags[1])


def _shares(counts):
    return {F(v, sum(counts.values())) for v in counts.values()}


def _formula(rng, atoms, depth):
    """A random formula tree over atom indices: ("atom", i) | ("not", t) | ("and"|"or", t, u) | ("if", t, u, v)."""
    if depth <= 0 or rng.random() < 0.3:
        return ("atom", rng.randrange(len(atoms)))
    op = rng.choices(["not", "and", "or", "if"], weights=[0.6, 1.2, 1.0, 0.35])[0]
    return (op,) + tuple(_formula(rng, atoms, depth - 1) for _ in range({"not": 1, "if": 3}.get(op, 2)))


def _eval(t, atoms, w, fix=None):
    op = t[0]
    if op == "atom":
        return fix[t[1]] if fix and t[1] in fix else atoms[t[1]][1](w)
    v = [_eval(u, atoms, w, fix) for u in t[1:]]
    return {"not": lambda: not v[0], "and": lambda: v[0] and v[1], "or": lambda: v[0] or v[1],
            "if": lambda: v[1] if v[0] else v[2]}[op]()


def _text(t, atoms):
    if t[0] == "atom":
        return atoms[t[1]][0]
    op, v = t[0], [_text(u, atoms) for u in t[1:]]
    return {"not": lambda: f"(it is not the case that {v[0]})",   # parenthesised: its scope ends here
            "and": lambda: f"({v[0]} and {v[1]})", "or": lambda: f"({v[0]} or {v[1]})",
            "if": lambda: f"(if {v[0]}, then {v[1]}; otherwise {v[2]})"}[op]()


def _used(t):
    return {t[1]} if t[0] == "atom" else set().union(*(_used(u) for u in t[1:]))


def _prob(worlds, pred, given=None):
    num = den = F(0)
    for w, p in worlds.items():
        if given is None or given(w):
            den += p
            num += p if pred(w) else 0
    return num / den if den else None


def _collapses(t, atoms, worlds):
    """A compound formula that is true on exactly the worlds where one atom (or its negation) is."""
    if t[0] == "atom":
        return False
    truth = [_eval(t, atoms, w) for w in worlds]
    return any(all(atoms[i][1](w) == v for w, v in zip(worlds, truth)) or
               all(atoms[i][1](w) != v for w, v in zip(worlds, truth)) for i in _used(t))


class OutcomeProbability(DevTask):
    summary = ("Give the probability, as a percentage to one decimal place, of an and/or/not/if formula over facts about a "
               "random process -- dependent urn draws, independent biased coins and dice, or a coin choosing the bag "
               "(posterior on the hidden choice) -- optionally given an observed formula; the numeric twin of "
               "most_probable_outcome, as general as most_probable_evidence.")
    task_version = 4

    def __init__(self, config=None):
        super().__init__(config=config or OutcomeProbabilityConfig())

    def generate_entry(self):
        c, rng = self.config, random
        while True:
            process = _two_stage if rng.random() < c.p_two_stage else rng.choice([_urn, _trials])
            text, worlds, atoms, stated = process(rng, c)
            tree = _formula(rng, atoms, sround(c.depth))
            obs = _formula(rng, atoms, max(0, sround(c.depth) - 1)) if rng.random() < c.p_observe else None
            if process is _two_stage and rng.random() < 0.5:   # ask about the hidden cause, given the draws
                tree, obs = ("atom", 0), obs or ("and", ("atom", rng.randrange(1, len(atoms))),
                                                  ("atom", rng.randrange(1, len(atoms))))
            given = (lambda w: _eval(obs, atoms, w)) if obs else None
            ans = _prob(worlds, lambda w: _eval(tree, atoms, w), given)
            # the setup must not state the answer, and an observation must change it
            tenths = None if ans is None else round(1000 * ans)   # the answer in tenths of a percent
            if tenths is None or not 1 <= tenths <= 999 or tenths == 500 or abs(1000 * ans - tenths) > F(1, 4) \
                    or tenths in {round(1000 * q) for q in stated} \
                    or (obs and tenths == round(1000 * _prob(worlds, lambda w: _eval(tree, atoms, w)))):
                continue
            used = _used(tree)
            if obs is None and len(used) < 2:   # one atom, nothing observed: the setup states the answer
                continue
            live = [w for w in worlds if given is None or given(w)]
            if any(all(_eval(tree, atoms, w, {i: True}) == _eval(tree, atoms, w, {i: False}) for w in live)
                   for i in used):   # an atom that never changes the event is padding
                continue
            if obs is not None and any(all(_eval(obs, atoms, w, {i: True}) == _eval(obs, atoms, w, {i: False})
                                           for w in worlds) for i in _used(obs)):
                continue
            # linked atoms (a dice total and one die) can collapse a formula onto one of its atoms
            if _collapses(tree, atoms, live) or (obs is not None and _collapses(obs, atoms, list(worlds))):
                continue
            event, n_atoms = _text(tree, atoms), len(used)
            obs = (_text(obs, atoms),) if obs else None
            return Entry({"setup": text, "event": event, "observation": obs[0] if obs else None,
                          "process": process.__name__[1:], "n_atoms": n_atoms, "exact": f"{ans.numerator}/{ans.denominator}"},
                         f"{tenths // 10}.{tenths % 10}")

    def render_prompt(self, m):
        given = f"\nYou are told that {m['observation']}." if m["observation"] else ""
        return (f"{m['setup']}{given}\nWhat is the probability that {m['event']}? "
                "Answer with a percentage rounded to one decimal place, such as 37.5.")

    def score_answer(self, answer, entry):
        m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*%?", str(answer).strip().rstrip("."))
        if not m:
            return 0.0
        off = abs(float(m.group(1)) - float(entry.answer))
        return 1.0 if off < 0.05 else 0.5 if off < 0.15 else 0.0   # half credit for a rounding slip
