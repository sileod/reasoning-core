import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.rotation_system_face_tracing.rotation_system_face_tracing import (
    FaceTracing,
)

random.seed(2305351643)

task = FaceTracing()
out = Path(__file__).with_name("samples_P011v1.md")

lines = ["# Samples for rotation_system_face_tracing (P011v1)", ""]
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    for _ in range(2):
        task.config.set_level(level)
        e = task.generate_example()
        lines.append("### Prompt")
        lines.append("")
        lines.append(e.prompt)
        lines.append("")
        lines.append("Answer")
        lines.append("")
        lines.append(e.answer)
        lines.append("")
        lines.append("---")
        lines.append("")

out.write_text("\n".join(lines))
print(out)
