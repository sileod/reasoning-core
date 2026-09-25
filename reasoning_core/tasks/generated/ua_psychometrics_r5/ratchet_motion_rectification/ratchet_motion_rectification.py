import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'ratchet_motion_rectification (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_psychometrics_r5/ratchet_motion_rectification',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


def _tuple_to_str(t):
    lo, hi, loc, hic = t
    left = '[' if loc else '('
    right = ']' if hic else ')'
    return f'{left}{lo},{hi}{right}'


def _contains(w, x):
    lo, hi, loc, hic = w
    if loc:
        if x < lo:
            return False
    else:
        if x <= lo:
            return False
    if hic:
        if x > hi:
            return False
    else:
        if x >= hi:
            return False
    return True


@dataclass
class RatchetMotionConfig(Config):
    n_strokes: int = 4
    max_mag: int = 6
    pitch: int = 1
    half_span: int = 2

    def apply_difficulty(self, level):
        self.n_strokes = 3 + level
        self.max_mag = 3 + level
        self.pitch = 1 + (level >= 3)
        self.half_span = 2 + level
        self.level = level


class RatchetMotionRectification(Task):
    summary = ("Convert alternating strokes into retained motion through ratchets with specified "
               "tooth pitches, pawl directions, and engagement windows; return net advance, the "
               "holding pawl, or the first ineffective stroke.")
    design_choice = ("Represent each stroke as a signed displacement and compute net advance by "
                     "summing only strokes that fall within the engagement window, with pawl "
                     "direction encoded as sign of window.")
    config_cls = RatchetMotionConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_strokes
        side = random.choice([-1, 1])
        window = (-cfg.half_span, cfg.half_span, True, True)

        strokes = []
        for _ in range(n):
            s = random.randint(-cfg.max_mag, cfg.max_mag)
            while s == 0:
                s = random.randint(-cfg.max_mag, cfg.max_mag)
            strokes.append(s)

        engaged = []
        for i, s in enumerate(strokes):
            v = s * side
            if _contains(window, v):
                engaged.append(i)

        set_engaged = set(engaged)

        mode = random.randint(0, 2)
        if mode == 0:
            target = 'net'
        elif mode == 1:
            target = 'pawl'
        else:
            target = 'first'

        if target == 'net':
            net = sum(strokes[i] for i in engaged)
            answer = str(net)
        elif target == 'pawl':
            if not engaged:
                answer = 'no pawl engages'
            else:
                engaged_sides = [1 if strokes[i] > 0 else -1 for i in engaged]
                pos = sum(1 for s in engaged_sides if s > 0)
                neg = sum(1 for s in engaged_sides if s < 0)
                if pos > neg:
                    answer = 'forward'
                elif neg > pos:
                    answer = 'backward'
                else:
                    answer = random.choice(['forward', 'backward'])
        else:
            first_ineff = next((i for i in range(n) if i not in set_engaged), None)
            if first_ineff is None:
                answer = 'no'
            else:
                answer = str(first_ineff)

        engaged_indices = tuple(sorted(engaged))

        metadata = {
            'strokes': strokes,
            'window': window,
            'side': side,
            'pitch': cfg.pitch,
            'target': target,
            'engaged_indices': list(engaged_indices),
            'net_advance': sum(strokes[i] for i in engaged),
        }

        # verify
        if target == 'net':
            assert int(answer) == metadata['net_advance']
        elif target == 'pawl':
            pass
        else:
            if answer != 'no':
                idx = int(answer)
                assert idx not in set_engaged
                assert all(j in set_engaged for j in range(idx))

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        m = metadata
        side = m['side']
        pawl = 'forward' if side > 0 else 'backward'
        wstr = _tuple_to_str(m['window'])
        strokes_str = ', '.join(str(x) for x in m['strokes'])
        if m['target'] == 'net':
            q = 'What is the net advance retained?'
        elif m['target'] == 'pawl':
            q = 'Which pawl holds the load (answer "forward", "backward", or "no pawl engages")?'
        else:
            q = 'What is the index of the first stroke that produces no retained motion, or "no"?'
        return (f'An escapement converts alternating strokes into retained motion. '
                f'Strokes are [{strokes_str}]. The pawl direction is {pawl}; only a stroke whose '
                f'scaled value v = stroke * direction falls inside the engagement window {wstr} '
                f'is retained, and the rest slip without producing motion. Tooth pitch is '
                f'{m["pitch"]}. {q} The answer is one value.')

    def score_answer(self, answer, entry):
        gold = entry.answer
        if isinstance(answer, str):
            answer = answer.strip()
        return 1.0 if answer == gold else 0.0
