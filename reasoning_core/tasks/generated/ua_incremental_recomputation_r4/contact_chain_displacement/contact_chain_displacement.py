import random
from dataclasses import dataclass
from math import gcd

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _reduced_fraction(num, den):
    g = gcd(num, den)
    num //= g
    den //= g
    if den == 1:
        return str(num)
    return f"{num}/{den}"


def _chain_answer(metadata):
    push = metadata["push"]
    gaps = list(metadata["gaps"])
    caps = list(metadata["caps"])
    n = len(caps)
    prefix = [0] * n
    acc = 0
    for i in range(1, n):
        acc += gaps[i - 1]
        prefix[i] = acc

    amount = push
    limiter = None
    for i in range(n):
        if caps[i] < 0:
            continue
        term = caps[i] + prefix[i]
        if term < amount:
            amount = term
            limiter = i

    d = [max(0, amount - prefix[i]) for i in range(n)]
    parts = [_reduced_fraction(d[i], push) for i in range(n)]
    if limiter is not None:
        parts.append(f"S{limiter}")
    return ",".join(parts)


@dataclass
class ContactChainConfig(Config):
    count: int = 3
    max_gap: int = 4
    push_min: int = 4
    push_max: int = 10
    max_cap: int = 4
    cap_prob: float = 0.55

    def apply_difficulty(self, level):
        self.count = 2 + level
        self.max_gap = 3 + level
        self.push_min = 4 + level
        self.push_max = 8 + 2 * level
        self.max_cap = 2 + 2 * level
        self.cap_prob = min(0.85, 0.40 + 0.06 * level)


class ContactChainDisplacement(Task):
    summary = ("Propagate a prescribed quasistatic push through ordered rigid bodies "
               "with varied lengths, gaps, and fixed stops; close gaps before "
               "transmitting motion and return changed positions or the blocking stop.")
    design_choice = ("Answer as a canonical chain of moves: for each body, output its "
                     "net displacement as a fraction of the push distance, with the last "
                     "element being the stop label if blocked.")
    config_cls = ContactChainConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(400):
            n = cfg.count
            push = random.randint(cfg.push_min, cfg.push_max)
            gaps = [random.randint(0, cfg.max_gap) for _ in range(max(0, n - 1))]
            caps = []
            for _ in range(n):
                if random.random() < cfg.cap_prob:
                    caps.append(random.randint(0, cfg.max_cap))
                else:
                    caps.append(-1)

            prefix = [0] * n
            acc = 0
            for i in range(1, n):
                acc += gaps[i - 1]
                prefix[i] = acc

            amount = push
            limiter = None
            for i in range(n):
                if caps[i] < 0:
                    continue
                term = caps[i] + prefix[i]
                if term < amount:
                    amount = term
                    limiter = i

            if limiter is not None:
                mins = [
                    i for i in range(n)
                    if caps[i] >= 0 and caps[i] + prefix[i] == amount
                ]
                if len(mins) != 1:
                    continue

            d = [max(0, amount - prefix[i]) for i in range(n)]
            ok = all(x >= 0 for x in d) and all(
                caps[i] < 0 or d[i] <= caps[i] for i in range(n)
            )
            if not ok:
                continue

            parts = [_reduced_fraction(d[i], push) for i in range(n)]
            if limiter is not None:
                parts.append(f"S{limiter}")
            answer = ",".join(parts)

            metadata = {
                "count": n,
                "gaps": gaps,
                "caps": caps,
                "push": push,
                "displacements": d,
                "blocked": limiter is not None,
                "limiter": limiter,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("contact_chain_displacement: failed to generate instance")

    def render_prompt(self, metadata):
        caps = metadata["caps"]
        n = metadata["count"]
        gap_list = metadata["gaps"]
        push = metadata["push"]

        gap_text = ", ".join(str(g) for g in gap_list) if gap_list else "none"
        stop_parts = []
        for i in range(n):
            if caps[i] >= 0:
                stop_parts.append(f"body {i} stop {caps[i]}")
        stop_text = "; ".join(stop_parts) if stop_parts else "none"

        return (
            f"A horizontal chain of {n} ordered rigid bodies sits left to right, indexed "
            f"0 (far left) through {n - 1}. The initial gap between body i and the body "
            f"to its right is G_i (i = 0 .. {n - 2}). Each body may carry a fixed stop "
            f"S_i, the greatest distance in units it may move right before wedging; a "
            f"body without a listed stop is free to move as far as it is pushed.\n"
            f"\n"
            f"A plane pushes the left face of body 0 by a total distance P = {push} "
            f"(quasistatic gap-closing cascade): the gap to a body's right must fully "
            f"close before motion transmits to the next body, and a body that reaches "
            f"its stop wedges there and blocks the plane. If the plane is blocked before "
            f"traveling the full P, it stops at the blocking body.\n"
            f"\n"
            f"Gaps G_i (left to right): [{gap_text}]\n"
            f"Stops: {stop_text}\n"
            f"P = {push}\n"
            f"\n"
            f"For each body i in index order, output its net displacement as a reduced "
            f"fraction of P, i.e. moves_i / P. If the plane was blocked, append the "
            f"stop label of the blocking body, written S_k for block at body k, as a "
            f"final extra element; if unblocked, list only the {n} fractions.\n"
            f"Answer as comma-separated values, e.g. \"1,1/2\" (two bodies, "
            f"displacements P and P/2, unblocked) or \"1,0,S1\" (two bodies, blocked "
            f"at body 1)."
        )

    def score_answer(self, answer, entry):
        expected = _chain_answer(entry.metadata)
        return 1.0 if str(answer).strip() == expected else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'contact_chain_displacement (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/contact_chain_displacement',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
