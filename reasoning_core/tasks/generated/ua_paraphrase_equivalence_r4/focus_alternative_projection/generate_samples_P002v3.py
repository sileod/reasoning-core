import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_paraphrase_equivalence_r4.focus_alternative_projection.focus_alternative_projection import (
    FocusAlternativeProjection,
)

random.seed(368817805)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

task = FocusAlternativeProjection()

out = []
for level in LEVELS:
    task.config.set_level(level)
    out.append(f"# Level {level}\n")
    for i in range(PER_LEVEL):
        ex = task.generate_example()
        out.append(f"## Example {i + 1}\n")
        out.append("Prompt:\n\n" + task.render_prompt(ex.metadata) + "\n")
        out.append(f"\nAnswer: {ex.answer}\n")

out.append("\nGenerated deterministically with seed 368817805.\n")
Path(__file__).with_name("samples_P002v3.md").write_text("\n".join(out))
