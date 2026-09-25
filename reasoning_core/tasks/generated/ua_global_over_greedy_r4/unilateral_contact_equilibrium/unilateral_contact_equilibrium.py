import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'unilateral_contact_equilibrium (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r4/unilateral_contact_equilibrium',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1140349348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

FRICTION_SET = [
    Fraction(1, 4),
    Fraction(1, 3),
    Fraction(2, 3),
    Fraction(3, 4),
    Fraction(1, 1),
    Fraction(3, 2),
    Fraction(2, 1),
]


def _fmt(f):
    if f.denominator == 1:
        return str(f.numerator)
    return "%d/%d" % (f.numerator, f.denominator)


def parse_fraction(s):
    if not isinstance(s, str):
        return None
    t = s.strip()
    if not t:
        return None
    try:
        return Fraction(t)
    except Exception:
        return None


@dataclass
class StackConfig(Config):
    max_blocks: int = 2
    max_weight: int = 4
    max_height: int = 4
    max_halfwidth: int = 3

    def apply_difficulty(self, level):
        self.max_blocks = 2 + level
        self.max_weight = 4 + 3 * level
        self.max_height = 3 + 2 * level
        self.max_halfwidth = 2 + level


class UnilateralContactEquilibrium(Task):
    config_cls = StackConfig
    summary = "Find the largest admissible horizontal load on a stack of rigid blocks held in static equilibrium by unilateral contacts and rational Coulomb friction cones, binding on slip at any interface or tipping of any upper group."

    def generate_entry(self):
        n = random.randint(2, self.config.max_blocks)
        weights = [random.randint(1, self.config.max_weight) for _ in range(n)]
        heights = [random.randint(1, self.config.max_height) for _ in range(n)]
        halfwidth = random.randint(1, self.config.max_halfwidth)
        mu0 = random.choice(FRICTION_SET)
        mus = [random.choice(FRICTION_SET) for _ in range(n - 1)]

        a = halfwidth
        total = sum(weights)
        H = Fraction(sum(heights[:-1])) + Fraction(heights[-1], 2)

        bounds = []
        for j in range(n):
            suffix = sum(weights[j:])
            mu = Fraction(mu0) if j == 0 else Fraction(mus[j - 1])
            slip = mu * suffix
            hsum = sum(heights[:j])
            tip = a * Fraction(suffix) / (H - Fraction(hsum))
            bounds.append(("slip", j, slip))
            bounds.append(("tip", j, tip))

        positive = [b[2] for b in bounds if b[2] > 0]
        if not positive:
            raise RuntimeError("no positive load bound")
        p_max = min(b[2] for b in bounds)
        if p_max <= 0:
            raise RuntimeError("nonpositive admissible load")

        metadata = {
            "n": n,
            "weights": [int(w) for w in weights],
            "heights": [int(h) for h in heights],
            "halfwidth": int(a),
            "mu_ground": _fmt(mu0),
            "mu_interface": [_fmt(m) for m in mus],
            "push_height": _fmt(H),
            "binding": [(_fmt(b[2])) for b in bounds],
        }
        return Entry(metadata=metadata, answer=_fmt(p_max))

    def render_prompt(self, metadata):
        m = metadata
        lines = []
        lines.append(
            "%d rigid rectangular blocks are stacked on a rough horizontal floor. "
            "Every block has half-width a = %d." % (m["n"], m["halfwidth"])
        )
        lines.append(
            "From bottom (block 1) to top, block k has weight W_k = %s and height h_k = %s."
            % (m["weights"], m["heights"])
        )
        lines.append(
            "The floor has static friction coefficient mu_0 = %s; the interface between "
            "block k and block k+1 has friction coefficient mu_k = %s."
            % (m["mu_ground"], m["mu_interface"])
        )
        lines.append(
            "A horizontal load P is applied to the center of the top block. Contacts are "
            "unilateral and friction follows a rational Coulomb cone. Find the largest "
            "load P for which the stack is in static equilibrium: no group of blocks "
            "slips on the surface below it and no upper group of blocks tips about an "
            "edge. Give P as one rational number (integer or fraction)."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = parse_fraction(entry.answer)
        cand = parse_fraction(answer)
        if gold is None or cand is None:
            return 0.0
        return 1.0 if cand == gold else 0.0
