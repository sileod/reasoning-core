import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.segment_tree_lazy_propagation.segment_tree_lazy_propagation import (
    SegmentTreeLazyPropagation,
)

random.seed(798610012)

task = SegmentTreeLazyPropagation()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"# Level {level}")
    for _ in range(2):
        e = task.generate_example()
        out.append("## Example")
        out.append(task.render_prompt(e.metadata))
        out.append("Answer:")
        out.append(e.answer)
        out.append("")
    out.append("")

Path(__file__).with_name("samples_P006v1.md").write_text("\n".join(out) + "\n")
