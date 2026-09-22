import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r4.post_tag_system_evolution.post_tag_system_evolution import (
    PostTagSystemEvolution,
)

SEED = 1139467751
OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        task = PostTagSystemEvolution()
        task.config.set_level(level)
        lines.append("# Level %d" % level)
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("Answer: %s" % ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
