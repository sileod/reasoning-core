import random
from pathlib import Path

random.seed(1259343118)

from reasoning_core.tasks.generated.ua_planning_backtracking_r5.common_polyhedral_net.common_polyhedral_net import (
    CommonPolyhedralNet,
)

out = Path(__file__).with_name("samples_P003v3.md")
task = CommonPolyhedralNet()
chunks = []
for level in (0, 2, 5):
    task.config.set_level(level)
    chunks.append("## Level %d" % level)
    for _ in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        chunks.append("**Prompt:** %s" % prompt)
        chunks.append("**Answer:** %s" % ex.answer)
out.write_text("\n\n".join(chunks) + "\n")
