import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'reidemeister_reduction_plan (variant 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_planning_backtracking_r5/reidemeister_reduction_plan',
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


def _bar(a):
    if len(a) > 1 and a.endswith('b'):
        return a[:-1]
    return a + 'b'


def _canon(word):
    """Canonical form of a cyclic, undirected word of strand labels."""
    n = len(word)
    if n == 0:
        return ()
    cands = []
    for k in range(n):
        r = word[k:] + word[:k]
        rr = word[:k][::-1] + word[k:][::-1]
        cands.append(tuple(r))
        cands.append(tuple(rr))
    return min(cands)


def _no_overlap(word, i, j):
    left = word[:i]
    right = word[j + 1:]
    return not (set(left) & set(right))


def _min_reduce(word):
    """Exact minimum number of RI/RII reductions to reach the empty diagram via BFS."""
    start = _canon(word)
    if not start:
        return 0
    from collections import deque
    visited = {start}
    q = deque([(start, 0)])
    depth_cap = 26
    while q:
        s, d = q.popleft()
        if d >= depth_cap:
            continue
        s_list = list(s)
        n = len(s_list)
        options = []
        for i in range(n - 1):
            if s_list[i + 1] == _bar(s_list[i]):
                options.append(i)
        cands = [
            (i, j) for i in range(n) for j in range(i + 1, n)
            if s_list[i] == s_list[j] and _no_overlap(s_list, i, j)
        ]
        for i in options:
            nb = _canon(list(s_list[:i]) + list(s_list[i + 2:]))
            if nb not in visited:
                visited.add(nb)
                if not nb:
                    return d + 1
                q.append((nb, d + 1))
        for i, j in cands:
            nb = _canon([x for k, x in enumerate(s_list) if k != i and k != j])
            if nb not in visited:
                visited.add(nb)
                if not nb:
                    return d + 1
                q.append((nb, d + 1))
    return -1


def _apply_inverse_move(word):
    kind = random.choice(['RI', 'RII'])
    if kind == 'RI':
        n = len(word)
        i = random.randrange(n + 1)
        a = random.choice(['A', 'B', 'Ab', 'Bb'])
        return list(word[:i]) + [a, _bar(a)] + list(word[i:])
    else:
        n = len(word)
        a = random.choice(['A', 'B', 'Ab', 'Bb'])
        positions = sorted(random.sample(range(n + 1), 2))
        out = list(word)
        for p in reversed(positions):
            out.insert(p, a)
        return out


@dataclass
class ReidemeisterConfig(Config):
    base_cycles: list = field(default_factory=lambda: [tuple(['A', 'A'])])
    insertions: int = 2
    budget_slack: int = 3

    def apply_difficulty(self, level):
        if level <= 1:
            self.base_cycles = [tuple(['A', 'A'])]
        elif level <= 3:
            self.base_cycles = [tuple(['A', 'A']), tuple(['A', 'A', 'B'])]
        else:
            self.base_cycles = [tuple(['A', 'A']), tuple(['A', 'A', 'B']), tuple(['A', 'A', 'C'])]
        if level == 0:
            self.insertions = 2
            self.budget_slack = 1
        elif level == 1:
            self.insertions = 3
            self.budget_slack = 2
        elif level == 2:
            self.insertions = 4
            self.budget_slack = 3
        elif level == 3:
            self.insertions = 5
            self.budget_slack = 3
        elif level == 4:
            self.insertions = 6
            self.budget_slack = 4
        else:
            self.insertions = 7
            self.budget_slack = 4


class ReidemeisterReductionPlan(Task):
    summary = "Build cyclic strand words by inverse Reidemeister moves then ask, against a randomized move budget K, whether the BFS-verified minimum reduction to the empty diagram is at most K; balanced yes/no with structural variety."
    config_cls = ReidemeisterConfig
    design_choice = "Instance construction: start from a fixed small knot diagram and generate targets by applying random Reidemeister moves, then ask for the minimum reverse-path length."

    def generate_entry(self):
        for _ in range(80):
            base = random.choice(self.config.base_cycles)
            word = list(base)
            for _stage in range(self.config.insertions):
                word = _apply_inverse_move(word)
            count = _min_reduce(word)
            wlen = len(word)
            if count < 1:
                continue
            if count != wlen // 2:
                continue
            yes = random.random() < 0.5
            if yes:
                delta = random.randrange(0, self.config.budget_slack + 1)
                budget = count + delta
            else:
                delta = random.randrange(1, self.config.budget_slack + 2)
                budget = count - delta
            if budget < 0:
                continue
            return Entry(
                metadata={'word': word, 'length': wlen,
                          'minimum_moves': count, 'budget': budget},
                answer='yes' if yes else 'no',
            )
        raise RuntimeError('failed to generate after bounded attempts')

    def score_answer(self, answer, entry):
        a = str(answer).strip().lower()
        if a not in ('yes', 'no'):
            return 0.0
        gold = 'yes' if entry.metadata['minimum_moves'] <= entry.metadata['budget'] else 'no'
        return 1.0 if a == gold else 0.0

    def render_prompt(self, metadata):
        word = metadata['word']
        budget = metadata['budget']
        return (
            f"A knot diagram is encoded as a cyclic list of labeled strands, where 'Xb' "
            f"is the inverse (reverse crossing) of 'X'. A Reidemeister-I reduction "
            f"collapses an adjacent backtrack pair 'X Xb'. A Reidemeister-II reduction "
            f"collapses two equal strands 'X ... X' provided the strands strictly between "
            f"them share no label with the rest of the diagram. Starting from the diagram "
            f"[{', '.join(word)}], can it be reduced to the empty diagram using at most "
            f"{budget} such reduction moves in total? Respond with a single word."
        )
