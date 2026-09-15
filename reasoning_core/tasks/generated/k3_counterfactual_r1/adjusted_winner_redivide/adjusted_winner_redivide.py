import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'adjusted_winner_redivide (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/adjusted_winner_redivide',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Vary perturbation by multiplying each item's value for each agent by a "
                 "random factor in [0.5, 1.5], then re-normalize total values per agent to 100; "
                 "final fractions are exact rationals.")


@dataclass
class AdjustedWinnerRedivideConfig(Config):
    count: int = 5

    def apply_difficulty(self, level):
        self.count = 5 + level


def _fmt(x):
    return f"{x.numerator}/{x.denominator}"


def _adjusted_winner(a, b):
    """Return final fraction of each good held by Agent A under Adjusted Winner.

    a[i], b[i] are Fractions (each agent's valuation of good i, both agents summed
    to 100). Returns a list of Fractions f[i] in [0,1], the share of good i held by
    A; the resulting point totals of A and B are equal (equitability).
    """
    n = len(a)
    f = []
    for i in range(n):
        if a[i] > b[i]:
            f.append(Fraction(1))
        elif a[i] < b[i]:
            f.append(Fraction(0))
        else:
            f.append(Fraction(1, 2))

    def a_tot():
        return sum(a[i] * f[i] for i in range(n))

    def b_tot():
        return sum(b[i] * (1 - f[i]) for i in range(n))

    if a_tot() == b_tot():
        return f

    if a_tot() > b_tot():
        richer = 'A'
        inds = sorted([i for i in range(n) if a[i] > b[i]], key=lambda i: a[i] / b[i])
    else:
        richer = 'B'
        inds = sorted([i for i in range(n) if a[i] < b[i]], key=lambda i: a[i] / b[i],
                      reverse=True)

    for j in inds:
        diff = abs(a_tot() - b_tot())
        if diff == 0:
            break
        q = diff / (a[j] + b[j])
        if q >= 1:
            f[j] = Fraction(0) if richer == 'A' else Fraction(1)
            continue
        if richer == 'A':
            f[j] = Fraction(1) - q
        else:
            f[j] = q
        break

    ta, tb = a_tot(), b_tot()
    assert ta == tb, "Adjusted Winner must equalize point totals"
    assert all(Fraction(0) <= x <= Fraction(1) for x in f), "fractions must lie in [0,1]"
    return f


class AdjustedWinnerRedivide(Task):
    summary = ("Divide divisible goods between two agents by ratio-ordered transfer that "
               "equalizes point totals; perturb valuations by per-agent factors in [0.5,1.5] "
               "renormalized to 100, answering Agent A's exact rational fractions per item and "
               "the common equalized score.")
    config_cls = AdjustedWinnerRedivideConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.count
        while True:
            base_a = [Fraction(random.randint(1, 10)) for _ in range(n)]
            base_b = [Fraction(random.randint(1, 10)) for _ in range(n)]
            fa = [Fraction(random.randint(50, 150), 100) for _ in range(n)]
            fb = [Fraction(random.randint(50, 150), 100) for _ in range(n)]
            pa = [base_a[i] * fa[i] for i in range(n)]
            pb = [base_b[i] * fb[i] for i in range(n)]
            ta = sum(pa)
            tb = sum(pb)
            if ta == 0 or tb == 0:
                continue
            a = [x * 100 / ta for x in pa]
            b = [y * 100 / tb for y in pb]
            if any(a[i] == b[i] for i in range(n)):
                continue
            break

        f = _adjusted_winner(a, b)
        score = sum(a[i] * f[i] for i in range(n))
        assert score == sum(b[i] * (1 - f[i]) for i in range(n)), "scores must be equal"

        fracA = [_fmt(x) for x in f]
        score_s = _fmt(score)

        answer = "\n".join(fracA) + f"\nscore {score_s}"
        return Entry(metadata={
            "count": n,
            "valA": [_fmt(x) for x in a],
            "valB": [_fmt(x) for x in b],
            "score": score_s,
            "fracA": fracA,
        }, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["count"]
        lines = []
        for i in range(n):
            lines.append(f"Good {i + 1}: A={metadata['valA'][i]}, B={metadata['valB'][i]}")
        goods = "\n".join(lines)
        return (
            "Two agents, A and B, divide divisible goods using the Adjusted Winner procedure "
            "(Brams-Taylor): each good is assigned to the agent whose ratio "
            "(A's valuation / B's valuation) is higher, then goods are transferred one at a "
            "time, possibly fractionally, from the agent with the higher point total to the "
            "other, starting with the good whose advantage ratio is closest to 1, until both "
            "agents reach the same point total. Each agent's total valuation is normalized to "
            "100.\n\n"
            f"Valuations of {n} goods (A / B):\n{goods}\n\n"
            "Report the Adjusted Winner outcome: the fraction of each good held by Agent A, one "
            "fraction per line in the order the goods are listed, then a line 'score <p/q>' with "
            "the common equalized point total shared by both agents. Fractions are exact "
            "rationals. Worked format example (a different instance):\n"
            "3/4\n1/1\nscore 289/4"
        )

    def score_answer(self, answer, entry):
        try:
            text = str(answer).strip()
        except Exception:
            return 0
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if len(lines) < 2:
            return 0
        if not lines[-1].startswith("score "):
            return 0
        try:
            score = Fraction(lines[-1][len("score "):].strip())
        except Exception:
            return 0
        try:
            gold_score = Fraction(entry.metadata["score"])
        except Exception:
            return 0
        if score != gold_score:
            return 0

        try:
            fracs = [Fraction(ln) for ln in lines[:-1]]
        except Exception:
            return 0
        try:
            gold = [Fraction(x) for x in entry.metadata["fracA"]]
        except Exception:
            return 0
        if fracs != gold:
            return 0
        return 1.0
