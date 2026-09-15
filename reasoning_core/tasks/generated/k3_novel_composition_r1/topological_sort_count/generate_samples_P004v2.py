"""Generate samples_P004v2.md with prompt/answer examples at levels 0, 2 and 5."""
import random
from pathlib import Path

from reasoning_core.template import Config

from topological_sort_count import TopologicalSortCountV2Config, TopologicalSortCount

random.seed(3577985643)


def main():
    out = Path(__file__).with_name("samples_P004v2.md")
    lines = []
    t = TopologicalSortCount(config=TopologicalSortCountV2Config())

    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = t.generate_example(level=level)
            lines.append("Prompt:")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
