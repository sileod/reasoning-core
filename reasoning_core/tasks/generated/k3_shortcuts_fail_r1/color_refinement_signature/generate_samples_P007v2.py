import random
from pathlib import Path

random.seed(241712510)

import importlib

module_path = (
    "reasoning_core.tasks.generated.k3_shortcuts_fail_r1"
    ".color_refinement_signature.color_refinement_signature"
)
mod = importlib.import_module(module_path)
TaskCls = mod.ColorRefinementSignature

out = Path(__file__).with_name("samples_P007v2.md")

task = TaskCls()
sections = []
for level in (0, 2, 5):
    task.config.set_level(level)
    lines = [f"## Level {level}"]
    for _ in range(2):
        entry = task.generate_example()
        lines.append("### Prompt")
        lines.append("")
        lines.append(entry.prompt)
        lines.append("")
        lines.append("### Answer")
        lines.append("")
        lines.append(entry.answer)
        lines.append("")
    sections.append("\n".join(lines))

out.write_text("\n".join(sections))
