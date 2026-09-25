import random
from pathlib import Path

random.seed(1662004003)

from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.anaphoric_description_transfer.anaphoric_description_transfer import (
    AnaphoricDescriptionTransfer,
)

TASK = AnaphoricDescriptionTransfer()
OUT = Path(__file__).with_name("samples_P001v1.md")


def main():
    lines = []
    for level in (0, 2, 5):
        TASK.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            ex = TASK.generate_example()
            lines.append("### Prompt")
            lines.append(TASK.render_prompt(ex.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
