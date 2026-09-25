import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.kauffman_bracket_state_sum.kauffman_bracket_state_sum import (
    KauffmanBracketStateSum,
)

random.seed(3577985643)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

out = Path(__file__).with_name("samples_P004v2.md")
lines = []
for level in LEVELS:
    lines.append(f"Level {level}")
    lines.append("")
    task = KauffmanBracketStateSum()
    for _ in range(PER_LEVEL):
        ex = task.generate_example(level=level)
        prompt = task.render_prompt(ex.metadata)
        lines.append("Prompt:")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append(ex.answer)
        lines.append("")
    lines.append("")

out.write_text("\n".join(lines))
print(f"wrote {out}")
