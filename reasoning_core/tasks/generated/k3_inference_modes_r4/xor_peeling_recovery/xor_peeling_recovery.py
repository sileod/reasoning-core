"""XOR peeling recovery order task.

Given source symbols s0..s_{n-1} and XOR checks (each check is the XOR of a set of
symbols equalling a bit), the model peels the system l-by-l: whenever a check mentions
exactly one not-yet-recovered symbol, recover it; ties broken by smallest source index.
The answer is the full recovery order.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'xor_peeling_recovery (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_inference_modes_r4/xor_peeling_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def peel_order(supports):
    """Return the deterministic recovery order of symbol indices for XOR peeling.

    ``supports`` is a list of tuples; each tuple is the sorted set of symbol indices
    appearing in one check (the XOR value of a check does not affect the recovery
    order, only its support does). At every step we recover the peelable symbol with
    the smallest index; peelable means some check currently mentions exactly that one
    unrecovered symbol. Recovered symbols are removed from every check they appear in.
    Symbols never recovered simply do not appear in the returned order.
    """
    remaining = [set(sup) for sup in supports]
    recovered = set()
    order = []
    while True:
        peelable = set()
        for sup in remaining:
            if len(sup) == 1:
                u = next(iter(sup))
                if u not in recovered:
                    peelable.add(u)
        if not peelable:
            break
        nxt = min(peelable)
        recovered.add(nxt)
        order.append(nxt)
        for sup in remaining:
            if nxt in sup:
                sup.discard(nxt)
        remaining = [sup for sup in remaining if sup]
    return order


def is_valid_peel_order(supports, order):
    """Independently verify ``order`` is exactly the peeling recovery order.

    Checks that every symbol in ``order`` was peelable at its own step and that, by the
    smallest-index tie-break, it was the peelable symbol with the smallest index at that
    step. Returns True only if the full order is reproducible.
    """
    remaining = [set(sup) for sup in supports]
    recovered = set()
    for s in order:
        peelable = set()
        for sup in remaining:
            if len(sup) == 1:
                u = next(iter(sup))
                if u not in recovered:
                    peelable.add(u)
        if s not in peelable:
            return False
        if min(peelable) != s:
            return False
        recovered.add(s)
        for sup in remaining:
            if s in sup:
                sup.discard(s)
        remaining = [sup for sup in remaining if sup]
    return True


@dataclass
class XORPeelingConfig(Config):
    n_symbols: int = 6
    n_checks: int = 6
    max_degree: int = 3

    def apply_difficulty(self, level):
        self.n_symbols = 5 + level
        self.n_checks = 5 + 2 * level
        self.max_degree = 2 + (level // 2)


class XORPeelingRecovery(Task):
    summary = ("Peel bipartite XOR-check constraints by resolving singleton checks and "
               "substituting recovered bits; answer the recovery order of source symbols, "
               "the kth symbol recovered, or which symbols stall unrecoverable.")
    design_choice = ("Recovery order is the sequence of source symbols as they are peeled, "
                     "with ties broken by smallest source index; answer is that full sequence.")
    config_cls = XORPeelingConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n_symbols
        m = self.config.n_checks
        maxd = self.config.max_degree
        supports = []
        order = []
        for _ in range(400):
            supports = []
            for _ in range(m):
                deg = random.randint(1, maxd)
                symbols = sorted(random.sample(range(n), deg))
                supports.append(tuple(symbols))
            order = peel_order(supports)
            if len(order) >= 2 and is_valid_peel_order(supports, order):
                break
        supports = [tuple(sorted(sup)) for sup in supports]
        order = peel_order(supports)
        checks = []
        for sup in supports:
            value = int(random.randint(0, 1))
            checks.append({"symbols": list(sup), "value": value})
        answer = " ".join("s%d" % i for i in order)
        metadata = {
            "n_symbols": n,
            "checks": checks,
            "order": ["s%d" % i for i in order],
            "recovered": len(order),
            "total": n,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        symbols = ", ".join("s%d" % i for i in range(metadata["n_symbols"]))
        lines = []
        for c in metadata["checks"]:
            expr = " XOR ".join("s%d" % s for s in c["symbols"])
            lines.append("  %s = %d" % (expr, c["value"]))
        checks_block = "\n".join(lines)
        return (
            "There are %d source symbols: %s.\n"
            "There are %d XOR checks, each an equation over some of the symbols:\n"
            "%s\n"
            "Peeling: repeatedly, if a check mentions exactly one not-yet-recovered "
            "symbol, recover that symbol (assign it the check's value and remove it from "
            "every check). Stop when no check mentions exactly one unrecovered symbol. "
            "Whenever several symbols are peelable at once, recover the one with the "
            "smallest index first.\n"
            "Give the recovery order: the symbols in the exact order they are recovered, "
            "separated by single spaces. Do not list any symbol that is never recovered. "
            "Format: s0 s3 s1"
            % (metadata["n_symbols"], symbols, len(metadata["checks"]), checks_block)
        )

    def score_answer(self, answer, entry):
        reference = str(entry.answer)
        return 1.0 if str(answer).strip() == reference else 0.0
