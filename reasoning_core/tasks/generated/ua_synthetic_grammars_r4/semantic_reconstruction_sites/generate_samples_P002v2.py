"""Generate samples_P002v2.md for the semantic_reconstruction_sites trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.semantic_reconstruction_sites.semantic_reconstruction_sites import (
    SemanticReconstructionSites,
)

random.seed(1336314872)

OUT = Path(__file__).with_name("samples_P002v2.md")

task = SemanticReconstructionSites()

sections = []
for level in (0, 2, 5):
    sections.append(f"## Level {level}\n")
    for n in range(2):
        ex = task.generate_example(level=level)
        sections.append(f"### Example {n + 1}\n")
        sections.append("Prompt:\n")
        sections.append(ex.prompt)
        sections.append("\nAnswer:\n")
        sections.append(ex.answer)
        sections.append("\n")

with open(OUT, "w") as f:
    f.write("\n".join(sections))

print("wrote", OUT)
