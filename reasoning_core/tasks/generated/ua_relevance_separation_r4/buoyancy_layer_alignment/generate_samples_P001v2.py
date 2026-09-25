import random
from pathlib import Path

from buoyancy_layer_alignment import BuoyancyLayerAlignment

random.seed(2302342651)
task = BuoyancyLayerAlignment()

out = []
for level, count, headings in [(0, 2, "Level 0"), (2, 2, "Level 2"), (5, 2, "Level 5")]:
    out.append(f"## {headings}")
    for _ in range(count):
        entry = task.generate_example(level=level)
        out.append("### Prompt")
        out.append(task.render_prompt(entry.metadata))
        out.append("")
        out.append("### Answer")
        out.append(entry.answer)
        out.append("")
        out.append("---")
        out.append("")

path = Path(__file__).with_name("samples_P001v2.md")
path.write_text("\n".join(out))
print(path)
