import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.ear_clipping_triangulation.ear_clipping_triangulation import (
    EarClippingTriangulation,
)

random.seed(1662004003)

task = EarClippingTriangulation()

out = []
for level in (0, 2, 5):
    out.append("")
    out.append(f"## Level {level}")
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("")
        out.append("### Example")
        out.append("")
        out.append("**Prompt:**")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append(ex.answer)
        out.append("")

text = "\n".join(out)
Path(__file__).with_name("samples_P001v1.md").write_text(text)
print("wrote samples_P001v1.md")
