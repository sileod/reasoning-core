import random
from pathlib import Path

random.seed(3713447331)

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.independence_restoring_mixtures.independence_restoring_mixtures import (  # noqa: E402
    IndependenceRestoringMixtures,
)

OUT = Path(__file__).with_name("samples_P009v3.md")

LEVELS = {0: 2, 2: 2, 5: 2}

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    for i in range(LEVELS[level]):
        task = IndependenceRestoringMixtures()
        task.config.set_level(level)
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        prompt = ex.metadata if False else task.render_prompt(ex.metadata)
        lines.append("**Prompt:**")
        lines.append(prompt)
        lines.append("")
        lines.append(f"**Answer:** {ex.answer}")
        lines.append("")

OUT.write_text("\n".join(lines), encoding="utf-8")
print("wrote", OUT)
