import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'attentional_blink_gating (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_language_implementation_r4/attentional_blink_gating',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class AttentionalBlinkGatingConfig(Config):
    n_items: int = 6
    max_gap: int = 4
    p_adjacent: float = 0.4
    p_long: float = 0.3

    def apply_difficulty(self, level):
        self.n_items = stochastic_rounding(self.n_items + level)
        self.max_gap = stochastic_rounding(self.max_gap + level)
        self.p_adjacent = min(0.6, 0.4 + 0.05 * level)
        self.p_long = min(0.5, 0.3 + 0.03 * level)


@dataclass
class _Gate:
    def __init__(self, recovery):
        self.recovery = recovery
        self.blink = 0


def _simulate(targets, distractors, gate):
    admitted = []
    for name, is_target in zip(targets, distractors):
        if not is_target:
            continue
        must_wait = gate.blink > 0
        gate.blink = max(0, gate.blink - 1)
        if must_wait:
            continue
        admitted.append(name)
        gate.blink = gate.recovery
    return admitted


class AttentionalBlinkGating(Task):
    summary = "Track target admission through an attention gate with stated consolidation and recovery rules; vary distractor gaps, adjacent targets, and prolonged stimuli; answer admitted targets or the gate state."
    design_choice = "Answer as a canonical list of admitted target identifiers in presentation order, e.g., 'T2,T5'"
    config_cls = AttentionalBlinkGatingConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_items
        names = [f"T{i}" for i in range(1, n + 1)]
        targets = list(names)

        gate = _Gate(recovery=random.randint(1, 3))
        # Pick a subset of targets to be "real" targets; rest are distractors.
        k = random.randint(1, n)
        chosen = set(random.sample(targets, k))
        distractors = [name in chosen for name in targets]
        admitted = _simulate(targets, distractors, gate)
        answer = ",".join(admitted) if admitted else "none"

        # Domain check: recovery perceptual delay and blink must be consistent.
        assert 0 <= gate.recovery <= 3
        assert all(
            name in chosen or name not in admitted for name in targets
        )

        metadata = {
            "targets": targets,
            "is_target": distractors,
            "admitted": admitted,
            "recovery": gate.recovery,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        target_series = ", ".join(
            metadata["targets"][i] + ("*" if m else "")
            for i, m in enumerate(metadata["is_target"])
        )
        return (
            f"An attentional system receives the following target series in order: {target_series}. "
            f"Items marked * are attended; unmarked items are distractors and are ignored. "
            f"Whenever an attended target is admitted, the gate enters a blink of the stated recovery "
            f"period and cannot admit any further target until it recovers; the blink decrements by 1 "
            f"per item while in effect. Here the consolidation recovery period is "
            f"{metadata['recovery']} item(s). "
            f"Which attended targets are actually admitted, in presentation order? "
            f"Answer as a comma-separated list like 'T2,T5', or 'none' if none."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        if answer is None:
            return 0.0
        a = str(answer).strip()
        g = gold
        if a == g:
            return 1.0
        return 0.0
