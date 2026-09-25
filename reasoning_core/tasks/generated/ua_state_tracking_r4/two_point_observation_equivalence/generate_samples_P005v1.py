import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.two_point_observation_equivalence.two_point_observation_equivalence import (
    TwoPointObservationEquivalence,
)

random.seed(729651269)

TASK = TwoPointObservationEquivalence()
OUT = Path(__file__).with_name("samples_P005v1.md")


def render(_level):
    TASK.config.set_level(_level)
    return TASK.generate_example()


lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for _ in range(2):
        x = render(level)
        prompt = TASK.render_prompt(x.metadata)
        lines.append("Prompt:")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append(x.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
