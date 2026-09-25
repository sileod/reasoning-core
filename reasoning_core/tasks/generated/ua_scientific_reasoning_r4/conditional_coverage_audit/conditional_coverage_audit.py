import random
import re
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'conditional_coverage_audit (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/conditional_coverage_audit',
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
class CoverageConfig(Config):
    min_strata: int = 2
    max_strata: int = 2
    min_size: int = 2
    max_size: int = 3
    adv_lo: int = 50
    adv_hi: int = 95

    def apply_difficulty(self, level):
        self.min_strata = 2
        self.max_strata = 2 + (level + 1) // 2
        self.min_size = 2
        self.max_size = 3 + level
        self.adv_lo = 50
        self.adv_hi = 95 if level < 4 else 99


def _render_set(members):
    members = sorted(members)
    return "{" + ",".join(str(m) for m in members) + "}"


def _parse_answer(answer):
    if not isinstance(answer, str):
        return None
    frac_match = re.search(r"coverage:\s*\[([^\]]*)\]", answer)
    fail_match = re.search(r"failing:\s*\[([^\]]*)\]", answer)
    if not (frac_match and fail_match):
        return None
    fracs = []
    for token in frac_match.group(1).split(","):
        token = token.strip()
        if not token:
            continue
        try:
            fracs.append(Fraction(token))
        except (ValueError, ZeroDivisionError):
            return None
    failing = []
    for token in fail_match.group(1).split(","):
        token = token.strip()
        if not token:
            continue
        try:
            failing.append(int(token))
        except ValueError:
            return None
    return fracs, sorted(failing)


class ConditionalCoverageAudit(Task):
    summary = ("Evaluate confidence procedures on finite sampling spaces under ancillary "
               "strata, stopping events, and reported-width subsets; return conditional "
               "coverage and the subsets where advertised coverage fails.")
    design_choice = ("Instances specify sampling space, strata, stopping rule, and "
                     "advertised coverage as integers; solver returns per-stratum "
                     "coverage as a list of fractions and failing strata indices.")
    config_cls = CoverageConfig

    def generate_entry(self):
        cfg = self.config
        k_count = random.randint(cfg.min_strata, cfg.max_strata)
        advertised = random.randint(cfg.adv_lo, cfg.adv_hi)
        a = advertised
        sizes = [random.randint(cfg.min_size, cfg.max_size) for _ in range(k_count)]

        strata_truth = []
        strata_sets = []
        covered_counts = []
        fracs = []
        failing = []
        for idx in range(k_count):
            n = sizes[idx]
            stratum = idx + 1
            want_fail = random.random() < 0.5
            if want_fail:
                c_max = max(0, (a * n - 1) // 100)
                c_max = min(c_max, n)
                c = random.randint(0, c_max)
            else:
                c = n
            assert 0 <= c <= n, "covered count must lie within the stratum size"

            truths = []
            sets = []
            for i in range(n):
                t = random.randint(0, 1)
                truths.append(t)
                if i < c:
                    if random.random() < 0.4:
                        sets.append(_render_set([0, 1]))
                    else:
                        sets.append(_render_set([t]))
                else:
                    sets.append(_render_set([1 - t]))
            strata_truth.append(truths)
            strata_sets.append(sets)
            covered_counts.append(c)

            cov = Fraction(c, n)
            assert 0 <= cov <= 1, "coverage fraction must lie in [0, 1]"
            fracs.append(cov)
            if cov < Fraction(a, 100):
                failing.append(stratum)

        coverage_str = ", ".join(str(f) for f in fracs)
        failing_str = ", ".join(str(i) for i in failing)
        answer = "coverage: [%s]; failing: [%s]" % (coverage_str, failing_str)

        metadata = {
            "advertised_coverage_pct": advertised,
            "strata_truth": strata_truth,
            "strata_sets": strata_sets,
            "covered_counts": covered_counts,
            "sizes": sizes,
            "failing_indices": failing,
            "per_stratum_coverage": [str(f) for f in fracs],
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        a = metadata["advertised_coverage_pct"]
        blocks = []
        for idx, (truths, sets) in enumerate(
                zip(metadata["strata_truth"], metadata["strata_sets"]), start=1):
            truth_str = "[" + ",".join(str(t) for t in truths) + "]"
            set_str = "[" + ",".join(sets) + "]"
            blocks.append("Stratum %d: true=%s sets=%s" % (idx, truth_str, set_str))
        body = "\n".join(blocks)
        return (
            "This is a finite-sample confidence audit. The sampling space is split into "
            "ancillary strata. Every point carries a true binary value (0 or 1) and a "
            "reported confidence set (a singleton such as {0} or the full set {0,1}); "
            "the reported set covers the point exactly when the true value is a member, "
            "and short reported sets are the stopping-event/reported-width subset that "
            "can break coverage. Advertised coverage A is an integer percentage: each "
            "stratum must cover at least A%% of its own points. For every stratum compute "
            "its conditional coverage = (points in it that are covered by their reported "
            "set) / (points in it), and list every stratum whose coverage is strictly "
            "below A%%. Advertised coverage: %d%%.\n%s\n"
            "Report the answer as exactly: coverage: [c1/n1, c2/n2, ...]; failing: [i1, i2, ...] "
            "with every fraction reduced and stratum indices 1-based and ascending "
            "(no failing strata -> failing: [])." % (a, body)
        )

    def score_answer(self, answer, entry):
        gold = _parse_answer(entry.answer)
        cand = _parse_answer(answer)
        if gold is None or cand is None:
            return 0.0
        if gold[0] == cand[0] and gold[1] == cand[1]:
            return 1.0
        return 0.0
