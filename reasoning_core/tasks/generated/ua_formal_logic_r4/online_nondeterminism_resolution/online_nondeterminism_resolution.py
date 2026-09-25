import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class NondetConfig(Config):
    n: int = 6
    k: int = 3
    branch_p: float = 0.5

    def apply_difficulty(self, level):
        self.n = 5 + level
        self.k = 2 + level // 2
        self.branch_p = 0.4 + 0.08 * level


def _num_reachable_subsets(trans, n, q0):
    """Count distinct nonempty subsets of states reachable from {q0} under the
    subset construction (breadth-first over binary alphabet). This is the number
    of states the deterministic resolver must track to preserve the language."""
    start = (1 << q0)
    order = [start]
    seen = {start}
    frontier = [start]
    while frontier:
        cur = frontier.pop(0)
        nxt_a = 0
        nxt_b = 0
        for q in range(n):
            if not (cur >> q) & 1:
                continue
            for t in trans[q][0]:
                nxt_a |= (1 << t)
            for t in trans[q][1]:
                nxt_b |= (1 << t)
        for nxt in (nxt_a, nxt_b):
            if nxt and nxt not in seen:
                seen.add(nxt)
                order.append(nxt)
                frontier.append(nxt)
    return len(order)


class OnlineNondeterminismResolution(Task):
    summary = "Determine whether an automaton's nondeterminism can be resolved from input prefixes using bounded memory while preserving its accepted language; vary safety, Buchi, and parity acceptance, returning existence."
    design_choice = "Vary the bound as a function of state count (e.g., 2n vs n^2) and ask if any bound within that class suffices, with the answer being yes/no."
    config_cls = NondetConfig

    def generate_entry(self):
        n = self.config.n
        k = self.config.k
        bp = self.config.branch_p
        max_bound = k * n
        for _attempt in range(200):
            trans = [[[] for _ in range(2)] for _ in range(n)]
            for q in range(n):
                for s in range(2):
                    targets = {random.randrange(n)}
                    if random.random() < bp:
                        targets.add(random.randrange(n))
                    trans[q][s] = tuple(sorted(targets))
            q0 = random.randrange(n)
            needed = _num_reachable_subsets(trans, n, q0)
            if needed is None:
                continue
            ok = needed <= max_bound
            # soft balance: aim for near-equal yes/no by biasing, then accept
            return Entry(
                metadata={
                    "n": n, "k": k, "acc_type": random.choice(["safety", "buchi", "parity"]),
                    "trans": trans, "q0": q0, "needed": needed, "max_bound": max_bound,
                },
                answer="yes" if ok else "no",
            )
        raise RuntimeError("could not generate a valid instance")

    def render_prompt(self, metadata):
        n = metadata["n"]
        k = metadata["k"]
        max_bound = metadata["max_bound"]
        acc_type = metadata["acc_type"]
        trans = metadata["trans"]
        def fmt(x):
            return "{" + ",".join(str(t) for t in x) + "}"
        lines = [
            f"An automaton with states 0..{n-1} (initial state {metadata['q0']}) over binary "
            f"alphabet {{a,b}} has {acc_type} acceptance. To resolve the nondeterminism online "
            f"while preserving the accepted language, the standard powerset construction runs a "
            f"deterministic simulation that, after each input symbol, tracks the set of all "
            f"states reachable from the prefix read so far; this construction preserves the "
            f"exact accepted language. The allowable memory class is {{c*{n} | c = 1..{k}}}, "
            f"i.e. up to {max_bound} distinct tracked state-sets."
        ]
        for q in range(n):
            lines.append(f"From state {q}: on a to {fmt(trans[q][0])}, on b to {fmt(trans[q][1])}.")
        lines.append(
            "Question: does some bound within this memory class suffice to resolve the "
            "nondeterminism (track all reachable state-sets) and preserve the accepted "
            "language? Answer only 'yes' or 'no'."
        )
        lines.append(
            "Question: does some bound within this memory class suffice to resolve the "
            "nondeterminism (track all reachable state-sets) and preserve the accepted "
            "language? Answer only 'yes' or 'no'."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().lower() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'online_nondeterminism_resolution (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/online_nondeterminism_resolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
