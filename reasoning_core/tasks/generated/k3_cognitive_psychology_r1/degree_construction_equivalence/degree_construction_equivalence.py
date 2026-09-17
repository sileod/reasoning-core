import itertools
import random
from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from reasoning_core.template import Config, Entry, Task, render_payload

TASK_META = {'parent_source_id': None,
 'idea': 'degree_construction_equivalence (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_cognitive_psychology_r1/degree_construction_equivalence',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


@dataclass
class DegreeEquivalenceConfig(Config):
    n_counts: int = 4
    n_context: int = 1
    maximum: int = 3

    def apply_difficulty(self, level):
        self.n_counts = 4 + 2 * min(1, int(max(0, level) / 3))
        self.n_context = min(7, 1 + int(max(0, level)))
        self.maximum = min(5, 3 + int(max(0, level) / 3))


def strict_constraints(atom, n):
    kind, a, b, k = atom

    def row(terms, bound):
        coefficients = [0] * n
        for i, coefficient in terms:
            coefficients[i] += coefficient
        return coefficients, bound

    if kind == 'more':
        return [row([(b, 1), (a, -1)], 0)]
    if kind in ('enough', 'gap'):
        return [row([(b, 1), (a, -1)], 1 - k)]
    if kind == 'equal':
        return [row([(a, 1), (b, -1)], 1), row([(b, 1), (a, -1)], 1)]
    if kind == 'too':
        return [row([(a, -1)], -k)]
    if kind == 'threshold':
        return [row([(a, -1)], 1 - k)]
    if kind == 'most':
        return [row([(j, 1), (a, -1)], 0) for j in range(n) if j != a]
    if kind == 'correlative':
        return [row([(b, 1), (a, -1)], 0), row([(b + 1, 1), (a + 1, -1)], 0)]
    raise ValueError(kind)


def meaning(atom, points):
    kind, a, b, k = atom
    if kind == 'more':
        return points[:, a] > points[:, b]
    if kind in ('enough', 'gap'):
        return points[:, a] >= points[:, b] + k
    if kind == 'equal':
        return points[:, a] == points[:, b]
    if kind == 'too':
        return points[:, a] > k
    if kind == 'threshold':
        return points[:, a] >= k
    if kind == 'most':
        return np.all(points[:, a, None] > points[:, [i for i in range(points.shape[1]) if i != a]], axis=1)
    if kind == 'correlative':
        return (points[:, a] > points[:, b]) & (points[:, a + 1] > points[:, b + 1])
    raise ValueError(kind)


@lru_cache(maxsize=8)
def domain(n, maximum):
    points = np.array(list(itertools.product(range(maximum + 1), repeat=n)), dtype=np.int64)
    atoms = []
    for a in range(n):
        for b in range(n):
            if a != b:
                atoms.extend((kind, a, b, 0) for kind in ('more', 'enough', 'equal'))
                atoms.extend(('gap', a, b, k) for k in (1, 2, 3))
        for k in range(1, maximum + 1):
            atoms.extend((kind, a, 0, k) for kind in ('too', 'threshold'))
        atoms.append(('most', a, 0, 0))
    for a in range(0, n, 2):
        for b in range(0, n, 2):
            if a != b:
                atoms.append(('correlative', a, b, 0))
    masks = np.array([meaning(atom, points) for atom in atoms])
    signatures = [np.packbits(mask).tobytes() for mask in masks]
    points.flags.writeable = False
    masks.flags.writeable = False
    return points, atoms, masks, signatures


def wording(atom, labels, alternate=False):
    kind, a, b, k = atom
    x, y = labels[a], labels[b]
    if kind == 'more':
        return f"The {y} count is smaller than the {x} count." if alternate else f"There are more {x} than {y}."
    if kind == 'enough':
        return f"There are at least as many {x} as {y}." if alternate else f"There are enough {x} to match the {y} one for one, with extras allowed."
    if kind == 'gap':
        return f"The {y} count plus {k} is no larger than the {x} count." if alternate else f"There are at least {k} more {x} than {y}."
    if kind == 'equal':
        return f"Neither the {x} count nor the {y} count exceeds the other." if alternate else f"There are exactly as many {x} as {y}."
    if kind == 'too':
        return f"The {x} count exceeds {k}." if alternate else f"There are too many {x} for a container holding at most {k}."
    if kind == 'threshold':
        places = "one place" if k == 1 else f"{k} places"
        return f"The {x} count is no smaller than {k}." if alternate else f"There are enough {x} to fill {places} with one each."
    if kind == 'most':
        if alternate:
            return f"The {x} count exceeds each other listed count."
        return f"The {x} count is the uniquely largest of all listed counts."
    if kind == 'correlative':
        if alternate:
            return f"There are more {x} than {y}, and more {labels[a + 1]} than {labels[b + 1]}."
        return f"From kit {y[0]} to kit {x[0]}: the more beads, the more buttons (both counts strictly increase)."
    raise ValueError(kind)


def check_constraints(atoms, points):
    constraints = [row for atom in atoms for row in strict_constraints(atom, points.shape[1])]
    coefficients, bounds = zip(*constraints)
    return np.all(points @ np.array(coefficients).T < np.array(bounds), axis=1)


def choose_pair(context, masks, signatures, want_yes):
    eligible = np.flatnonzero(np.any(masks[:, context], axis=1) & ~np.all(masks[:, context], axis=1)).tolist()
    groups = {}
    for index in eligible:
        key = np.packbits(masks[index, context]).tobytes()
        groups.setdefault(key, []).append(index)
    if want_yes:
        pairs = [(a, b) for group in groups.values() for a, b in itertools.combinations(group, 2)
                 if signatures[a] != signatures[b]]
        if not pairs:
            return None
        return random.choice(pairs)
    if len(groups) < 2:
        return None
    first, second = random.sample(list(groups.values()), 2)
    return random.choice(first), random.choice(second)


class DegreeConstructionEquivalence(Task):
    summary = "Comparative, superlative, equative, too/enough and correlative degree constructions over stated integer counts; translate to strict order and threshold constraints and answer yes/no whether two wording sets have identical solutions."
    design_choice = "Represent quantities as integer counts and encode each degree construction as a conjunction of strict inequalities; the answer is 'yes' iff the two constraint sets have identical solution sets over the stated domain."
    config_cls = DegreeEquivalenceConfig
    task_version = 3

    def generate_entry(self):
        cfg = self.config
        points, atoms, masks, signatures = domain(cfg.n_counts, cfg.maximum)
        want_yes = random.choice([False, True])
        for _ in range(80):
            witness = random.randrange(len(points))
            valid = np.flatnonzero(masks[:, witness]).tolist()
            context = np.ones(len(points), dtype=bool)
            common = []
            for _ in range(cfg.n_context):
                useful = [i for i in valid if 4 <= np.count_nonzero(context & masks[i]) < np.count_nonzero(context)]
                if not useful:
                    break
                families = sorted({atoms[i][0] for i in useful})
                family = random.choice(families)
                chosen = random.choice([i for i in useful if atoms[i][0] == family])
                common.append(chosen)
                context &= masks[chosen]
            pair = choose_pair(context, masks, signatures, want_yes)
            if pair is None:
                continue
            sides = [common + [pair[0]], common + [pair[1]]]
            random.shuffle(sides)
            for side in sides:
                random.shuffle(side)
            constructions = [[atoms[i] for i in side] for side in sides]
            solutions = [check_constraints(side, points) for side in constructions]
            for side, solution in zip(sides, solutions):
                assert np.array_equal(solution, np.all(masks[side], axis=0))
                assert np.any(solution)
                assert np.all((points[solution] >= 0) & (points[solution] <= cfg.maximum))
            assert bool(np.array_equal(*solutions)) == want_yes
            labels = [f"{chr(65 + i // 2)} {'beads' if i % 2 == 0 else 'buttons'}" for i in range(cfg.n_counts)]
            payload = {f"wording_{name}": "\n".join(wording(atom, labels, random.choice([False, True])) for atom in side)
                       for name, side in zip(('a', 'b'), constructions)}
            return Entry(metadata={'labels': labels, 'maximum': cfg.maximum,
                                   'constructions': constructions, 'payload': payload},
                         answer='yes' if want_yes else 'no')
        raise RuntimeError("No nontrivial equivalence pair found after 80 attempts")

    def render_prompt(self, metadata):
        return (
            "Two editors describe bead-and-button kits. Each listed count independently ranges "
            f"over the integers 0 through {metadata['maximum']}, inclusive: "
            + ", ".join(metadata['labels']) + ". No total or other restrictions apply.\n"
            "Interpret each wording as a conjunction. 'Enough' includes equality; 'too many' "
            "exceeds capacity. 'Uniquely largest' excludes ties and compares all listed counts. "
            "A 'the more ..., the more ...' statement describes only the two strict increases "
            "between its named kits, not causation or a rate of change.\n\n"
            + render_payload(metadata['payload'])
            + "\n\nDo A and B hold for exactly the same assignments over the entire stated domain? "
            "You can check by finite-domain enumeration after translating the comparisons into "
            "strict integer inequalities. Reply yes or no only. For example, equivalent wordings "
            "receive the answer 'yes'; give no explanation."
        )

    def score_answer(self, answer, entry):
        return float(isinstance(answer, str) and answer.strip().lower() == entry.answer)
