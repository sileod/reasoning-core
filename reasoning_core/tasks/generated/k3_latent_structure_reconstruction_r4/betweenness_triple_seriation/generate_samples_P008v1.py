import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.betweenness_triple_seriation.betweenness_triple_seriation import (
    BetweennessTripleSeriation,
)

random.seed(682015719)

OUT = Path(__file__).with_name("samples_P008v1.md")
task = BetweennessTripleSeriation()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    for idx in range(2):
        task.config.set_level(level)
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        lines.append(f"### Example {idx + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")
    lines.append("")

OUT.write_text("\n".join(lines))
print(OUT)
