import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class ChecksumSchemeConfig(Config):
    pos_count: int = 8
    batch_size: int = 5
    partial_pos: int = 4

    def apply_difficulty(self, level):
        self.pos_count = 5 + self.pos_count_scale(level)
        self.batch_size = 4 + self.batch_scale(level)
        self.partial_pos = self.pos_count - 2

    def pos_count_scale(self, level):
        return level

    def batch_scale(self, level):
        return (level // 2) + 1


CHECK_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _char_to_val(c):
    if c.isdigit():
        return ord(c) - ord("0")
    return ord(c) - ord("A") + 10


def _val_to_char(v):
    return CHECK_CHARS[v]


def _compute_check(digits, weights, modulus):
    total = sum(d * w for d, w in zip(digits, weights)) % modulus
    return (_val_to_char((modulus - (total % modulus)) % modulus))


def _weights(modulus, pos_count):
    return [((i % modulus) + 1) for i in range(pos_count)]


class ChecksumSchemeInference(Task):
    summary = ("Infer a check-digit scheme (position weights cycling from 1 upward, "
               "modulus among {7,9,11,13}) from a batch of valid codes, then return "
               "the check character completing each fresh partial code.")
    design_choice = ("Vary modulus among 7, 9, 11, and 13, with weights cycling from 1 upward; "
                     "solver must test each modulus to fit the batch.")
    config_cls = ChecksumSchemeConfig
    task_version = 2

    def _gen_valid(self, pos_count, modulus):
        digits = [_char_to_val(random.choice(CHECK_CHARS)) for _ in range(pos_count - 1)]
        ck = _compute_check(digits, _weights(modulus, pos_count), modulus)
        return "".join(_val_to_char(d) for d in digits) + ck

    def generate_entry(self):
        modulus = random.choice([7, 9, 11, 13])
        pos_count = self.config.pos_count
        body_len = pos_count - 1
        batch = [self._gen_valid(pos_count, modulus) for _ in range(self.config.batch_size)]
        fresh_vals = [_char_to_val(_val_to_char(random.randrange(modulus))) for _ in range(body_len)]
        fresh = [_val_to_char(v) for v in fresh_vals]
        fresh_code = "".join(fresh)
        ck = _compute_check(fresh_vals, _weights(modulus, pos_count), modulus)
        answer = ck
        idx = None
        # answer must not be readable off the surface
        for i, f in enumerate(fresh):
            if fresh[i] == answer and _val_to_char(_char_to_val(f)) == answer:
                idx = i
        metadata = {
            "modulus": modulus,
            "pos_count": pos_count,
            "batch": batch,
            "partial": fresh_code,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        batch = ", ".join(metadata["batch"])
        return (
            "These are valid codes produced by a single check-digit scheme:\n"
            f"{batch}\n"
            "The scheme assigns each position a weight cycling 1,2,3,... and combines "
            "position-weighted digit values with a modulus that is one of 7, 9, 11, or 13. "
            "A small corporate check runs over the code body (all positions except the last), "
            "taking the character whose position-weighted digit sum makes the total a multiple "
            "of the modulus as the trailing check character.\n"
            f"Given the partial code {metadata['partial']} with the same scheme, what is its "
            "trailing check character?\n"
            "Answer with exactly one character."
        )

    def score_answer(self, answer, entry):
        a = str(answer).strip()
        if not a:
            return 0.0
        gold = entry.answer
        if a == gold:
            return 1.0
        try:
            if len(a) == 1 and _char_to_val(a) == _char_to_val(gold):
                return 1.0
        except Exception:
            pass
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'checksum_scheme_inference (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dependence_relevance_r1/checksum_scheme_inference',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
