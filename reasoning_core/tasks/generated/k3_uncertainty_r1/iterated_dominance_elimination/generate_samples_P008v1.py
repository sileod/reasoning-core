import random
import sys
from pathlib import Path

OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    seed = 682015719
    random.seed(seed)
    out_dir = Path(__file__).parent
    sys.path.insert(0, str(out_dir))
    from reasoning_core.tasks.generated.k3_uncertainty_r1.iterated_dominance_elimination.iterated_dominance_elimination import (
        IteratedDominanceElimination,
    )

    task = IteratedDominanceElimination()
    lines = ["# Samples P008v1", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append("**Prompt:**")
            lines.append("")
            for pl in prompt.split("\n"):
                lines.append(f"    {pl}")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"    {x.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
