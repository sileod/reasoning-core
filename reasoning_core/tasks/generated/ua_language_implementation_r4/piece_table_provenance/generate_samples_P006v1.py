import random
from pathlib import Path

random.seed(798610012)

from reasoning_core.tasks.generated.ua_language_implementation_r4.piece_table_provenance.piece_table_provenance import (
    PieceTableProvenance,
)

OUT = Path(__file__).with_name("samples_P006v1.md")


def main():
    task = PieceTableProvenance()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Prompt")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("### Answer")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
