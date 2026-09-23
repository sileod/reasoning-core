import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_inference_modes_r4.bresenham_raster_trace.bresenham_raster_trace import (
    BresenhamRasterTrace,
)

random.seed(2267388306)

task = BresenhamRasterTrace()

out = Path(__file__).with_name("samples_P003v1.md")
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for i in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt**")
        lines.append(prompt)
        lines.append("")
        lines.append("**Answer**")
        lines.append(ex.answer)
        lines.append("")

out.write_text("\n".join(lines))
