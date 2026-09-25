import random
from collections import defaultdict
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def parse_p(p):
    num, den = p.split("/")
    return int(num) / int(den)


def fmt_frac(x):
    from fractions import Fraction

    return str(Fraction(x).limit_denominator(20))


def classify(rows):
    """rows: list of (x, y, p_or_None). Return MCAR / MAR / MNAR."""
    present = [(x, y, p) for (x, y, p) in rows if p is not None]
    ps = {p for _, _, p in present}
    if len(ps) <= 1:
        return "MCAR"
    groups = defaultdict(set)
    for _, y, p in present:
        groups[y].add(p)
    mar = all(len(g) == 1 for g in groups.values())
    return "MAR" if mar else "MNAR"


@dataclass
class MissingnessConfig(Config):
    level: int = 0
    rich: bool = False
    zero_pool: tuple = (0, 1)
    p_pool: tuple = (25, 50, 75)

    def apply_difficulty(self, level):
        self.level = level
        self.rich = level >= 3
        if level <= 1:
            self.zero_pool = (0, 0, 1, 1, 2)
        elif level <= 3:
            self.zero_pool = (1, 1, 2, 2)
        else:
            self.zero_pool = (1, 2, 2, 2)
        self.p_pool = (20, 25, 33, 40, 50, 60, 67, 75, 80) if not self.rich else (20, 25, 33, 40, 50, 60, 67, 75, 80, 15, 30, 70)


class MissingnessPatternIgnorability(Task):
    summary = "Classify finite missing-data mechanisms by whether each mask probability depends on values visible under that mask; vary structural zeros and realized versus all compatible records; answer the applicable ignorability class."
    design_choice = "Represent each mechanism by a small truth table over all possible full-data records, and ask for the ignorability class (MCAR/MAR/MNAR) with structural zeros marked as impossible records."
    config_cls = MissingnessConfig

    def _build_rows(self):
        combos = [(0, 0), (0, 1), (1, 0), (1, 1)]
        pool = [p / 100 for p in self.config.p_pool]
        for _ in range(300):
            target = random.choice(["MCAR", "MAR", "MNAR"])
            zero_pool = list(self.config.zero_pool)
            if target == "MNAR":
                y = random.randint(0, 1)
                a = random.choice(pool)
                b = random.choice(pool)
                if a == b:
                    continue
                other = [c for c in combos if c[1] != y]
                zc = min(random.choice(zero_pool), len(other), 2)
                zeros = set(random.sample(other, zc))
                pillar = set(random.sample([c for c in combos if c[1] == y], 2))
                rows = []
                for (x, yy) in combos:
                    if (x, yy) in zeros:
                        rows.append((x, yy, None))
                    elif (x, yy) in pillar:
                        rows.append((x, yy, a if x == 0 else b))
                    else:
                        rows.append((x, yy, random.choice(pool)))
            elif target == "MAR":
                p0 = random.choice(pool)
                p1 = random.choice(pool)
                if p0 == p1:
                    continue
                avail = combos
                zc = min(random.choice(zero_pool), len(avail), 2)
                zeros = set(random.sample(avail, zc))
                rows = []
                for (x, yy) in combos:
                    if (x, yy) in zeros:
                        rows.append((x, yy, None))
                    else:
                        rows.append((x, yy, p0 if yy == 0 else p1))
            else:  # MCAR
                pc = random.choice(pool)
                avail = combos
                zc = min(random.choice(zero_pool), len(avail), 2)
                zeros = set(random.sample(avail, zc))
                rows = []
                for (x, yy) in combos:
                    if (x, yy) in zeros:
                        rows.append((x, yy, None))
                    else:
                        rows.append((x, yy, pc))
            present = [(x, y, p) for (x, y, p) in rows if p is not None]
            if len(present) < 2:
                continue
            if classify(rows) == target:
                return rows, target
        raise RuntimeError("could not build a consistent instance")

    def generate_entry(self):
        rows, target = self._build_rows()
        meta_rows = [[x, y, None if p is None else fmt_frac(p)] for (x, y, p) in rows]
        return Entry(metadata={"rows": meta_rows}, answer=target)

    def render_prompt(self, metadata):
        lines = []
        lines.append(
            "There are two binary variables X and Y. X may be missing; Y is always "
            "observed. The table below gives, for every possible full-data record "
            "(X, Y), the probability P that X is observed given that record. A row "
            "marked with \u2014 is a structural zero: that record can never occur, so "
            "no missingness probability applies to it."
        )
        lines.append("")
        lines.append("Class definitions:")
        lines.append("- MCAR: P depends on neither X nor Y.")
        lines.append("- MAR: P depends only on Y (the observed value).")
        lines.append("- MNAR: P depends on X (the missing value) itself, even after accounting for Y.")
        lines.append("")
        lines.append("  X   Y     P")
        for (x, y, p) in metadata["rows"]:
            pcell = "\u2014" if p is None else p
            lines.append(f"  {x}   {y}   {pcell}")
        lines.append("")
        lines.append("What is the missing-data class of this mechanism?")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().lower() == entry.answer.strip().lower() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'missingness_pattern_ignorability (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r4/missingness_pattern_ignorability',
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
