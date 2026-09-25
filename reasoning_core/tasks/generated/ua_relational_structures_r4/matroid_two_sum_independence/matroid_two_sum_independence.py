import random
from dataclasses import dataclass
from itertools import combinations

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'matroid_two_sum_independence (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/matroid_two_sum_independence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Present matroids via explicit basis lists, requiring solvers to "
                 "verify whether a queried subset is contained in any basis of the "
                 "two-sum composition.")


def _binomial(n, r):
    from math import comb
    return comb(n, r)


def _iter_uniform_bases(ground, r):
    ground = sorted(ground)
    for combo in combinations(ground, r):
        yield frozenset(combo)


def _fresh_labels(used):
    base = "abcdefghijklmnopqrstuvwxyz"
    while True:
        for ch in base:
            if ch not in used:
                used.add(ch)
                return ch
        base = [c + ch for c in base for ch in "abcdefghijklmnopqrstuvwxyz"]


def _make_uniform_component(used, n, r):
    labels = [_fresh_labels(used) for _ in range(n)]
    ground = set(labels)
    marked = random.sample(sorted(ground), 1)[0]
    bases = set(_iter_uniform_bases(ground, r))
    return ground, marked, bases


def _two_sum(comp, other):
    p1, b1g = comp[1], comp[0]
    p2, b2g = other[1], other[0]
    new_ground = (comp[0] - {comp[1]}) | (other[0] - {other[1]})
    new_bases = set()
    for ba in comp[2]:
        has_p = comp[1] in ba
        for bb in other[2]:
            has_q = other[1] in bb
            if has_p != has_q:
                new_bases.add((ba - {comp[1]}) | (bb - {other[1]}))
    return new_ground, new_bases


def _build_result(components):
    ground, marked, bases = components[0]
    for comp in components[1:]:
        ground, bases = _two_sum((ground, marked, bases), comp)
        marked = random.sample(sorted(ground), 1)[0]
    return ground, bases


def _sorted_bases(bset):
    return sorted(bset, key=lambda b: "".join(sorted(b)))


def _pick_basis(result_bases):
    return _sorted_bases(result_bases)[random.randrange(len(result_bases))]


def _independent(bset, s):
    for b in bset:
        if s <= b:
            return True
    return False


def _fundamental_circuit(bset, basis, e):
    circ = {e}
    for f in basis:
        cand = (basis - {f}) | {e}
        if cand in bset:
            circ.add(f)
    return frozenset(circ)


@dataclass
class MatroidTwoSumConfig(Config):
    n_components: int = 2
    nmin: int = 3
    nmax: int = 4

    def apply_difficulty(self, level):
        self.n_components = 2 if level < 3 else 3
        self.nmin = 3
        self.nmax = 4 + level // 2


class MatroidTwoSumIndependence(Task):
    summary = ("Determine independence in matroids assembled by nested two-sums along "
               "shared marked elements, with components supplied by rank-uniform basis "
               "lists; answer yes/no whether a queried subset lies in any composed basis.")
    config_cls = MatroidTwoSumConfig

    def generate_entry(self):
        used = set()
        components = []
        for _ in range(self.config.n_components):
            while True:
                n = random.randint(self.config.nmin, self.config.nmax)
                n = min(n, 6)
                r = random.randint(1, n - 1)
                if _binomial(n, r) <= 25:
                    break
            components.append(_make_uniform_component(used, n, r))

        result_ground, result_bases = _build_result(components)
        rank = len(_pick_basis(result_bases))
        ground_sorted = sorted(result_ground)

        yes = random.random() < 0.5
        if yes:
            basis = _pick_basis(result_bases)
            k = random.randint(1, min(rank, len(basis)))
            s = frozenset(random.sample(sorted(basis), k))
            answer = "yes"
        else:
            basis = _pick_basis(result_bases)
            candidates = [e for e in ground_sorted if e not in basis]
            if candidates:
                e = random.choice(candidates)
                s = _fundamental_circuit(result_bases, basis, e)
            else:
                s = set(basis)
                extra = [e for e in ground_sorted if e not in s]
                if extra:
                    s = set(s) | {random.choice(extra)}
                s = frozenset(s)
            answer = "no"

        if answer == "yes":
            assert _independent(result_bases, s)
        else:
            assert not _independent(result_bases, s)

        components_meta = []
        for g, m, b in components:
            components_meta.append({
                "ground": sorted(g),
                "marked": m,
                "bases": [sorted(x) for x in sorted(b, key=lambda x: _sortkey(x))],
            })

        metadata = {
            "components": components_meta,
            "result_ground": ground_sorted,
            "query": sorted(s),
            "answer": answer,
            "rank": int(rank),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        head = ("Two matroids (or a chain of them) are joined by a series two-sum: "
                "the marked element of one is identified with the marked element of the "
                "next, and a set B is a basis of the composition exactly when "
                "B = (B1 - {p1}) | (B2 - {p2}) for bases B1, B2 of the joined pair with "
                "exactly one of them containing its own marked element. Apply that "
                "repeatedly in the given order to form the composed matroid.\n")
        lines = [head]
        for idx, comp in enumerate(metadata["components"]):
            bases_txt = "{" + "; ".join(
                "{" + ",".join(e) + "}" for e in comp["bases"]) + "}"
            lines.append(f"Component {idx + 1}: ground {comp['ground']}, "
                         f"marked element {comp['marked']}, basis set {bases_txt}.")
        query = "{" + ",".join(metadata["query"]) + "}"
        lines.append(f"A subset is independent in a matroid when it is contained in some "
                     f"basis. Is the set {query} contained in some basis of the composed "
                     f"two-sum matroid? Reply with exactly one of the two words.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().lower()
        if norm not in ("yes", "no"):
            return 0.0
        return 1.0 if norm == entry.metadata["answer"] else 0.0


def _sortkey(x):
    return "".join(sorted(x))
