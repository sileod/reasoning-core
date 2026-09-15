import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.debruijn_scope_translation.debruijn_scope_translation import (
    DeBruijnScopeTranslationV1,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")

task = DeBruijnScopeTranslationV1()

lines = ["# Samples P003v1", ""]
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append("```")
        lines.append(ex.prompt)
        lines.append("```")
        lines.append("")
        lines.append("Answer:")
        lines.append("")
        lines.append("```")
        lines.append(ex.answer)
        lines.append("```")
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
