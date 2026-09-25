import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.relation_residuation.relation_residuation import (
    RelationResiduation,
)


def main():
    random.seed(1339177894)
    task = RelationResiduation()
    out = Path(__file__).with_name("samples_P004v3.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            lines.append("Prompt:")
            lines.append("")
            lines.append("    " + task.render_prompt(e.metadata).replace("\n", "\n    "))
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("    " + e.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
