import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.prufer_code_roundtrip.prufer_code_roundtrip import (
    PruferCodeRoundtrip,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    task = PruferCodeRoundtrip()
    out = Path(__file__).with_name("samples_P001v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
