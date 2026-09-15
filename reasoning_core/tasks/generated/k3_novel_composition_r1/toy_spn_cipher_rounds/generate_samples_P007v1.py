import random
from pathlib import Path

random.seed(1139467751)

from reasoning_core.tasks.generated.k3_novel_composition_r1.toy_spn_cipher_rounds.toy_spn_cipher_rounds import (
    ToySPNCipherRounds,
)


def main():
    task = ToySPNCipherRounds()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Prompt")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("### Answer")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P007v1.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
