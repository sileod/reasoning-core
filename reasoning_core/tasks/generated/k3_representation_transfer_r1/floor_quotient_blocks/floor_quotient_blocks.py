import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'floor_quotient_blocks (draw 2 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/floor_quotient_blocks',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2072234021,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}

design_choice = ("Given n and a query index i, output the start and end indices of the maximal "
                 "block where floor(n/k) equals floor(n/i), as two space-separated integers.")


@dataclass
class FloorQuotientBlocksConfig(Config):
    min_n: int = 2
    max_n: int = 50

    def apply_difficulty(self, level):
        self.max_n = 50 * (level + 1) ** 3


def _block_span(n, i):
    """Return (start, end) of the maximal k-block where floor(n/k) == floor(n/i)."""
    q = n // i
    start = n // (q + 1) + 1
    end = n // q if q > 0 else n
    return start, end


class FloorQuotientBlocks(Task):
    summary = ("Exploit the few distinct values of floor(n/i): given n and a query index i, "
               "answer the start and end indices of the maximal block of k where "
               "floor(n/k) equals floor(n/i).")
    config_cls = FloorQuotientBlocksConfig
    design_choice = design_choice
    task_version = 2

    def generate_entry(self):
        n = random.randint(self.config.min_n, self.config.max_n)
        i = random.randint(1, n)
        q = n // i
        start, end = _block_span(n, i)

        # Verifier: the returned block must be exactly the maximal constant-quotient block.
        assert n // start == q and n // end == q, "block endpoints must carry the queried quotient"
        if start > 1:
            assert n // (start - 1) != q, "start must be minimal"
        if end < n:
            assert n // (end + 1) != q, "end must be maximal"

        answer = f"{start} {end}"
        return Entry(metadata={"n": n, "i": i, "q": q, "start": start, "end": end},
                     answer=answer)

    def render_prompt(self, metadata):
        return (f"For n = {metadata['n']} and query index i = {metadata['i']}, consider the "
                f"function floor(n/k) for integer k. The values of k where the quotient stays "
                f"equal to floor(n/i) form one maximal contiguous block. Give its first and "
                f"last k as two space-separated integers.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        parts = answer.split()
        if len(parts) != 2:
            return 0.0
        try:
            a, b = int(parts[0]), int(parts[1])
        except ValueError:
            return 0.0
        if (a, b) == (entry["metadata"]["start"], entry["metadata"]["end"]):
            return 1.0
        return 0.0
