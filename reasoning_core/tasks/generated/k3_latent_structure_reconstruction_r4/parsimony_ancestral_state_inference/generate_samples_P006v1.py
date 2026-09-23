import random
from pathlib import Path

random.seed(798610012)

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.parsimony_ancestral_state_inference.parsimony_ancestral_state_inference import (
    ParsimonyAncestralStateInference,
)

OUT = Path(__file__).with_name("samples_P006v1.md")
task = ParsimonyAncestralStateInference()

lines = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"### Level {level}")
    for _ in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append("**Prompt**")
        lines.append(prompt)
        lines.append("**Answer**")
        lines.append(ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
