import random
import importlib
from pathlib import Path

random.seed(3867019559)

mod = importlib.import_module(
    "reasoning_core.tasks.generated.k3_state_tracking_r4."
    "morphism_word_indexing.morphism_word_indexing"
)
MorphismWordIndexing = mod.MorphismWordIndexing

out = Path(__file__).with_name("samples_P009v1.md")

lines = []
for level in (0, 2, 5):
    task = MorphismWordIndexing()
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append("```")
        lines.append(ex.prompt)
        lines.append("```")
        lines.append("")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")

out.write_text("\n".join(lines))
print(out)
