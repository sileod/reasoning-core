import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.loom_shed_memory.loom_shed_memory import (
    LoomShedMemory, LoomShedMemoryV2Config,
)

random.seed(2302342651)

levels = [0, 2, 5]
out = []
task = LoomShedMemory()
for level in levels:
    cfg = LoomShedMemoryV2Config()
    cfg.set_level(level)
    task.config = cfg
    out.append("## Level %d\n" % level)
    for _ in range(2):
        ex = task.generate_example()
        out.append("### Prompt\n")
        out.append(task.render_prompt(ex.metadata))
        out.append("\n")
        out.append("### Answer\n")
        out.append(ex.answer)
        out.append("\n")

Path(__file__).with_name("samples_P001v2.md").write_text("\n".join(out))
