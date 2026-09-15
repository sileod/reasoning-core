import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_counterfactual_r1.grid_light_occlusion_delta.light_occlusion_delta_task import (
    LightOcclusionDelta,
)

SEED = 682015719
OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    random.seed(SEED)
    task = LightOcclusionDelta()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"## Example {i + 1}")
            lines.append("Prompt:")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
