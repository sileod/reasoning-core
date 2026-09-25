import random
from pathlib import Path

random.seed(1618848011)

from marginal_extension_consistency import MarginalExtensionConsistency

OUT = Path(__file__).with_name("samples_P008v3.md")
task = MarginalExtensionConsistency()


sections = []
for level, count in ((0, 2), (2, 2), (5, 2)):
    lines = [f"## Level {level}"]
    for _ in range(count):
        ex = task.generate_example(level=level)
        lines.append("")
        lines.append("### Example")
        lines.append("")
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
    sections.append("\n".join(lines))

OUT.write_text("\n\n".join(sections) + "\n")
print(OUT)
