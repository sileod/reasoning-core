import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class WeightedVoteRealizationV2Config(Config):
    n_parties: int = 3
    max_weight: int = 6
    quota: int = 4

    def apply_difficulty(self, level):
        self.n_parties = 3 + level
        self.max_weight = 5 + level * 3
        self.quota = None  # decided per-instance in generate_entry


def _bounds(weights, quota, labels):
    n = len(weights)
    lo = [0] * n
    hi = [w for w in weights]
    for i, lab in labels.items():
        if lab in ("min", "win"):
            lo[i] = quota + 1
        elif lab in ("max", "lose"):
            hi[i] = quota
    return lo, hi


def _labels_int(labels):
    """Convert labels dict with string keys to int keys."""
    return {int(k): v for k, v in labels.items()}


def _realizable(weights, quota, labels, target_total):
    labels = _labels_int(labels)
    n = len(weights)
    lo, hi = _bounds(weights, quota, labels)
    if any(lo[i] > hi[i] for i in range(n)):
        return False
    reachable = {0}
    for i in range(n):
        nxt = set()
        for s in reachable:
            for w in range(lo[i], hi[i] + 1):
                nxt.add(s + w)
        reachable = nxt
        if not reachable:
            return False
    return target_total in reachable


def _least_total(weights, quota, labels):
    labels = _labels_int(labels)
    lo, hi = _bounds(weights, quota, labels)
    n = len(weights)
    if any(lo[i] > hi[i] for i in range(n)):
        return None
    return sum(lo)


def _witness(weights, quota, labels):
    labels = _labels_int(labels)
    lo, hi = _bounds(weights, quota, labels)
    if any(lo[i] > hi[i] for i in range(len(weights))):
        return None
    return lo


def _satisfies(weights, quota, labels, witness):
    labels = _labels_int(labels)
    n = len(weights)
    for i in range(n):
        if not (0 <= witness[i] <= weights[i]):
            return False
        if i in labels:
            winning = witness[i] > quota
            want = labels[i] in ("min", "win")
            if winning != want:
                return False
    return True


def _pick_label_mode(level):
    modes = ["complete", "boundary", "partial"]
    return modes[level % 3]


def _canonical_label(n, label_mode):
    if label_mode == "complete":
        k = random.randint(1, n - 1)
        win = set(random.sample(range(n), k))
        return {i: ("min" if i in win else "max") for i in range(n)}
    if label_mode == "boundary":
        k = random.randint(1, n - 1)
        chosen = set(random.sample(range(n), k))
        return {i: random.choice(["min", "max"]) for i in chosen}
    k = random.randint(1, n)
    chosen = set(random.sample(range(n), k))
    return {i: random.choice(["min", "max"]) for i in chosen}


class WeightedVoteRealization(Task):
    summary = "Realize coalition constraints with nonnegative integer weights and one quota; vary complete winning labels, boundary antichains, and partial labels; answer the least total weight or impossibility."
    design_choice = "Answer as a canonical string of the form 'min:<integer>' or 'none', ensuring a fixed parseable format"
    config_cls = WeightedVoteRealizationV2Config

    def generate_entry(self):
        level = self.config.level
        n = self.config.n_parties
        max_w = self.config.max_weight
        label_mode = _pick_label_mode(level)

        for _ in range(300):
            weights = [random.randint(2, max_w) for _ in range(n)]
            labels = _canonical_label(n, label_mode)
            if not labels:
                continue
            wmax = max(weights)
            winners = [i for i, lab in labels.items() if lab in ("min", "win")]
            # Choose a quota. With probability ~0.8 it sits strictly below every
            # winner's capacity (feasible, giving varied minimal totals); the
            # rest force at least one winner beyond capacity -> 'none'.
            if winners and random.random() < 0.8:
                mincap = min(weights[i] for i in winners)
                if mincap <= 1:
                    quota = random.randint(1, wmax)
                else:
                    quota = random.randint(1, mincap - 1)
            else:
                if winners:
                    mincap = min(weights[i] for i in winners)
                    quota = random.randint(mincap, wmax + 1)
                else:
                    quota = random.randint(1, wmax)
            least = _least_total(weights, quota, labels)

            feasible = least is not None
            if feasible:
                witness = _witness(weights, quota, labels)
                if witness is None or not _satisfies(weights, quota, labels, witness):
                    continue
                if not _realizable(weights, quota, labels, least):
                    continue

            if feasible:
                answer = f"min:{least}"
            else:
                answer = "none"

            labels_str = {str(k): v for k, v in labels.items()}

            return Entry(
                metadata={
                    "n_parties": n,
                    "weights_capacity": weights,
                    "quota": quota,
                    "label_mode": label_mode,
                    "labels": labels_str,
                    "least_total": least,
                    "feasible": feasible,
                },
                answer=answer,
            )
        raise RuntimeError("could not generate instance")

    def render_prompt(self, metadata):
        lines = [
            "A coalition has party weight capacities "
            + str(metadata["weights_capacity"])
            + " (the weight of party i may be any nonnegative integer up to its capacity).",
            "A party is winning iff its chosen weight is strictly greater than the quota "
            + str(metadata["quota"])
            + ".",
            "The required labels are: "
            + _format_labels(metadata["labels"], metadata["n_parties"]),
            "Find the least possible sum of all party weights realizing exactly these labels, "
            "or 'none' if impossible. Answer as 'min:<integer>' or 'none'.",
        ]
        return "\n".join(lines)


def _format_labels(labels, n):
    if len(labels) == n:
        parts = [
            f"party {i} is {'winning' if labels[i] in ('min', 'win') else 'losing'}"
            for i in sorted(labels, key=int)
        ]
        return "; ".join(parts) + "."
    if not labels:
        return "none fixed."
    parts = [
        f"party {i} is {'winning' if lab in ('min', 'win') else 'losing'}"
        for i, lab in sorted(labels.items(), key=lambda kv: int(kv[0]))
    ]
    return "; ".join(parts) + "."


def score_realization(answer, entry):
    feasible = entry.metadata["feasible"]
    if not isinstance(answer, str):
        return 0.0
    ans = answer.strip()
    if not feasible:
        return 1.0 if ans == "none" else 0.0
    expected = f"min:{entry.metadata['least_total']}"
    return 1.0 if ans == expected else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'weighted_vote_realization (variant 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/weighted_vote_realization',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
