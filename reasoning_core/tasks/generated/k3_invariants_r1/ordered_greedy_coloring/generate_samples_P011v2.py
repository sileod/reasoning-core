import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.ordered_greedy_coloring.ordered_greedy_coloring import (  # noqa: E501
    OrderedGreedyColoring,
)

SEED = 525660630


def main():
    random.seed(SEED)
    task = OrderedGreedyColoring()
    out_path = Path(__file__).with_name("samples_P011v2.md")
    lines = ["# Samples for ordered_greedy_coloring (P011v2)"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"\n## Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            lines.append("")
            lines.append("### Prompt")
            lines.append("```")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("```")
            lines.append("")
            lines.append("### Answer")
            lines.append("```")
            lines.append(entry.answer)
            lines.append("```")
    out_path.write_text("\n".join(lines) + "\n")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
