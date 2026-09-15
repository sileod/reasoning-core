"""Counterfeit weighing deduction.

One of N coins is counterfeit: it is either heavier or lighter than a normal
coin by the same fixed amount. A number of balance-scale weighings were run and
their outcomes recorded (left pan heavier, right pan heavier, or balanced).
A hypothesis is a (coin, sense) pair claiming that specific coin is the
counterfeit with that specific deviation. We keep every hypothesis that predicts
all recorded outcomes; "cH" means coin c is heavier, "cL" means coin c is
lighter. The answer is the full surviving candidate set, sorted.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'counterfeit_weighing_deduction (draw 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/counterfeit_weighing_deduction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Use 3 outcomes per weighing (left, right, balance) and require the solver to output the full candidate set as a sorted list of coin-sense pairs when multiple remain."


def predicted(left, right, coin, dev):
    """Recorded outcome under a (coin, dev) hypothesis.

    dev=+1 means the coin is heavier than normal, dev=-1 lighter. 'L' means the
    left pan is heavier, 'R' the right pan, '=' a balance.
    """
    if coin in left:
        return "L" if dev == 1 else "R"
    if coin in right:
        return "R" if dev == 1 else "L"
    return "="


def candidate_set(n, weighings):
    """All (coin, dev) hypotheses consistent with every recorded weighing."""
    out = []
    for c in range(n):
        for dev in (1, -1):
            if all(predicted(l, r, c, dev) == rec for (l, r, rec) in weighings):
                out.append((c, dev))
    return out


def format_candidates(cands):
    sense = lambda dev: "H" if dev == 1 else "L"
    ordered = sorted(cands, key=lambda cd: (cd[0], 0 if cd[1] == 1 else 1))
    return " ".join(f"{c}{sense(d)}" for (c, d) in ordered)


@dataclass
class CounterfeitConfig(Config):
    n_coins: int = 4
    n_weighings: int = 2

    def apply_difficulty(self, level):
        self.n_coins = 4 + level
        self.n_weighings = 2 + (level // 2)


class CounterfeitWeighingDeduction(Task):
    summary = "Intersect the candidate sets left by each recorded balance-scale outcome: one coin among the suspects is heavier or lighter, pans may tip either way or stay level; answer the guilty coin and sense or the remaining candidates."
    config_cls = CounterfeitConfig

    def generate_entry(self):
        n = self.config.n_coins
        k = self.config.n_weighings
        while True:
            hidden_c = random.randrange(n)
            hidden_d = random.choice((1, -1))
            weighings = []
            for _ in range(k):
                coins = list(range(n))
                random.shuffle(coins)
                ls = random.randrange(1, n)
                rs = random.randrange(1, n - ls + 1)
                left = sorted(coins[:ls])
                right = sorted(coins[ls:ls + rs])
                rec = predicted(left, right, hidden_c, hidden_d)
                weighings.append((left, right, rec))
            cands = candidate_set(n, weighings)
            if cands:
                break
        answer = format_candidates(cands)
        return Entry(
            metadata={
                "n_coins": int(n),
                "n_weighings": int(k),
                "weighings": [
                    {"left": l, "right": r, "outcome": rec}
                    for (l, r, rec) in weighings
                ],
                "hidden": f"{hidden_c}{'H' if hidden_d == 1 else 'L'}",
                "answer": answer,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        n = metadata["n_coins"]
        lines = [
            f"There are {n} coins, numbered 0 to {n - 1}. Exactly one coin is counterfeit: it weighs either slightly more or slightly less than a normal coin. We ran balance-scale weighings comparing the coins on the left pan against the coins on the right pan; 'L' means the left pan was heavier, 'R' means the right pan was heavier, and '=' means they balanced.",
            "Weighings recorded:",
        ]
        for i, w in enumerate(metadata["weighings"]):
            lines.append(
                f"  Weighing {i}: left pan {w['left']}, right pan {w['right']} -> {w['outcome']}"
            )
        lines.append(
            "Give every hypothesis (coin, sense) that is consistent with ALL recorded weighings. Write each candidate as 'cH' for coin c heavier or 'cL' for coin c lighter, separated by spaces, sorted by coin number then sense with 'H' before 'L'. If only one hypothesis remains, output just that one."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        if " ".join(answer.split()) == entry.answer:
            return 1.0
        return 0.0
