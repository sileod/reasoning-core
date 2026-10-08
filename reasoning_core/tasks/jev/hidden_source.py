"""Which source produced the observations? Bags with known contents and prior weights, a hidden pick, and the
marbles drawn from it: the decision is the most probable bag, and `soft` is the exact posterior over bags -- the
calibration target a decision model should match, not just its argmax. Draws are with or without replacement;
level adds bags, colours, draws and uneven priors. Near-ties (posterior margin under 0.1) are rejected so the
label is well defined. The state (bags, priors, draws) comes only from random.Random(state_seed).
"""
import random
from dataclasses import dataclass
from fractions import Fraction as F

from reasoning_core.decision import Decision
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

COLORS = ["red", "blue", "green", "yellow", "white", "black"]
NAMES = ["A", "B", "C", "D", "E"]


@dataclass
class HiddenSourceConfig(Config):
    n_bags: float = 2
    n_colors: float = 2
    n_draws: float = 2
    max_count: float = 5
    p_uneven_prior: float = 0.0
    min_margin: float = 0.1

    def apply_difficulty(self, level):
        self.n_bags = min(5, self.n_bags + 0.5 * level)
        self.n_colors = min(4, self.n_colors + 0.35 * level)
        self.n_draws = min(5, self.n_draws + 0.5 * level)
        self.max_count = self.max_count + level
        self.p_uneven_prior = min(0.7, 0.15 * level)


def _likelihood(counts, seq, replace):
    left, p = dict(counts), F(1)
    for c in seq:
        if left[c] <= 0:
            return F(0)
        p *= F(left[c], sum(left.values()))
        if not replace:
            left[c] -= 1
    return p


def _stock(counts):
    parts = [f"{v} {c}" for c, v in counts.items() if v]
    return ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]


class HiddenSource(Task):
    summary = ("Name the bag most likely to have produced the observed draws, from known contents and prior "
               "weights; the decision carries the exact posterior over bags.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or HiddenSourceConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        c, rng = self.config, random.Random(state_seed)
        r = lambda x: sround(x, seed=rng.random())   # sizes too come from the state seed, not the global RNG
        for _ in range(1000):
            names = NAMES[:max(2, r(c.n_bags))]
            colors = rng.sample(COLORS, max(2, r(c.n_colors)))
            bags = {n: {col: rng.randint(0, max(2, r(c.max_count))) for col in colors} for n in names}
            if any(sum(b.values()) < 2 for b in bags.values()) or len({tuple(b.values()) for b in bags.values()}) < len(bags):
                continue
            weights = ({n: rng.randint(1, 4) for n in names} if rng.random() < c.p_uneven_prior
                       else dict.fromkeys(names, 1))
            replace, n = rng.random() < 0.5, max(1, r(c.n_draws))
            source = rng.choices(names, weights=[weights[x] for x in names])[0]
            seq = []
            left = dict(bags[source])
            for _ in range(n):
                if not sum(left.values()):
                    break
                col = rng.choices(colors, weights=[left[x] for x in colors])[0]
                seq.append(col)
                left[col] -= 0 if replace else 1
            joint = {x: F(weights[x], sum(weights.values())) * _likelihood(bags[x], seq, replace) for x in names}
            total = sum(joint.values())
            post = sorted(((p / total, x) for x, p in joint.items()), reverse=True)
            if post[0][0] - post[1][0] < c.min_margin:
                continue
            even = len(set(weights.values())) == 1
            prior = ("One bag is picked at random." if even else "A bag is picked with these odds: " +
                     ", ".join(f"bag {x} {weights[x]}" for x in names) + " (relative weights).")
            draw = "each marble is put back before the next draw" if replace else "marbles are not put back"
            state = {"bags": "\n".join(f"Bag {x}: {_stock(bags[x])} marbles." for x in names),
                     "procedure": f"{prior} Then {len(seq)} marble{'s' * (len(seq) > 1)} are drawn from it; {draw}.",
                     "observed": ", ".join(seq) + "."}
            soft = {x: round(float(p), 4) for p, x in post}
            soft[post[0][1]] += round(1 - sum(soft.values()), 4)   # rounding residue on the argmax
            answer = Decision(post[0][1], instructions="Which bag were the marbles drawn from?",
                              criteria=dict.fromkeys(names), soft=soft)
            return Entry({"payload": state, "state_seed": state_seed, "posterior": {x: str(p) for p, x in post},
                          "n_bags": len(names), "replace": replace, "n_draws": len(seq)}, answer)
        raise RuntimeError("hidden_source: no instance with a clear most probable bag")

    def render_prompt(self, m):
        state = m["payload"]
        return (f"{state['bags']}\n{state['procedure']}\nObserved: {state['observed']}\n"
                "Which bag were the marbles drawn from? Answer with the bag letter.")

    def score_answer(self, answer, entry):
        return float(str(answer).strip().rstrip(".").removeprefix("Bag ").removeprefix("bag ").strip().upper()
                     == str(entry.answer))
