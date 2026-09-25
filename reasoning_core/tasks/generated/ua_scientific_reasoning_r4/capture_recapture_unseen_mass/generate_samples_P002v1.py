import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.capture_recapture_unseen_mass import (
    capture_recapture_unseen_mass as mod,
)

random.seed(1475571465)

task = mod.CaptureRecaptureUnseenMass()
out_path = Path(__file__).with_name("samples_P002v1.md")


def render_example(level):
    task.config.set_level(level)
    x = task.generate_example()
    prompt = task.render_prompt(x.metadata)
    return prompt, x.answer


lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for idx in range(1, 3):
        prompt, answer = render_example(level)
        lines.append(f"### Example {idx}")
        lines.append(prompt)
        lines.append("")
        lines.append(f"Answer: {answer}")
        lines.append("")

out_path.write_text("\n".join(lines) + "\n")
