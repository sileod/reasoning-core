import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relevance_separation_r1.flow_path_decomposition.flow_path_decomposition import (
    FlowPathDecomposition,
)

random.seed(1475571465)

task = FlowPathDecomposition()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}")
    for _ in range(2):
        ex = task.generate_example()
        out.append("Prompt:")
        out.append(ex.prompt)
        out.append("Answer:")
        out.append(ex.answer)
        out.append("")
    out.append("")

path = Path(__file__).with_name("samples_P002v1.md")
path.write_text("\n".join(out))
print("wrote", path)
