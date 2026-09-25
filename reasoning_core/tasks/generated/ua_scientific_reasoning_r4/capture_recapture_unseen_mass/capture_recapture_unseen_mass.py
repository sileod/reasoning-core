import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def chapman_estimate(n1, n2, m):
    return (n1 + 1) * (n2 + 1) // (m + 1) - 1


def overlap_count(a_sorted, b_sorted):
    ia = ib = 0
    n1 = len(a_sorted)
    n2 = len(b_sorted)
    m = 0
    while ia < n1 and ib < n2:
        if a_sorted[ia] == b_sorted[ib]:
            m += 1
            ia += 1
            ib += 1
        elif a_sorted[ia] < b_sorted[ib]:
            ia += 1
        else:
            ib += 1
    return n1, n2, m


@dataclass
class CaptureRecaptureConfig(Config):
    n1_lo: int = 3
    n1_hi: int = 8
    n2_lo: int = 3
    n2_hi: int = 8
    m_lo: int = 2
    pop_cap: int = 220
    id_max: int = 300

    def apply_difficulty(self, level):
        self.n1_lo = 3 + 4 * level
        self.n1_hi = 8 + 12 * level
        self.n2_lo = 3 + 4 * level
        self.n2_hi = 8 + 12 * level
        self.m_lo = 2 + level
        self.pop_cap = 100 + 220 * level
        self.id_max = max(80, 3 * (self.n1_hi + self.n2_hi))


def _gen_counts(cfg):
    while True:
        n1 = random.randint(cfg.n1_lo, cfg.n1_hi)
        n2 = random.randint(cfg.n2_lo, cfg.n2_hi)
        m_hi = min(n1, n2) - 1
        if m_hi < cfg.m_lo:
            continue
        m = random.randint(cfg.m_lo, m_hi)
        n_est = chapman_estimate(n1, n2, m)
        union = n1 + n2 - m
        if n_est < union:
            continue
        if n_est > cfg.pop_cap:
            continue
        return n1, n2, m, n_est


class CaptureRecaptureUnseenMass(Task):
    summary = ("Infer the all-missed population size from two overlapping detection "
               "lists of marks via the Chapman (Lincoln-Petersen family) estimator; "
               "return the integer population estimate.")
    design_choice = ("Present detection lists as sets of marked individuals with overlap "
                     "counts; solvers must derive the unseen count via Lincoln-Petersen or "
                     "Chapman estimators and return the integer population size.")
    config_cls = CaptureRecaptureConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n1, n2, m, n_est = _gen_counts(cfg)
        union = n1 + n2 - m
        ids = random.sample(range(1, cfg.id_max + 1), union)
        overlap_ids = sorted(ids[:m])
        a_only = sorted(ids[m:m + (n1 - m)])
        b_only = sorted(ids[m + (n1 - m):])
        list_a = sorted(overlap_ids + a_only)
        list_b = sorted(overlap_ids + b_only)
        cn1, cn2, cm = overlap_count(list_a, list_b)
        assert (cn1, cn2, cm) == (n1, n2, m), "gold overlap recount failed"
        assert n_est >= cn1 + cn2 - cm, "estimate below visible union"
        assert int(n_est) == n_est and n_est >= 0, "estimate must be a non-negative integer"
        metadata = {
            "list_a": list_a,
            "list_b": list_b,
            "n1": int(cn1),
            "n2": int(cn2),
            "m": int(cm),
        }
        return Entry(metadata=metadata, answer=str(int(n_est)))

    def render_prompt(self, metadata):
        return (
            "Two independent capture rounds were run on a closed population of marked "
            "individuals, and each individual was equally likely to be captured in each "
            "independent round. List 1 contained the individuals "
            f"{{{', '.join(str(x) for x in metadata['list_a'])}}}. List 2 contained the "
            f"individuals {{{', '.join(str(x) for x in metadata['list_b'])}}}. "
            "Under these assumptions, use the Chapman estimator "
            "N = floor((n1+1)(n2+1)/(m+1)) - 1, where n1 is the size of List 1, n2 the size "
            "of List 2, and m the number of individuals appearing in both lists, to estimate "
            "the total population size. What is N? Answer with a single integer."
        )

    def score_answer(self, answer, entry):
        n_est = chapman_estimate(entry.metadata["n1"], entry.metadata["n2"], entry.metadata["m"])
        try:
            parsed = int(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if parsed == n_est else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'capture_recapture_unseen_mass (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/capture_recapture_unseen_mass',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
