import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.lie_bracket_hall_normal_form.lie_bracket_hall_normal_form import (
    LieBracketHallNormalForm, LieHallConfig,
)

random.seed(1662004003)

levels = [0, 2, 5]
out = []
task = LieBracketHallNormalForm()
for level in levels:
    cfg = LieHallConfig()
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

Path(__file__).with_name("samples_P001v1.md").write_text("\n".join(out))
