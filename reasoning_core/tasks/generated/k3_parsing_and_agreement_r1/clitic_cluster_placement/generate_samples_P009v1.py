import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.clitic_cluster_placement.clitic_cluster_placement import (
    CliticClusterPlacement,
)

random.seed(3867019559)

task = CliticClusterPlacement()

out = []
for level in (0, 2, 5):
    out.append(f"# Level {level}")
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("")
        out.append("**Prompt:**")
        out.append("")
        out.append(ex.prompt)
        out.append("")
        out.append("**Answer:**")
        out.append("")
        out.append(ex.answer)

Path(__file__).with_name("samples_P009v1.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print("wrote samples_P009v1.md")
