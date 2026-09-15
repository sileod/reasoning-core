import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


COLORS = {
    "red": ["crimson", "scarlet", "vermillion"],
    "blue": ["azure", "cerulean", "cobalt"],
    "green": ["emerald", "olive", "lime"],
    "yellow": ["golden", "amber", "saffron"],
    "purple": ["violet", "magenta", "plum"],
    "orange": ["tangerine", "apricot", "marigold"],
}
COLOR_NAMES = sorted(COLORS.keys())


def decode_color(word):
    for color, synonyms in COLORS.items():
        if word == color or word in synonyms:
            return color
    return None


@dataclass
class NoisyChannelConfig(Config):
    length: int = 3

    def apply_difficulty(self, level):
        self.length = min(6, 2 + level)


class NoisyChannelRecovery(Task):
    summary = (
        "Recover a short intended utterance from controlled corruption, "
        "contextual constraints, and an explicit noise model: each intended "
        "color is replaced by one of its synonyms per an explicit per-token "
        "replace probability, and the solver must answer with the original "
        "color set sorted alphabetically."
    )
    design_choice = (
        "Present the intended utterance as a sequence of color names, apply "
        "noise by randomly replacing each color with one of its synonyms, and "
        "require the solver to answer with the original color set sorted "
        "alphabetically."
    )
    config_cls = NoisyChannelConfig

    TASK_META = {
        'parent_source_id': None,
        'idea': 'noisy_channel_recovery (draw 3 of 3)',
        'hypothesis': 'ASTRA2:noisy_channel_recovery',
        'changes': 'new task in '
                   'reasoning_core/tasks/generated/wave12/noisy_channel_recovery',
        'generation': {'provider_name': 'albert',
                       'model_name': 'deepseek-v4-flash',
                       'harness_name': 'opencode',
                       'harness_version': None,
                       'agent_name': 'task-search-worker',
                       'settings': {'variant': None,
                                    'requested_seed': 960070481,
                                    'seed_forwarded': True,
                                    'temperature': None,
                                    'top_p': None,
                                    'pure': True,
                                    'max_steps': 40,
                                    'timeout_seconds': 1800,
                                    'sandbox': {'name': 'bubblewrap',
                                                'version': 'bubblewrap 0.8.0'}}}}

    def generate_entry(self):
        length = self.config.length
        while True:
            intended = [random.choice(COLOR_NAMES) for _ in range(length)]
            replace_prob = random.choice([0.3, 0.5, 0.7])
            observed = []
            for color in intended:
                if random.random() < replace_prob:
                    observed.append(random.choice(COLORS[color]))
                else:
                    observed.append(color)
            original_set = sorted(set(intended))
            answer = ", ".join(original_set)
            assert all(decode_color(w) == c for w, c in zip(observed, intended))
            assert len(answer) > 0
            return Entry(
                metadata={
                    "observed": observed,
                    "replace_prob": replace_prob,
                    "length": length,
                    "intended": intended,
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        observed = ", ".join(metadata["observed"])
        return (
            f"A noisy channel sent a sequence of color names. Each intended "
            f"color was independently left unchanged with probability "
            f"{1 - metadata['replace_prob']:.1f}, or replaced by one of its "
            f"synonyms with probability {metadata['replace_prob']:.1f}. The "
            f"received sequence is: {observed}. Recover the set of distinct "
            f"intended colors, and write them as a comma-separated list sorted "
            f"alphabetically (e.g. 'blue, green, red')."
        )

    def score_answer(self, answer, entry):
        answer = (answer or "").strip().lower()
        if not answer:
            return 0.0
        parts = [p.strip() for p in answer.split(",")]
        parts = [p for p in parts if p]
        expected = [c for c in entry.metadata["intended"]]
        gold_set = sorted(set(expected))
        if sorted(parts) == gold_set:
            return 1.0
        return 0.0


TASK_META = {
    'parent_source_id': None,
    'idea': 'noisy_channel_recovery (draw 3 of 3)',
    'hypothesis': 'ASTRA2:noisy_channel_recovery',
    'changes': 'new task in '
               'reasoning_core/tasks/generated/wave12/noisy_channel_recovery',
    'generation': {'provider_name': 'albert',
                   'model_name': 'deepseek-v4-flash',
                   'harness_name': 'opencode',
                   'harness_version': None,
                   'agent_name': 'task-search-worker',
                   'settings': {'variant': None,
                                'requested_seed': 960070481,
                                'seed_forwarded': True,
                                'temperature': None,
                                'top_p': None,
                                'pure': True,
                                'max_steps': 40,
                                'timeout_seconds': 1800,
                                'sandbox': {'name': 'bubblewrap',
                                            'version': 'bubblewrap 0.8.0'}}}}
