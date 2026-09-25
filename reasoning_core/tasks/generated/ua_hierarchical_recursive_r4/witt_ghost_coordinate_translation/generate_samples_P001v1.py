#!/usr/bin/env python
import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_hierarchical_recursive_r4.witt_ghost_coordinate_translation import (
    witt_ghost_coordinate_translation as m,
)

random.seed(1662004003)

task = m.WittGhostCoordinateTranslation()
lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    task.config.set_level(level)
    for k in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(f"## Example {k + 1} ({ex.metadata['family']}, mode {ex.metadata['mode']})")
        lines.append("Prompt:")
        lines.append("```")
        lines.append(prompt)
        lines.append("```")
        lines.append("Answer:")
        lines.append("```")
        lines.append(ex.answer)
        lines.append("```")
        lines.append("")

out = Path(__file__).with_name("samples_P001v1.md")
out.write_text("\n".join(lines))
print("wrote", out)
