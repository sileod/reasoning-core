import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.havel_hakimi_realization.havel_hakimi_realization import (
    HavelHakimiRealization,
    HavelHakimiConfig,
)

random.seed(682015719)

task = HavelHakimiRealization()
out = []
for level in (0, 2, 5):
    cfg = HavelHakimiConfig()
    cfg.set_level(level)
    task.config = cfg
    out.append(f"## Level {level}\n")
    for _ in range(2):
        ex = task.generate_example()
        out.append("### Prompt\n")
        out.append(task.render_prompt(ex.metadata))
        out.append("\n")
        out.append("### Answer\n")
        out.append(ex.answer)
        out.append("\n")

Path(__file__).with_name("samples_P008v1.md").write_text("\n".join(out))
