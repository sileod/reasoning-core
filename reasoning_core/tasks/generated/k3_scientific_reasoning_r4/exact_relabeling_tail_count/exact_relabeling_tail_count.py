import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'exact_relabeling_tail_count (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/exact_relabeling_tail_count',
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


def _group_size(level):
    return 2 + (level + 1) // 2


def _ranks(scores):
    order = sorted(range(len(scores)), key=lambda i: scores[i])
    r = [0] * len(scores)
    for rank, idx in enumerate(order, start=1):
        r[idx] = rank
    return r


def _tail_count(n, k, observed_sum):
    center = k * (n + 1) / 2.0
    obs_dev = abs(observed_sum - center)
    total = 0
    for combo in itertools.combinations(range(n), k):
        s = sum(combo) + k
        if abs(s - center) >= obs_dev - 1e-12:
            total += 1
    return total


@dataclass
class RelabelTailConfig(Config):
    level: int = 0
    scores_lo: int = -50
    scores_hi: int = 50

    def apply_difficulty(self, level):
        self.level = level


class ExactRelabelingTailCount(Task):
    summary = ("Enumerate all relabelings of a fixed two-group allocation, rank the scores and "
               "recompute the group-A rank sum per arrangement, tally arrangements whose rank sum "
               "is at least as extreme as the observed one, and answer the exact integer tail count "
               "(balanced small groups 2-5 per side over levels 0-6).")
    design_choice = ("Use fixed small group sizes (e.g., 3 vs 3) with all possible relabelings "
                     "enumerated exhaustively, answer as exact integer tail count.")
    config_cls = RelabelTailConfig
    task_version = 2

    def generate_entry(self):
        k = _group_size(self.config.level)
        n = 2 * k
        hi = max(self.config.scores_lo, self.config.scores_hi)
        scores = random.sample(range(self.config.scores_lo, hi), n)
        combo = tuple(sorted(random.sample(range(n), k)))
        observed_sum = int(sum(combo)) + k
        count = _tail_count(n, k, observed_sum)
        n_subsets = 1
        for i in range(1, k + 1):
            n_subsets = n_subsets * (n - k + i) // i
        if not (1 <= count <= n_subsets):
            raise RuntimeError("tail count outside valid range")
        rank = _ranks(scores)
        a_ranks = [rank[i] for i in combo]
        metadata = {
            "group_a_scores": [scores[i] for i in combo],
            "group_b_scores": [scores[i] for i in range(n) if i not in combo],
            "all_scores": scores,
            "ranks": rank,
            "a_ranks": a_ranks,
            "observed_sum": observed_sum,
            "k": k,
            "n_subsets": n_subsets,
            "tail_count": count,
        }
        return Entry(metadata=metadata, answer=str(count))

    def render_prompt(self, metadata):
        a = ", ".join(str(x) for x in metadata["group_a_scores"])
        b = ", ".join(str(x) for x in metadata["group_b_scores"])
        k = metadata["k"]
        n = 2 * k
        center = k * (n + 1) / 2.0
        return (
            f"{n} measured biomarker values belong to two groups, group A ({k} values) and group B "
            f"({k} values). "
            f"Group A holds {a}; group B holds {b}. "
            f"Rank the {n} distinct values from 1 (smallest) to {n} (largest), and take as the "
            f"test statistic the sum of the ranks of the group-A values. "
            f"The observed group-A rank sum is {metadata['observed_sum']}. "
            f"An exact permutation test relabels the groups in every possible way, i.e. for every "
            f"choice of which {k} of the {n} values lie in group A. A relabeling is at least as "
            f"extreme as the observed one when its group-A rank sum deviates from the expected "
            f"rank sum {center:g} at least as much as the observed one does, "
            f"i.e. |rank-sum - {center:g}| >= |{metadata['observed_sum']} - {center:g}|. "
            f"The observed assignment itself counts. "
            f"Count how many such arrangements there are and answer with that single integer."
        )

    def score_answer(self, answer, entry):
        return _score_int_tail(answer, entry)


def _score_int_tail(answer, entry):
    try:
        val = int(str(answer).strip())
    except (TypeError, ValueError):
        return 0.0
    return 1.0 if val == int(entry.metadata["tail_count"]) else 0.0
