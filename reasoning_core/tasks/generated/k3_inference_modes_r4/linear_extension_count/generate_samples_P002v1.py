import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_inference_modes_r4.linear_extension_counting.linear_extension_counting import (
    LinearExtensionCountV1,
)

random.seed(1475571465)
task = LinearExtensionCountV1()
out = Path(__file__).with_name("samples_P002v1.md")
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for _ in range(2):
        ex = task.generate_example(level=level)
        lines.append("Prompt:")
        lines.append(ex.prompt)
        lines.append("Answer:")
        lines.append(ex.answer)
        lines.append("")
out.write_text("\n".join(lines))
print(out)
