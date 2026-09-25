import random
from pathlib import Path

random.seed(4238614268)

from reasoning_core.tasks.generated.ua_multi_relation_integration_r4.polyhedral_plane_sections.polyhedral_plane_sections import PolyhedralPlaneSections

out = Path(__file__).with_name("samples_P001v3.md")

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task = PolyhedralPlaneSections()
    task.config.set_level(level)
    for i in range(2):
        x = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append(f"Answer: {x.answer}")
        lines.append("")

out.write_text("\n".join(lines))
