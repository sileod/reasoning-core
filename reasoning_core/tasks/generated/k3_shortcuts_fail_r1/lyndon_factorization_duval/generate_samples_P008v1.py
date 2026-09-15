import random
from pathlib import Path

seed = 682015719
random.seed(seed)

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.lyndon_factorization_duval.lyndon_factorization_duval import LyndonFactorizationDuval, LyndonFactorizationConfig  # noqa: E402


def emit(level):
    cfg = LyndonFactorizationConfig()
    cfg.set_level(level)
    task = LyndonFactorizationDuval()
    task.config = cfg
    lines = [f"### Level {level}"]
    for _ in range(2):
        x = task.generate_example()
        lines.append("")
        lines.append("Prompt:")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append(x.answer)
    return "\n".join(lines)


parts = []
for lvl in (0, 2, 5):
    parts.append(emit(lvl))

here = Path(__file__).resolve().parent
with open(here / "samples_P008v1.md", "w") as f:
    f.write("\n".join(parts) + "\n")
