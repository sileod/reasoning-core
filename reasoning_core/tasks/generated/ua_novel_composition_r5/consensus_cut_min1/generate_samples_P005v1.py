import random
from pathlib import Path

import reasoning_core
from consensus_cut_minimum import ConsensusCutMin1

random.seed(729651269)

task = ConsensusCutMin1()

out = []
out.append("# samples_P005v1  consensus_cut_minimum")
out.append("")

for level in (0, 2, 5):
    task.config.set_level(level)
    out.append("## Level %d" % level)
    out.append("")
    for i in range(2):
        ex = task.generate_example()
        out.append("### Example %d" % (i + 1))
        out.append("")
        out.append("Prompt:")
        out.append("")
        out.append(task.render_prompt(ex.metadata))
        out.append("")
        out.append("Answer: %s" % ex.answer)
        out.append("")

out_path = Path(__file__).with_name("samples_P005v1.md")
out_path.write_text("\n".join(out))
