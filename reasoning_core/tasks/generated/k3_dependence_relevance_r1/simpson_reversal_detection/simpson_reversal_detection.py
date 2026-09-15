import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SimpsonConfig(Config):
    strat_count: int = 2
    max_n: int = 40
    min_n: int = 6

    def apply_difficulty(self, level):
        self.strat_count = 2 + level // 2
        self.max_n = 26 + 12 * level


def _dir(a, b):
    if a > b:
        return 1
    if a < b:
        return -1
    return 0


class SimpsonReversalDetection(Task):
    summary = ("Given small integer contingency tables, pooled and per stratum, compute "
               "stratum-specific and overall rates, compare association directions, and decide "
               "whether Simpson reversal occurs, naming the conditioning variable responsible.")
    design_choice = ("Present tables with per-stratum rates already computed, and require the "
                     "solver to only compare direction signs and output the responsible stratum "
                     "variable name.")
    config_cls = SimpsonConfig

    def generate_entry(self):
        strat_count = self.config.strat_count
        max_n = self.config.max_n
        min_n = self.config.min_n
        var_name = random.choice(["site", "center", "ward", "clinic"])

        target = random.choice(["reversal", "none"])

        for _ in range(500):
            a_better = random.choice([1, -1])
            strata = []
            for _s in range(strat_count):
                n1 = random.randint(min_n, max_n)
                n2 = random.randint(min_n, max_n)
                r1 = random.uniform(0.1, 0.9)
                mag = random.uniform(0.05, 0.4)
                r2 = r1 - a_better * mag
                r2 = max(0.03, min(0.97, r2))
                if a_better > 0 and not (r1 > r2):
                    break
                if a_better < 0 and not (r1 < r2):
                    break
                s1 = int(round(r1 * n1))
                s2 = int(round(r2 * n2))
                s1 = max(0, min(n1, s1))
                s2 = max(0, min(n2, s2))
                strata.append((n1, s1, n2, s2))
            else:
                pass
            if len(strata) != strat_count:
                continue

            r1_pool = sum(s1 for (n1, s1, n2, s2) in strata) / sum(n1 for (n1, s1, n2, s2) in strata)
            r2_pool = sum(s2 for (n1, s1, n2, s2) in strata) / sum(n2 for (n1, s1, n2, s2) in strata)
            pooled_dir = _dir(r1_pool, r2_pool)
            if pooled_dir == 0:
                continue

            reversal = (a_better != pooled_dir)

            if target == "reversal" and not reversal:
                continue
            if target == "none" and reversal:
                continue

            overall_pos = sum(s1 + s2 for (n1, s1, n2, s2) in strata)
            overall_n = sum(n1 + n2 for (n1, s1, n2, s2) in strata)

            if reversal:
                answer = var_name
            else:
                answer = "no"

            metadata = {
                "strata": [[n1, s1, n2, s2] for (n1, s1, n2, s2) in strata],
                "group_b_rate": round(r2_pool, 4),
                "group_a_rate": round(r1_pool, 4),
                "overall_rate": round(overall_pos / overall_n, 4),
                "a_better": a_better,
                "var_name": var_name,
                "reversal": reversal,
            }
            return Entry(metadata=metadata, answer=answer)

        raise RuntimeError("could not construct a valid instance after bounded attempts")

    def render_prompt(self, metadata):
        lines = []
        lines.append("Subjects receive one of two treatments, A or B, at several sites. For each "
                     "site the success rate per treatment is already computed for you. A higher "
                     "rate means the treatment is better at that site.")
        for i, (n1, s1, n2, s2) in enumerate(metadata["strata"]):
            lines.append(f"Site {i + 1}: A has {s1} of {n1} successes "
                         f"(rate {round(s1 / n1, 4)}); B has {s2} of {n2} successes "
                         f"(rate {round(s2 / n2, 4)}).")
        lines.append("Pooled over all sites: A has pooled rate "
                     f"{metadata['group_a_rate']}; B has pooled rate "
                     f"{metadata['group_b_rate']}.")
        lines.append("Decide whether the association direction between the treatments within each "
                     "site (which treatment is better) points opposite the direction between the "
                     "pooled treatment rates. When that happens, Simpson's reversal occurs and the "
                     "conditioning site variable is responsible.")
        lines.append("Answer exactly the responsible variable's name if Simpson's reversal occurs, "
                     f"which here would be '{metadata['var_name']}'; otherwise answer exactly "
                     "'no'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = str(entry.answer).strip().lower()
        ans = str(answer).strip().lower()
        return 1.0 if ans == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'simpson_reversal_detection (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dependence_relevance_r1/simpson_reversal_detection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
