import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'masked_stencil_identification (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_interacting_updates_r4/masked_stencil_identification',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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

MASK = '?'


@dataclass
class MaskedStencilConfig(Config):
    radius: int = 1
    alphabet: int = 2
    runs: int = 2
    rows: int = 5
    cols: int = 7
    mask_prob: float = 0.3

    def apply_difficulty(self, level):
        self.radius = 1 + (level >= 3)
        self.alphabet = 2 + (level >= 4)
        self.runs = _sround(2 + level * 0.6)
        self.rows = _sround(5 + level * 0.9)
        self.cols = _sround(7 + level * 1.0)
        self.mask_prob = 0.25 + 0.04 * level


def _sround(value):
    return int(value) + (1 if random.random() < (value - int(value)) else 0)


def _window_index(nbhd, base):
    idx = 0
    for i, d in enumerate(nbhd):
        idx += int(d) * (base ** i)
    return idx


def _render_grid(grid):
    return '\n'.join(''.join(str(c) if c is not None else MASK for c in row) for row in grid)


def _parse_answer(answer):
    entries = {}
    for tok in str(answer).strip().split():
        if not tok:
            continue
        left, right = tok.split(':')
        entries[int(left)] = int(right)
    return entries


class MaskedStencilIdentification(Task):
    summary = ("Sparse space-time patches from several runs share an unknown "
               "finite-neighborhood update rule; vary boundaries, alphabets, "
               "and missing states, and recover rule entries forced across "
               "all completions.")
    design_choice = ("Present patches as fixed masked grids over a shared "
                     "global timeline, where the answer is the canonical "
                     "list of rule entries sorted by neighborhood vector.")
    config_cls = MaskedStencilConfig
    task_version = 2

    def generate_entry(self):
        base = self.config.alphabet
        r = self.config.radius
        W = 2 * r + 1
        nbhd_counts = base ** W

        rule = {}
        for idx in range(nbhd_counts):
            nbhd = tuple((idx // (base ** i)) % base for i in range(W))
            rule[nbhd] = random.randrange(base)

        patches = []
        observed = {}
        for _ in range(self.config.runs):
            cols = self.config.cols
            grid = [[random.randrange(base) for _ in range(cols)]]
            for t in range(1, self.config.rows):
                prev = grid[-1]
                nxt = []
                for x in range(cols):
                    if x < r or x >= cols - r:
                        nxt.append(random.randrange(base))
                    else:
                        nbhd = tuple(prev[x - r + i] for i in range(W))
                        nxt.append(rule[nbhd])
                grid.append(nxt)

            masked = [
                [c if random.random() >= self.config.mask_prob else None for c in row]
                for row in grid
            ]
            for t in range(self.config.rows - 1):
                for x in range(r, cols - r):
                    window = masked[t][x - r:x + r + 1]
                    succ = masked[t + 1][x]
                    if succ is None or any(v is None for v in window):
                        continue
                    nbhd = tuple(window)
                    idx = _window_index(nbhd, base)
                    observed[idx] = rule[nbhd]
            patches.append(masked)

        assert observed, "no forced transitions observed"
        for idx, val in observed.items():
            nbhd = tuple((idx // (base ** i)) % base for i in range(W))
            assert rule[nbhd] == val, "collected entry contradicts the rule"

        sorted_idx = sorted(observed)
        answer = ' '.join(f"{i}:{observed[i]}" for i in sorted_idx)

        payload = {
            'radius': r,
            'alphabet': base,
            'patches': [_render_grid(p) for p in patches],
            'format': '2:1 5:0',
        }
        return Entry(metadata={
            'payload': payload,
            'radius': int(r),
            'alphabet': int(base),
            'answer_list': [(int(i), int(observed[i])) for i in sorted_idx],
        }, answer=answer)

    def render_prompt(self, metadata):
        payload = metadata['payload']
        r = payload['radius']
        base = payload['alphabet']
        w = 2 * r + 1
        blocks = '\n\n'.join(f"Run {i + 1}:\n{p}" for i, p in enumerate(payload['patches']))
        return (
            f"Cells hold values from the alphabet 0..{base - 1}; '?' marks a "
            f"missing state. Several spatial slices (runs) were produced by a "
            f"single unknown update rule that maps every length-{w} neighborhood "
            f"(this position plus {r} left and {r} right) to the next value of "
            f"the center cell, acting identically on every run. Each run advances "
            f"one row per time step; edge columns never update.\n\n"
            f"{blocks}\n\n"
            f"Recover the rule entries that the data forces: every entry whose "
            f"length-{w} neighborhood and center successor are both fully visible "
            f"(no '?') in at least one run. Write each as INDEX:VALUE, where INDEX "
            f"is the neighborhood read left-to-right as a base-{base} number "
            f"(all-zero window has INDEX 0), and VALUE is the forced successor. "
            f"List the entries in ascending INDEX, separated by spaces "
            f"(format: '2:1 5:0')."
        )

    def score_answer(self, answer, entry):
        reference = entry['answer']
        if str(answer).strip() == str(reference).strip():
            return 1
        try:
            got = _parse_answer(answer)
            want = _parse_answer(reference)
        except Exception:
            return 0
        return 1 if got == want else 0
