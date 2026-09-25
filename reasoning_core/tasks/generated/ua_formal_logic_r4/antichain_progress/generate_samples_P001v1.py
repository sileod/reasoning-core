import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.antichain_progress_completion.antichain_progress import (
    AntichainProgress,
)

random.seed(1662004003)

out_path = Path(__file__).with_name("samples_P001v1.md")
task = AntichainProgress()

lines = []
lines.append("# P001v1 samples")
lines.append("")

for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    lines.append("")
    task.config.set_level(level)
    for _ in range(2):
        e = task.generate_example()
        lines.append("### Example")
        lines.append("")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append(f"**Answer:** {e.answer}")
        lines.append("")

out_path.write_text("\n".join(lines))
