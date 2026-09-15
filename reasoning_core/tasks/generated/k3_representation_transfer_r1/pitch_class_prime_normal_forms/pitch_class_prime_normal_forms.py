import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _rotations(pcs):
    pcs = sorted(set(pcs))
    n = len(pcs)
    out = []
    for start in range(n):
        seq = [pcs[(start + i) % n] for i in range(n)]
        seq = [(x - seq[0]) % 12 for x in seq]
        out.append(seq)
    return out


def _prime_form(pcs):
    originals = _rotations(pcs)
    inversions = _rotations(sorted((12 - x) % 12 for x in pcs))
    return sorted(originals + inversions)[0]


def _symmetric(pcs):
    p = set(pcs)
    return p == set((12 - x) % 12 for x in p)


@dataclass
class PrimeFormConfig(Config):
    cardinality_pool: tuple = (3, 4)

    def apply_difficulty(self, level):
        if level <= 1:
            self.cardinality_pool = (3, 4)
        elif level <= 4:
            self.cardinality_pool = (5, 6)
        else:
            self.cardinality_pool = (2, 3, 4, 5, 6, 7, 8)


class PitchClassPrimeNormalForms(Task):
    summary = "Reduce pitch-class sets to normal order and prime form through transposition, inversion, and rotation comparisons, across cardinalities and symmetric special cases; answers are the ascending prime form as a compact pc list."
    design_choice = "Vary difficulty by set cardinality: use only 3- and 4-note sets for easy, 5-6 for medium, and all 2-8 for hard, with symmetric sets (e.g., tritone, augmented triad) appearing only in hard levels."
    config_cls = PrimeFormConfig

    def generate_entry(self):
        while True:
            k = random.choice(self.config.cardinality_pool)
            pcs = sorted(random.sample(range(12), k))
            symmetric = _symmetric(pcs)
            if symmetric and self.config.cardinality_pool in ((3, 4), (5, 6)):
                continue
            pf = _prime_form(pcs)
            start = pf[0]
            if start != 0:
                raise RuntimeError("prime form must start on 0")
            answer = str(pf)
            return Entry(metadata={"pcs": pcs, "prime_form": pf}, answer=answer)

    def render_prompt(self, metadata):
        pcs = metadata["pcs"]
        return (
            f"Given the pitch-class set {pcs} (pitch-class integers 0-11), compute its prime "
            f"form: reduce to normal order, then compare under transposition, inversion, and "
            f"rotation, selecting the most compact ascending form that starts on 0. "
            f"Return the prime form as a list of ascending integers, e.g. [0, 3, 7]. "
            f"Answer for {pcs}:"
        )

    def score_answer(self, answer, entry):
        try:
            parsed = eval(answer.strip())
        except Exception:
            return 0.0
        if not isinstance(parsed, list):
            return 0.0
        if not all(isinstance(x, int) for x in parsed):
            return 0.0
        if len(parsed) != len(entry.metadata["prime_form"]):
            return 0.0
        return 1.0 if parsed == entry.metadata["prime_form"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'pitch_class_prime_normal_forms (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/pitch_class_prime_normal_forms',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
