import random
from pathlib import Path

from rely_guarantee_compatibility import RelyGuaranteeCompatibility

random.seed(729651269)

task = RelyGuaranteeCompatibility()

out = Path(__file__).with_name("samples_P005v1.md")
sections = []
for level in (0, 2, 5):
    sections.append(f"## Level {level}\n")
    for k in range(2):
        task.config.set_level(level)
        ex = task.generate_example()
        sections.append(f"### Prompt {k + 1}\n")
        sections.append(task.render_prompt(ex.metadata))
        sections.append("\n")
        sections.append(f"**Answer:** {ex.answer}\n")
    sections.append("\n")

out.write_text("\n".join(sections), encoding="utf-8")
print("wrote", out)
