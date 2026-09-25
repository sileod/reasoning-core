import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'likelihood_sufficient_partition (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_state_tracking_r4/likelihood_sufficient_partition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Instances present 5 hypotheses and 10 outcomes; solver must output a partition of outcomes into minimal classes where likelihood vectors are scalar multiples, with answer as a canonical list of class labels per outcome.")


@dataclass
class LikelihoodPartitionConfig(Config):
    num_hypotheses: int = 5
    num_outcomes: int = 10
    level: int = 0
    max_classes: int = 5

    def apply_difficulty(self, level):
        self.level = level
        self.num_outcomes = 10 + 2 * level
        self.max_classes = min(5 + level, self.num_outcomes - 1)


def _gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def _normalize(veclist):
    g = 0
    for v in veclist:
        g = _gcd(g, v)
    if g == 0:
        return tuple(veclist)
    return tuple(v // g for v in veclist)


def _classes_for(vectors):
    labels = {}
    order = []
    for vec in vectors:
        key = _normalize(list(vec))
        if key not in labels:
            labels[key] = len(order)
            order.append(key)
    class_labels = [labels[_normalize(list(v))] for v in vectors]
    return class_labels, labels


class LikelihoodSufficientPartition(Task):
    summary = "Group outcomes whose positive likelihood vectors across fixed hypotheses are scalar multiples; output minimal first-occurrence class labels, with variable outcome counts and class-splits, preserving every posterior."
    config_cls = LikelihoodPartitionConfig

    def generate_entry(self):
        cfg = self.config
        n_h = cfg.num_hypotheses
        n_o = cfg.num_outcomes
        attempts = 0
        while True:
            attempts += 1
            if attempts > 200:
                raise RuntimeError("could not build a valid instance")
            k = random.randint(2, cfg.max_classes)
            bases = set()
            while len(bases) < k:
                bases.add(_normalize([random.randint(1, 12) for _ in range(n_h)]))
            base_vecs = sorted(bases)
            assign = list(range(k)) + [random.randrange(k) for _ in range(n_o - k)]
            random.shuffle(assign)
            feats = []
            for c in assign:
                sc = random.randint(1, 6)
                feats.append([x * sc for x in base_vecs[c]])
            class_labels, labels = _classes_for(feats)
            if len(labels) != k:
                continue
            gold = ",".join(str(x) for x in class_labels)
            break
        metadata = {
            "features": [[int(x) for x in v] for v in feats],
            "num_classes": len(labels),
            "num_outcomes": n_o,
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        feats = metadata["features"]
        n_o = len(feats)
        lines = "\n".join(
            f"Outcome o{i + 1}: " + " ".join(str(x) for x in feats[i])
            for i in range(n_o)
        )
        nh = len(feats[0])
        return (
            f"There are {nh} hypotheses h1..h{nh}. Each of the {n_o} outcomes o1..o{n_o} "
            "has a likelihood vector of positive integers, one entry per hypothesis "
            "(relative unnormalized likelihoods). Two outcomes are in the same minimal "
            "sufficient class when their likelihood vectors are scalar multiples of each "
            "other (proportional), so that grouping them loses no posterior information. "
            f"Output the minimal partition as a comma-separated list of {n_o} class "
            "labels, one per outcome, labelling classes by first occurrence (o1's class "
            "is label 0, then each new class gets the next integer in order of first "
            f"appearance).\n\n{lines}"
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        parsed = answer.strip().replace(" ", "")
        return 1.0 if parsed == entry.answer else 0.0
