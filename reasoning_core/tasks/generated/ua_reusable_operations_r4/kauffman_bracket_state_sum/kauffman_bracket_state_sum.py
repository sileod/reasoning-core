import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'kauffman_bracket_state_sum (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/kauffman_bracket_state_sum',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class KauffmanBracketStateConfig(Config):
    ncross: int = 4
    nloops: int = 0

    def apply_difficulty(self, level):
        self.ncross = random.randint(2, min(10, 7 + level))
        self.nloops = random.randint(0, min(level + 1, 5))


def kauffman_contribution(a_count, b_count, loops):
    """Contribution of a single smoothing state with `a_count` A-type
    resolutions (factor -A^{-3} each), `b_count` B-type resolutions
    (factor -A^{3} each), and `loops` closed loops (factor
    (-A^2 - A^{-2}) each). Treat each loop as contributing its pure
    monomial part; the state's contribution is the monomial
    (sign) * A^{exponent}."""
    A_exp = -3 * a_count + 3 * b_count + 2 * loops
    coeff = ((-1) ** (a_count + b_count + loops))
    return coeff, A_exp


def monomial_str(coeff, A_exp):
    if coeff == 0:
        return "0"
    c = "" if coeff == 1 else ("-" if coeff == -1 else str(coeff))
    if A_exp == 0:
        if coeff == 1:
            return "1"
        return c if coeff != -1 else "-1"
    e = "" if A_exp == 1 else f"^{A_exp}"
    return f"{c}A{e}"


class KauffmanBracketStateSum(Task):
    summary = "Evaluate the Kauffman bracket of knot and tangle diagrams by summing over local smoothings with loop factors; answers give the bracket polynomial, the contribution of a smoothing choice, or the writhe-corrected normalization."
    config_cls = KauffmanBracketStateConfig
    design_choice = "Ask for the contribution of a single specified smoothing choice (all crossings resolved either A- or B-type) as a product of loop factors and writhe corrections, answer as a monomial in A."

    def generate_entry(self):
        ncross = self.config.ncross
        nloops = self.config.nloops
        a_count = random.randint(0, ncross)
        b_count = ncross - a_count
        coeff, A_exp = kauffman_contribution(a_count, b_count, nloops)
        ans = monomial_str(coeff, A_exp)
        metadata = {
            "ncross": ncross,
            "nloops": nloops,
            "a_count": a_count,
            "b_count": b_count,
        }
        c2, e2 = kauffman_contribution(a_count, b_count, nloops)
        assert monomial_str(c2, e2) == ans
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        n = metadata["ncross"]
        loops = metadata["nloops"]
        a = metadata["a_count"]
        b = metadata["b_count"]
        return (
            f"A tangle diagram has {n} crossings and resolves (when all its loops "
            f"are formed after smoothing) into disjoint simple closed curves, of "
            f"which {loops} arise from a particular smoothing. The Kauffman bracket "
            f"local smoothing rule assigns to each A-type resolution a factor of "
            f"-A^(-3) and to each B-type resolution a factor of -A^(3); each closed "
            f"loop contributes a factor of (-A^2 - A^(-2)). Consider the single "
            f"smoothing state in which exactly {a} of the {n} crossings are resolved "
            f"A-type and {b} are resolved B-type, and this state produces {loops} "
            f"closed loops. Write the contribution of this one smoothing state, "
            f"simplified, as a monomial in A (with integer coefficient, using "
            f"A^0 -> 1 and A^1 -> A). Answer with the monomial only."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip()
        gold = entry.answer
        if norm == gold:
            return 1.0
        # also accept the equivalent monomial spelled as e.g. "1*A" forms, but keep strict to canonical
        return 0.0
