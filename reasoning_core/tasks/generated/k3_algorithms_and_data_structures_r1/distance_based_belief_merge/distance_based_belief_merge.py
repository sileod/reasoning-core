"""Distance-based belief merging over small propositional bases (trial P003v1)."""

import random
from collections import deque
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'distance_based_belief_merge (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_algorithms_and_data_structures_r1/distance_based_belief_merge',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

RULES = ('sum', 'max', 'lex')
LETTERS = 'ABC'


def _aggregate(rule, dists):
    if rule == 'sum':
        return (sum(dists),)
    if rule == 'max':
        return (max(dists),)
    if rule == 'lex':
        return tuple(sorted(dists, reverse=True))
    raise ValueError('Unknown aggregation rule')


def _min_dist(x, models):
    return min(sum(a != b for a, b in zip(x, m)) for m in models)


def _merged_models(bases, rule):
    n = len(next(iter(bases.values()))[0])
    order = sorted(bases)
    best = None
    winners = []
    for i in range(2 ** n):
        x = format(i, '0%db' % n)
        dists = [_min_dist(x, bases[L]) for L in order]
        key = _aggregate(rule, dists)
        if best is None or key < best:
            best = key
            winners = [x]
        elif key == best:
            winners.append(x)
    return winners


def _verify_gold(bases, rule, winners):
    n = len(next(iter(bases.values()))[0])
    distances = []
    for name in sorted(bases):
        dist = {int(model, 2): 0 for model in bases[name]}
        queue = deque(sorted(dist))
        while queue:
            x = queue.popleft()
            for bit in range(n):
                neighbor = x ^ (1 << bit)
                if neighbor not in dist:
                    dist[neighbor] = dist[x] + 1
                    queue.append(neighbor)
        assert len(dist) == 2 ** n
        distances.append(dist)
    scores = []
    for x in range(2 ** n):
        values = [dist[x] for dist in distances]
        if rule == 'sum':
            score = sum(values)
        elif rule == 'max':
            score = max(values)
        else:
            score = tuple(sorted(values, reverse=True))
        scores.append(score)
    optimum = min(scores)
    expected = [format(x, f'0{n}b') for x, score in enumerate(scores) if score == optimum]
    assert winners == expected
    assert winners and all(len(x) == n and set(x) <= {'0', '1'} for x in winners)


def _canonical(models):
    return ', '.join(sorted(models))


@dataclass
class BeliefMergeConfig(Config):
    num_vars: int = 3
    num_bases: int = 2
    models_per_base: int = 2

    def apply_difficulty(self, level):
        lvl = max(0, level)
        self.num_vars = min(6, 3 + int(lvl) // 2)
        self.num_bases = min(3, 2 + int(lvl) // 3)
        self.models_per_base = min(4, 2 + int(lvl) // 2)


class DistanceBasedBeliefMerge(Task):
    summary = "Merge 2-3 conflicting propositional belief bases with 2-4 models each over 3-6 variables using minimum Hamming distance to each base and sum, max, or descending-sorted lexicographic aggregation; return all aggregate-minimizing models."
    design_choice = "Instances present 2-3 small propositional bases (each with 2-4 models) and a fixed distance metric (e.g., Hamming) with a stated aggregation rule (sum, max, or lexicographic); answers are the set of models minimizing aggregate distance."
    config_cls = BeliefMergeConfig
    task_version = 3

    def generate_entry(self):
        cfg = self.config
        n = cfg.num_vars
        rule = random.choice(RULES)
        for _ in range(200):
            bases = {
                name: sorted(format(x, f'0{n}b') for x in random.sample(
                    range(2 ** n), random.randint(2, cfg.models_per_base)))
                for name in LETTERS[:cfg.num_bases]
            }
            if set.intersection(*(set(models) for models in bases.values())):
                continue
            winners = _merged_models(bases, rule)
            if 0 < len(winners) < 2 ** n:
                break
        else:
            raise RuntimeError('distance_based_belief_merge: could not build instance')
        _verify_gold(bases, rule, winners)
        answer = _canonical(winners)
        assert answer.split(', ') == winners
        return Entry(
            metadata={'num_vars': n, 'bases': bases, 'rule': rule, 'merged': winners},
            answer=answer)

    def render_prompt(self, metadata):
        n = metadata['num_vars']
        names = ', '.join(f'p{i + 1}' for i in range(n))
        lines = [f"Source {name}: {', '.join(metadata['bases'][name])}"
                 for name in sorted(metadata['bases'])]
        rule = metadata['rule']
        if rule == 'sum':
            rule_txt = 'D(x) is the SUM of the distances to all the bases, with equal weights.'
        elif rule == 'max':
            rule_txt = 'D(x) is the MAXIMUM of the distances to all the bases.'
        else:
            rule_txt = (
                'D(x) is the tuple of distances to all the bases sorted from largest to '
                'smallest, minimized lexicographically: at the first unequal component, '
                'smaller wins (for example, (1, 1) beats (2, 0)).')
        example = f"{'0' * (n - 1)}1, 1{'0' * (n - 1)}"
        return (
            f'Merge the beliefs of {len(lines)} sources about {names}. Each source lists '
            'ALL models of its base as bitstrings in this variable order (0=false, 1=true).\n'
            + '\n'.join(lines)
            + f'\nConsider all {2 ** n} length-{n} bitstrings, not just the listed models; '
            'there are no additional constraints. Hamming distance counts differing bit '
            'positions. Distance to a base is the MINIMUM Hamming distance to any of its models. '
            + rule_txt
            + '\nUse exhaustive assignment enumeration to find every model minimizing D(x); '
            'include all ties. Return only the comma-separated bitstrings in increasing '
            f'lexicographic order, without duplicates (format example: {example}).')

    def score_answer(self, answer, entry):
        if not isinstance(answer, str) or not answer.strip():
            return 0.0
        got = [part.strip() for part in answer.strip().split(',')]
        return float(got == entry.answer.split(', '))
