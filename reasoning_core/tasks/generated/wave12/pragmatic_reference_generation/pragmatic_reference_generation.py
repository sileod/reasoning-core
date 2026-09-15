import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

SHAPES = ["circle", "square", "triangle", "star", "diamond", "moon", "heart", "crescent"]
COLORS = ["red", "blue", "green", "yellow", "orange", "purple", "white", "black"]
LEFT = "left"
RIGHT = "right"


@dataclass
class PragmaticReferenceGenConfig(Config):
    n_distractors: int = 3
    max_shapes: int = 4
    max_colors: int = 4

    def apply_difficulty(self, level):
        self.n_distractors = min(3 + level, 7)
        self.max_shapes = min(4 + level, 8)
        self.max_colors = min(4 + level, 8)


def _canonical(shape, color, pos):
    return f"{color} {shape} {pos}"


TASK_META = {'parent_source_id': None,
 'idea': 'pragmatic_reference_generation (draw 1 of 3)',
 'hypothesis': 'ASTRA0:pragmatic_reference_generation',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/pragmatic_reference_generation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1294949280,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def score_scalar(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    return 1.0 if answer == entry["answer"] else 0.0


class PragmaticReferenceGeneration(Task):
    summary = "Given a shared scene of colored shapes each on the left or right, name the canonical 'color shape side' of the unique object matching a stated color+shape clue, against distractors that each share at least one attribute with it."
    config_cls = PragmaticReferenceGenConfig
    design_choice = "Scene objects are colored geometric shapes; answer is a canonical string like 'circle red' or 'red circle left', with distractors sharing at least one attribute."

    def generate_entry(self):
        colors = COLORS[: self.config.max_colors]
        shapes = SHAPES[: self.config.max_shapes]
        while True:
            target = (
                random.choice(shapes),
                random.choice(colors),
                random.choice([LEFT, RIGHT]),
            )
            scene = [target]
            for _ in range(self.config.n_distractors):
                while True:
                    d = (
                        random.choice(shapes),
                        random.choice(colors),
                        random.choice([LEFT, RIGHT]),
                    )
                    if d == target:
                        continue
                    shares_color = d[1] == target[1]
                    shares_shape = d[0] == target[0]
                    if not (shares_color or shares_shape):
                        continue
                    if shares_color and shares_shape:
                        continue
                    if d in scene:
                        continue
                    break
                scene.append(d)

            clue = f"{target[1]} {target[0]}"
            target_desc = _canonical(*target)
            normalized = sorted({_canonical(s, c, p) for (s, c, p) in scene})
            if len(normalized) != len(scene):
                continue
            metadata = {"scene": normalized, "clue": clue, "target": target_desc}
            return Entry(metadata=metadata, answer=target_desc)

    def render_prompt(self, metadata):
        return (
            f"In a scene objects are described as 'color shape side'. The scene is: "
            f"{metadata['scene']}. A speaker refers to the unique object that is a "
            f"{metadata['clue']} (color and shape; ignore side). Nothing else in the "
            f"scene matches both color and shape. Give the full 'color shape side' of "
            f"that object."
        )

    def score_answer(self, answer, entry):
        return score_scalar(answer, entry)
