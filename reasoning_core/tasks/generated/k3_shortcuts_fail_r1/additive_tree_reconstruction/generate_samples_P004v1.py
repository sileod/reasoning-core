import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.additive_tree_reconstruction.additive_tree_reconstruction import (
    AdditiveTreeReconstruction,
)

random.seed(3536382515)

OUT = Path(__file__).resolve().parent / "samples_P004v1.md"


def main():
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task = AdditiveTreeReconstruction()
        for _ in range(2):
            ex = task.generate_example(level=level)
            prompt = task.render_prompt(ex.metadata)
            lines.append("Prompt:")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
