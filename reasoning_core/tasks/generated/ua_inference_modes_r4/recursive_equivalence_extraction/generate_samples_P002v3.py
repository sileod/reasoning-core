import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.recursive_equivalence_extraction.recursive_equivalence_extraction import (
    RecursiveEquivalenceExtraction,
)

random.seed(368817805)

OUT = Path(__file__).with_name("samples_P002v3.md")
task = RecursiveEquivalenceExtraction()

lines = []
for level in (0, 2, 5):
    lines.append("Level %d" % level)
    lines.append("")
    task.config.set_level(level)
    for i in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append("Example %d" % (i + 1))
        lines.append("")
        lines.append("Prompt:")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append(ex.answer)
        lines.append("")
        lines.append("-")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT)
