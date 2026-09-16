import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.nominal_compound_relation.nominal_compound_relation import (
    NominalCompoundRelation,
)

random.seed(2072234021)

TASK = NominalCompoundRelation()

otp = Path(__file__).with_name("samples_P005v2.md")
lines = []
for level in [0, 2, 5]:
    lines.append(f"## Level {level}")
    TASK.config.set_level(level)
    for i in range(2):
        x = TASK.generate_example()
        lines.append("### Example " + str(i + 1))
        lines.append("Prompt:")
        lines.append("")
        lines.append(TASK.render_prompt(x.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append("")
        lines.append(x.answer)
        lines.append("")
otp.write_text("\n".join(lines))
