import random
from pathlib import Path

from reasoning_core.template import Task
from reasoning_core.tasks.generated.ua_interacting_updates_r4.boundary_degree_inference.boundary_degree_inference import (
    BoundaryDegreeInference,
)

random.seed(1339177894)

LEVELS = {0: 2, 2: 2, 5: 2}
task = BoundaryDegreeInference()
out = []
for level, count in LEVELS.items():
    task.config.set_level(level)
    out.append(f"# Level {level}")
    for _ in range(count):
        ex = task.generate_example()
        out.append("")
        out.append("Prompt:")
        out.append(ex.prompt)
        out.append("")
        out.append(f"Answer: {ex.answer}")
    out.append("")

dest = Path(__file__).with_name("samples_P004v3.md")
dest.write_text("\n".join(out) + "\n")
print("wrote", dest)
