import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.melodic_transposition_spelling.melodic_transposition_spelling import (
    MelodicTranspositionSpelling,
)

random.seed(1662004003)
task = MelodicTranspositionSpelling()
out = Path(__file__).with_name("samples_P001v1.md")
lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}\n")
    for i, mode in enumerate(("notes", "key_signature")):
        task.config.set_level(level)
        for _ in range(100):
            e = task.generate_entry()
            if e.metadata["mode"] == mode:
                break
        else:
            raise RuntimeError("Could not sample both answer modes")
        lines.append(f"### Example {i + 1}\n")
        lines.append("Prompt:\n")
        lines.append(task.render_prompt(e.metadata) + "\n")
        lines.append(f"Answer: {e.answer}\n")
out.write_text("\n".join(lines))
print(f"wrote {out}")
