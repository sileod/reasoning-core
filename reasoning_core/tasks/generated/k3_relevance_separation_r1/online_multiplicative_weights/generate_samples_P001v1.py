"""Generate samples_P001v1.md for the online multiplicative weights trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relevance_separation_r1.online_multiplicative_weights.online_multiplicative_weights import (
    OnlineMultiplicativeWeights,
)

random.seed(1662004003)


def main():
    out_path = Path(__file__).with_name("samples_P001v1.md")
    task = OnlineMultiplicativeWeights()
    lines = ["# Samples P001v1 — online_multiplicative_weights", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            task.config.set_level(level)
            ex = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    out_path.write_text("\n".join(lines))
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
