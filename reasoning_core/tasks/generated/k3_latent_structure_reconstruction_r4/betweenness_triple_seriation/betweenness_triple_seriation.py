import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'betweenness_triple_seriation (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/betweenness_triple_seriation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class BetweennessSeriationConfig(Config):
    n: int = 4
    mode_weights: tuple = (4, 2, 1)  # (multiple, unique, conflict)

    def apply_difficulty(self, level):
        self.n = 5 + min(2, level // 2)
        self.mode_weights = (1, 1, 1)


def _count_orders(n, triples):
    count = 0
    for perm in itertools.permutations(range(n)):
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[a] < pos[b] < pos[c] or pos[c] < pos[b] < pos[a]
               for a, b, c in triples):
            count += 1
    return count


def _consistent_triples(order):
    n = len(order)
    pos = {v: i for i, v in enumerate(order)}
    cons = []
    for combo in itertools.combinations(range(n), 3):
        p = sorted((pos[x], x) for x in combo)
        cons.append((p[0][1], p[1][1], p[2][1]))
    return cons


def _build_unique_subset(n, cons):
    for _ in range(60):
        m = random.randint(max(1, len(cons) - 2), len(cons))
        subset = random.sample(cons, m)
        if _count_orders(n, subset) == 2:
            return subset
    return list(cons)


def _canonical_order(n, triples):
    best = None
    for perm in itertools.permutations(range(n)):
        pos = {v: i for i, v in enumerate(perm)}
        if all(pos[a] < pos[b] < pos[c] or pos[c] < pos[b] < pos[a]
               for a, b, c in triples):
            if best is None or perm < best:
                best = perm
    return best


def _parse_list(s):
    if isinstance(s, (list, tuple)):
        try:
            return tuple(int(x) for x in s)
        except (TypeError, ValueError):
            return None
    s = str(s).strip()
    if not s:
        return None
    try:
        return tuple(int(p.strip()) for p in s.split(','))
    except ValueError:
        return None


def _parse_count(s):
    try:
        return int(str(s).strip())
    except (TypeError, ValueError):
        return None


def _parse_triple(s):
    s = str(s).strip().strip('()')
    try:
        return tuple(int(p.strip()) for p in s.split(','))
    except (TypeError, ValueError):
        return None


class BetweennessTripleSeriation(Task):
    summary = ("Rebuild a line order from betweenness triples by anchoring extremes and "
               "splicing elements into surviving slots; answer the canonical order, the count "
               "of consistent orders, or the first conflicting triple.")
    design_choice = ("Vary the number of given betweenness triples from sparse to dense, "
                     "altering whether the answer is uniquely determined or has multiple "
                     "consistent orders.")
    config_cls = BetweennessSeriationConfig

    def generate_entry(self):
        n = self.config.n
        weights = self.config.mode_weights
        mode = random.choices(['multiple', 'unique', 'conflict'], weights=weights, k=1)[0]

        order = list(range(n))
        random.shuffle(order)
        cons = _consistent_triples(order)

        if mode == 'conflict':
            prefix = _build_unique_subset(n, cons)
            combo = random.choice(list(itertools.combinations(range(n), 3)))
            pos = {v: i for i, v in enumerate(order)}
            p = sorted((pos[x], x) for x in combo)
            lo, mid, hi = p[0][1], p[1][1], p[2][1]
            wrong = (lo, hi, mid)
            triples = prefix + [wrong]
            assert _count_orders(n, prefix) == 2
            assert _count_orders(n, triples) == 0
            return Entry(metadata={'mode': mode, 'n': n, 'triples': triples},
                         answer=f"({wrong[0]},{wrong[1]},{wrong[2]})")

        if mode == 'unique':
            subset = _build_unique_subset(n, cons)
            can = _canonical_order(n, subset)
            assert can is not None
            assert len(can) == n and sorted(can) == list(range(n))
            return Entry(metadata={'mode': mode, 'n': n, 'triples': subset},
                         answer=",".join(str(x) for x in can))

        total = len(cons)
        for _ in range(80):
            k = random.randint(max(1, int(0.25 * total)),
                               max(1, int(0.45 * total)))
            subset = random.sample(cons, k)
            count = _count_orders(n, subset)
            if count > 2:
                assert isinstance(count, int) and count >= 0
                return Entry(metadata={'mode': mode, 'n': n, 'triples': subset},
                             answer=str(count))
        raise RuntimeError('could not build a multiple-consistent instance')

    def render_prompt(self, metadata):
        n = metadata['n']
        mode = metadata['mode']
        elems = ", ".join(str(x) for x in range(n))
        triples = ", ".join(f"({a},{b},{c})" for a, b, c in metadata['triples'])
        if mode == 'multiple':
            return (
                f"There are {n} elements {{{elems}}} laid out on a line. A betweenness triple "
                f"(a,b,c) states that b lies strictly between a and c in the line. You are given "
                f"this list of betweenness triples: [{triples}]. Count how many distinct line "
                f"orders of the {n} elements satisfy every one of these triples, where an order "
                f"and its mirror image count as two different orders. Answer with a single "
                f"integer, the count."
            )
        if mode == 'unique':
            return (
                f"There are {n} elements {{{elems}}} arranged on a line, and a betweenness "
                f"triple (a,b,c) means b lies strictly between a and c. The given triples pin "
                f"the line order down to two mirror-image possibilities. Here they are: "
                f"[{triples}]. Rebuild the line order and write it as a comma-separated list of "
                f"the {n} integers, in the orientation that is lexicographically smallest among "
                f"the two (i.e. the one starting with the smaller leading integer)."
            )
        return (
            f"There are {n} elements {{{elems}}} on a line, where a betweenness triple (a,b,c) "
            f"means b lies strictly between a and c. No single line order satisfies all of the "
            f"given triples because they contradict one another: [{triples}]. Scanning the "
            f"triples in the order they are listed, report the first triple that, combined with "
            f"the ones before it, makes the constraints impossible. Answer exactly as that "
            f"triple in the form (a,b,c)."
        )

    def score_answer(self, answer, entry):
        mode = entry.metadata.mode
        gold = entry.answer
        if mode == 'multiple':
            a = _parse_count(answer)
            g = _parse_count(gold)
            if a is None or g is None:
                return 0.0
            return 1.0 if a == g else 0.0
        if mode == 'unique':
            a = _parse_list(answer)
            g = _parse_list(gold)
            if a is None or g is None or len(a) != len(g):
                return 0.0
            return 1.0 if a == g else 0.0
        a = _parse_triple(answer)
        g = _parse_triple(gold)
        if a is None or g is None or len(a) != 3:
            return 0.0
        return 1.0 if a == g else 0.0
