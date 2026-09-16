import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.thematic_role_linking.thematic_role_linking import (
    ThematicRoleLinking)

SEED = 2409743872
random.seed(SEED)


def main():
    task = ThematicRoleLinking()
    lines = []
    lines.append("# Samples for P010v1: thematic_role_linking\n")
    for level in (0, 2, 5):
        lines.append(f"Level {level}\n")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            lines.append(f"**Prompt:** {prompt}")
            lines.append(f"**Answer:** {e.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P010v1.md")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
