import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.wrench_line_reconstruction import (
    wrench_line_reconstruction as wlr,
)

random.seed(3536382515)

task = wlr.WrenchLineReconstruction()

out = []
for lvl in (0, 2, 5):
    task.config.set_level(lvl)
    out.append("# Level {}".format(lvl))
    for i in range(2):
        e = task.generate_example()
        prompt = task.render_prompt(e.metadata)
        out.append("### Example {}".format(i + 1))
        out.append("**Prompt:**")
        out.append(prompt)
        out.append("**Answer:**")
        out.append(e.answer)
        out.append("")

dest = Path(__file__).with_name("samples_P004v1.md")
dest.write_text("\n".join(out) + "\n")
print("wrote", dest)
