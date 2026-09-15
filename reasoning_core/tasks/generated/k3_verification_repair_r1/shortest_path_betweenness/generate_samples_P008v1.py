import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.shortest_path_betweenness.shortest_path_betweenness import (
    ShortestPathBetweenness,
)

SEED = 682015719


def main():
    random.seed(SEED)
    task = ShortestPathBetweenness()
    out = Path(__file__).with_name("samples_P008v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}\n")
            lines.append(f"**Prompt:**\n\n{ex.prompt}\n")
            lines.append(f"**Answer:** {ex.answer}\n")
        lines.append("")
    out.write_text("\n".join(lines))
    print(out)


if __name__ == "__main__":
    main()
