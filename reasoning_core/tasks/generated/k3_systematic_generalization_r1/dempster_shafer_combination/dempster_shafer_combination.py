import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround

LETTERS = ["A", "B", "C"]

FOCAL = []
for _mask in range(1, 8):
    FOCAL.append(tuple(LETTERS[i] for i in range(3) if _mask & (1 << i)))


def _fmt_set(s):
    return "{" + ",".join(s) + "}"


def _frac_text(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _parse_frac(s):
    try:
        s = str(s).strip()
        if "/" in s:
            n, d = s.split("/", 1)
            return Fraction(int(n), int(d))
        return Fraction(int(s))
    except Exception:
        return None


def _distribution(total, min_pos):
    counts = [0] * 7
    bins = list(range(7))
    random.shuffle(bins)
    for i in range(min_pos):
        counts[bins[i]] = 1
    for _ in range(total - min_pos):
        counts[random.randrange(7)] += 1
    return counts


def _combine(c1, c2):
    pooled = {}
    conflict = 0
    for s, a in c1.items():
        for t, b in c2.items():
            inter = tuple(x for x in s if x in t)
            p = a * b
            if inter:
                pooled[inter] = pooled.get(inter, 0) + p
            else:
                conflict += p
    return pooled, conflict


@dataclass
class DempsterShaferConfig(Config):
    denominator: int = 4
    min_focal: int = 2
    max_attempts: int = 500

    def apply_difficulty(self, level):
        self.denominator = 4 + level
        self.min_focal = 2 + (level // 3)


class DempsterShaferCombination(Task):
    summary = ("Combine two mass assignments over a 3-hypothesis frame with focal sets drawn "
               "from all nonempty subsets and masses as integer fractions summing to 1, by "
               "intersecting focal sets pairwise and pooling products, then either normalizing "
               "to report the combined mass of a queried set or reporting the conflict mass.")
    design_choice = ("Frame size fixed at 3 hypotheses, with focal sets drawn from all nonempty "
                     "subsets and masses as integer fractions summing to 1.")
    config_cls = DempsterShaferConfig

    def generate_entry(self):
        cfg = self.config
        D = cfg.denominator
        for _ in range(cfg.max_attempts):
            c1c = _distribution(D, cfg.min_focal)
            c2c = _distribution(D, cfg.min_focal)
            c1 = {FOCAL[i]: c1c[i] for i in range(7) if c1c[i] > 0}
            c2 = {FOCAL[i]: c2c[i] for i in range(7) if c2c[i] > 0}
            pooled, conflict = _combine(c1, c2)
            variant = random.choice(["combine", "conflict"])
            query = None
            if variant == "conflict":
                if conflict == 0:
                    continue
                ans = Fraction(conflict, D * D)
            else:
                pos = [u for u, cnt in pooled.items() if cnt > 0]
                norm = D * D - conflict
                if not pos or norm <= 0:
                    continue
                query = random.choice(pos)
                ans = Fraction(pooled[query], norm)
            if not Fraction(0) <= ans <= Fraction(1):
                continue
            ordered1 = sorted(c1.items(), key=lambda kv: FOCAL.index(kv[0]))
            ordered2 = sorted(c2.items(), key=lambda kv: FOCAL.index(kv[0]))
            metadata = edict(
                variant=variant,
                query=_fmt_set(query) if query else None,
                m1=[[_fmt_set(s), _frac_text(Fraction(c, D))] for s, c in ordered1],
                m2=[[_fmt_set(s), _frac_text(Fraction(c, D))] for s, c in ordered2],
                answer=_frac_text(ans),
            )
            return Entry(metadata=metadata, answer=_frac_text(ans))
        raise RuntimeError("DempsterShaferCombination: failed to generate an admissible instance")

    def render_prompt(self, metadata):
        lines = ["The hypotheses are A, B, and C over the frame {A, B, C} in Dempster-Shafer theory."]
        lines.append("Two mass assignments m1 and m2 are given; each mass is an integer fraction "
                     "and each assignment's masses sum to 1.")
        lines.append("Combination rule: for every focal set S of m1 and every focal set T of m2, "
                     "pool the product m1(S)*m2(T) at their intersection S and T. Products whose "
                     "intersection is empty accumulate into the conflict mass. The normalized "
                     "combined mass of a set U is its pooled product divided by (1 - conflict).")
        for label, m in (("m1", metadata.m1), ("m2", metadata.m2)):
            lines.append(f"Mass assignment {label}:")
            for s, v in m:
                lines.append(f"  m({s}) = {v}")
        if metadata.variant == "conflict":
            lines.append("What is the conflict mass, i.e. the total product pooled at the empty "
                         "intersection? The answer is a single reduced fraction such as 3/8 or "
                         "1/2, or an integer like 1 for mass 1/1.")
        else:
            lines.append(f"What is the normalized combined mass assigned to the set "
                         f"{metadata.query}? The answer is a single reduced fraction such as 3/8 "
                         f"or 1/2, or an integer like 1 for mass 1/1.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ref = _parse_frac(entry.metadata.answer)
        got = _parse_frac(answer)
        if ref is None or got is None:
            return 0.0
        return 1.0 if got == ref else 0.0

    def balancing_key(self, problem):
        return str(problem.answer)


TASK_META = {'parent_source_id': None,
 'idea': 'dempster_shafer_combination (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/dempster_shafer_combination',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
