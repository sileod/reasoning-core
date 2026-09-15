import random
import sys
from pathlib import Path

random.seed(382564971)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from matrix_characteristic_polynomial import MatrixCharacteristicPolynomial

out = Path(__file__).with_name("samples_P003v2.md")

task = MatrixCharacteristicPolynomial()

lines = []
lines.append("# Samples for matrix_characteristic_polynomial (P003v2)")
lines.append("")
lines.append("Two prompt/answer examples at each of levels 0, 2 and 5.")
lines.append("")

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for ex_idx in range(2):
        e = task.generate_example()
        lines.append(f"### Example {ex_idx + 1}")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append("```text")
        lines.append(e.answer)
        lines.append("```")
        lines.append("")

out.write_text("\n".join(lines))
print("wrote", out)
