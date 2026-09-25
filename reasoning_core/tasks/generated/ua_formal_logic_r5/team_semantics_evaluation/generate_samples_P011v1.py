import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r5.team_semantics_evaluation import (
    team_semantics_evaluation as mod,
)

random.seed(2305351643)

task = mod.TeamSemanticsEvaluation()
out = Path(__file__).with_name("samples_P011v1.md")

lines = []
lines.append("# Samples: team_semantics_evaluation (P011v1)")
lines.append("")
lines.append("Two prompt/answer examples at each of levels 0, 2 and 5. Answers are verbatim.")
lines.append("")

for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("Prompt:")
        lines.append("```text")
        lines.append(ex.prompt)
        lines.append("```")
        lines.append(f"Answer: {ex.answer}")
        lines.append("")

Path(out).write_text("\n".join(lines))
print("wrote", out)
