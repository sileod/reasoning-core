import random
from pathlib import Path

from mass_count_unit_interpretation import MassCountUnitInterpretation

random.seed(798610012)

OUT = Path(__file__).with_name("samples_P006v1.md")

task = MassCountUnitInterpretation()


def render(level, count):
    task.config.set_level(level)
    for i in range(count):
        ex = task.generate_example()
        yield ex


lines = ["# Samples: mass_count_unit_interpretation", ""]
for level, count in ((0, 2), (2, 2), (5, 2)):
    lines.append(f"## Level {level}")
    lines.append("")
    for ex in render(level, count):
        lines.append("**Prompt:**")
        lines.append("")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer:**")
        lines.append("")
        lines.append(ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print(f"wrote {OUT}")
