import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r4.process_dissociation_routes.process_dissociation_routes import (
    ProcessDissociationRoutes,
)

random.seed(382564971)

OUT = Path(__file__).with_name("samples_P003v2.md")
task = ProcessDissociationRoutes()

lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    task.config.set_level(level)
    lines.append("")
    for _ in range(2):
        e = task.generate_example()
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append(e.answer)
        lines.append("")
        lines.append("")

OUT.write_text("\n".join(lines))
