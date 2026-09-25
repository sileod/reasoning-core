import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.paragraph_reflow_resynchronization.paragraph_reflow_resynchronization import (
    ParagraphReflowResync,
    ParagraphReflowResyncConfig,
)

random.seed(1475571465)

OUT = Path(__file__).with_name("samples_P002v1.md")

task = ParagraphReflowResync()

lines = []
for level in (0, 2, 5):
    cfg = ParagraphReflowResyncConfig()
    cfg.set_level(level)
    task.config = cfg
    lines.append(f"# Level {level}")
    lines.append("")
    for k in range(2):
        entry = task.generate_entry()
        lines.append(f"## Example {k + 1}")
        lines.append("")
        lines.append(task.render_prompt(entry.metadata))
        lines.append("")
        lines.append(f"Answer: {entry.answer}")
        lines.append("")

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("wrote", OUT)
