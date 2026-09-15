import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_counterfactual_r1.palindromic_tree_counts.palindromic_tree_counts import (
    PalindromicTreeCounts,
)

random.seed(1336314872)


def main():
    task = PalindromicTreeCounts()
    out = Path(__file__).with_name("samples_P002v2.md")
    lines = []
    required = {0: 2, 2: 2, 5: 2}
    for level in [0, 2, 5]:
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(required[level]):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            answer = entry.answer
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {answer}")
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
