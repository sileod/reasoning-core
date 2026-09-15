"""Generate the samples file for counterfeit_weighing_deduction."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.counterfeit_weighing_deduction.counterfeit_weighing_deduction import (
    CounterfeitWeighingDeduction,
)

SEED = 3577985643


def main():
    random.seed(SEED)
    task = CounterfeitWeighingDeduction()
    out = Path(__file__).with_name("samples_P004v2.md")
    parts = [
        "# samples_P004v2 - counterfeit_weighing_deduction",
        "",
    ]
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        parts.append("")
        task.config.set_level(level)
        for k in range(2):
            x = task.generate_example()
            parts.append(f"### Example {k + 1}")
            parts.append("")
            parts.append("**Prompt:**")
            parts.append("")
            parts.append(task.render_prompt(x.metadata))
            parts.append("")
            parts.append("**Answer:**")
            parts.append("")
            parts.append(f"`{x.answer}`")
            parts.append("")
    out.write_text("\n".join(parts))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
