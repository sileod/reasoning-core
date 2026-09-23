"""Stepwise multiple-comparison rejection sets.

We generate n indices 1..n, each with a p-value, and ask which hypotheses a
named stepwise rule rejects at a significance level alpha. Three rules:

  Bonferroni : reject i when p_i <= alpha / n (fixed, non-stepwise).
  Holm       : sort p-values ascending; step k=1..n rejects the k-th smallest
               index while p_(k) <= alpha / (n - k + 1), and stops at the first
               violation.
  Benjamini-Hochberg : sort ascending; reject the k smallest indices where k is
               the largest value satisfying p_(k) <= (k / n) * alpha (step-up).

The answer is the exact rejection set as a sorted list of 1-based hypothesis
indices, with the empty set written as the empty list []. Different rules
produce different thresholds and different cutoffs, so answering correctly
requires actually applying the named rule rather than any single shortcut.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

RULES = ("bonferroni", "holm", "bh")
ALPHAS = (0.01, 0.05, 0.10)


@dataclass
class StepwiseRejectionConfig(Config):
    n: int = 4
    alpha: float = 0.05

    def apply_difficulty(self, level):
        self.n = 4 + level * 2


def _bonferroni(pvals, alpha):
    thr = alpha / len(pvals)
    return [i + 1 for i, p in enumerate(pvals) if p <= thr]


def _holm(pvals, alpha):
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    rejected = []
    for k, idx in enumerate(order, start=1):
        if pvals[idx] <= alpha / (n - k + 1):
            rejected.append(idx + 1)
        else:
            break
    return sorted(rejected)


def _bh(pvals, alpha):
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    largest = 0
    for k in range(n, 0, -1):
        if pvals[order[k - 1]] <= (k / n) * alpha:
            largest = k
            break
    return sorted(order[i] + 1 for i in range(largest))


def _reject(pvals, rule, alpha):
    if rule == "bonferroni":
        return _bonferroni(pvals, alpha)
    if rule == "holm":
        return _holm(pvals, alpha)
    return _bh(pvals, alpha)


class StepwiseRejectionSet(Task):
    summary = ("Apply Bonferroni, Holm, or Benjamini-Hochberg to indexed p-values: order, "
               "compare against position-scaled thresholds, and return the exact rejected "
               "hypothesis set for the named rule.")
    design_choice = ("Return rejection set as a sorted list of hypothesis indices (1-based) "
                     "in ascending order, with empty set as empty list.")
    config_cls = StepwiseRejectionConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n
        alpha = random.choice(ALPHAS)
        thr = alpha / n
        rule = random.choice(RULES)
        pvals = None
        for _ in range(1000):
            active_count = random.randint(1, n)
            active_pos = random.sample(range(n), active_count)
            raw = [
                random.uniform(thr * 0.1, thr * 1.5) if i in active_pos
                else random.uniform(thr * 3.0, 1.0)
                for i in range(n)
            ]
            rounded = [round(p, 4) for p in raw]
            if len(set(rounded)) == n:
                pvals = rounded
                break
            if min(rounded) <= 0.0:
                raise RuntimeError("stepwise: non-positive rounded p-value")
        if pvals is None:
            raise RuntimeError("stepwise: could not build distinct rounded p-values")
        rejected = _reject(pvals, rule, alpha)
        assert all(isinstance(r, int) for r in rejected)
        assert rejected == sorted(rejected)
        assert len(rejected) <= n
        answer = "[%s]" % ", ".join(str(r) for r in rejected)
        metadata = {
            "pvalues": pvals,
            "alpha": alpha,
            "rule": rule,
            "n": n,
            "indexed": list(range(1, n + 1)),
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["n"]
        alpha = metadata["alpha"]
        pairs = ", ".join(
            "H%d: p=%.4f" % (idx, p)
            for idx, p in zip(metadata["indexed"], metadata["pvalues"])
        )
        rule_desc = {
            "bonferroni": "Bonferroni correction (reject i when p_i <= alpha/n)",
            "holm": "Holm step-down procedure (sort ascending; at step k reject the k-th "
                    "smallest while p_(k) <= alpha/(n-k+1), stopping at the first violation)",
            "bh": "Benjamini-Hochberg procedure (sort ascending; reject the k smallest where k "
                  "is the largest value with p_(k) <= (k/n)*alpha)",
        }[metadata["rule"]]
        return (
            f"At significance level alpha = {alpha}, apply the {rule_desc} to the following "
            f"{n} hypotheses and their p-values: {pairs}. "
            f"Give the exact set of rejected hypotheses as a sorted list of 1-based indices in "
            f"ascending order, for example [2, 5]; if none are rejected answer []. "
            f"Report only that list, nothing else."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry)


def _parse(ans):
    if not isinstance(ans, str):
        return None
    s = ans.strip().replace("[", "").replace("]", "").replace(" ", "")
    if s == "":
        return []
    parts = s.split(",")
    out = []
    for p in parts:
        if p == "":
            return None
        try:
            out.append(int(p))
        except ValueError:
            return None
    return out


def _score(answer, entry):
    if not isinstance(answer, str) or answer.strip() == "":
        return 0.0
    gold = _parse(entry.answer)
    resp = _parse(answer)
    if gold is None or resp is None:
        return 0.0
    try:
        return 1.0 if sorted(resp) == sorted(gold) else 0.0
    except TypeError:
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'stepwise_rejection_set (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/stepwise_rejection_set',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
