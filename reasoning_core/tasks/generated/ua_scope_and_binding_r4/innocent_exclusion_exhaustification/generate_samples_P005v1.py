import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.innocent_exclusion_exhaustification.task_innocent_exclusion_exhaustification import (
    InnocentExclusionExhaustification as TaskCls,
)

SEED = 729651269
TARGET_LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = TaskCls()
    base_config = TaskCls.config_cls()
    lines = []
    for level in sorted(TARGET_LEVELS):
        cfg = TaskCls.config_cls()
        cfg.set_level(level)
        task.config = cfg
        lines.append(f"## Level {level}\n")
        for _ in range(TARGET_LEVELS[level]):
            entry = task.generate_example()
            lines.append("**Prompt:**\n\n")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("\n\n**Answer:**\n\n")
            lines.append(entry.answer + "\n\n")

    out = Path(__file__).with_name("samples_P005v1.md")
    out.write_text("".join(lines))


if __name__ == "__main__":
    main()
