import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.inversion_trigger_linearization.inversion_trigger_linearization import (
    InversionTriggerLinearization,
)

random.seed(1705404348)

task = InversionTriggerLinearization()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for _ in range(2):
        task.config.set_level(level)
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        lines.append(prompt)
        lines.append("Answer: " + entry.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P006v2.md")
out.write_text("\n".join(lines))
