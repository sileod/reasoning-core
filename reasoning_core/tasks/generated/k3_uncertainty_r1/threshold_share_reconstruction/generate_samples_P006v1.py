import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.threshold_share_reconstruction.threshold_share_reconstruction import (
    ThresholdShareReconstruction,
)

random.seed(798610012)


def main():
    task = ThresholdShareReconstruction()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"Level {level}")
        for _ in range(2):
            e = task.generate_example()
            out.append("")
            out.append("Prompt:")
            out.append(task.render_prompt(e.metadata))
            out.append("")
            out.append("Answer:")
            out.append(e.answer)
        out.append("")
    path = Path(__file__).with_name("samples_P006v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
