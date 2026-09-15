import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.skyline_dominance_query.skyline_dominance_query import SkylineDominanceQuery

random.seed(3536382515)

LEVELS = [0, 2, 5]


def main():
    task = SkylineDominanceQuery()
    out = Path(__file__).with_name("samples_P004v1.md")
    lines = []
    lines.append("# Samples P004v1: skyline_dominance_query")
    lines.append("")
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for example_idx in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Example {example_idx + 1}")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"**Answer:** {entry.answer}")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
