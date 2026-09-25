import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'representation_composition_multiplicity (variant 2 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/representation_composition_multiplicity',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 525660630,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

IRREPS = ["T", "S", "E"]
CHARS = {
    "T": (1, 1, 1),
    "S": (1, -1, 1),
    "E": (2, 0, -1),
}
ORDER = 6


def _sym_class(irrep, cls, n):
    """Character value on class cls of the n-th symmetric power of irrep."""
    if irrep in ("T", "S"):
        x = 1 if (irrep == "T" or cls == "s") else (-1 if cls == "t" else 1)
        return x ** n
    if cls == "e":
        return n + 1
    if cls == "t":
        return 1 if n % 2 == 0 else 0
    return [1, -1, 0][n % 3]


def _ext_class(irrep, cls, n):
    """Character value on class cls of the n-th exterior power of irrep."""
    if irrep in ("T", "S"):
        return _sym_class(irrep, cls, n) if n == 1 else 0
    if n == 1:
        return {"e": 2, "t": 0, "s": -1}[cls]
    if n == 2:
        return {"e": 1, "t": -1, "s": 1}[cls]
    return 0


def _power_vec(irrep, n, kind):
    v = []
    for cls in ("e", "t", "s"):
        if kind == "sym":
            v.append(_sym_class(irrep, cls, n))
        else:
            v.append(_ext_class(irrep, cls, n))
    return v


@dataclass
class RepCompositionConfig(Config):
    nlevels: int = 2

    def apply_difficulty(self, level):
        self.nlevels = 2 + level


class RepCompositionMultiplicityV2(Task):
    task_name = "rep_composition_multiplicity"
    summary = ("Resolve nested tensor, symmetric and exterior powers of finite-group "
               "representations into irreducibles using supplied character tables; "
               "return a target multiplicity after global cancellation.")
    design_choice = ("Use a fixed small group (e.g., S3) and vary only the "
                     "representation labels and power exponents, keeping the character "
                     "table constant across instances.")
    config_cls = RepCompositionConfig

    def generate_entry(self):
        levels = self.config.nlevels
        pieces = []
        for _ in range(levels):
            rep = random.choice(IRREPS)
            op = random.choice(["sym", "ext"])
            n = random.randint(2, 5)
            pieces.append((rep, op, n))
        target = random.choice(IRREPS)

        total = [0, 0, 0]
        for rep, op, n in pieces:
            v = _power_vec(rep, n, op)
            total = [total[i] + v[i] for i in range(3)]

        m = _inner_prod(total, target)
        assert m >= 0, (pieces, target, total)
        metadata = {
            "pieces": pieces,
            "target": target,
            "nlevels": levels,
        }
        return Entry(metadata=metadata, answer=str(int(m)))

    def render_prompt(self, metadata):
        lines = []
        lines.append("The symmetric group S3 has three irreducible representations with "
                     "character vectors on (identity, transposition, 3-cycle):")
        lines.append("  T = (1, 1, 1)")
        lines.append("  S = (1, -1, 1)")
        lines.append("  E = (2, 0, -1)")
        lines.append("Class sizes: 1 identity, 3 transpositions, 2 three-cycles.")
        lines.append("The n-th symmetric power Sym^n and exterior power Ext^n are taken "
                     "per conjugacy class from the relevant character value.")
        parts = [f"{'Sym' if op == 'sym' else 'Ext'}^{n}({rep})" for rep, op, n in metadata["pieces"]]
        expr = " + ".join(parts)
        lines.append(f"Compute the multiplicity of {metadata['target']} in the "
                     f"direct sum {expr}. The answer is one non-negative integer.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        try:
            cand = str(int(str(answer).strip()))
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if cand == gold else 0.0


def _inner_prod(v, target):
    t = CHARS[target]
    return (v[0] * t[0] + 3 * v[1] * t[1] + 2 * v[2] * t[2]) // ORDER
