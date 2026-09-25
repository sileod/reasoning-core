import random
import sys
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r5.heap_assertion_separability.heap_assertion_separability import (
    HeapAssertionSeparability,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")

task = HeapAssertionSeparability()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for _ in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.append(f"### Prompt")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append(ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(OUT)
