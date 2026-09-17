"""Generate samples_P004v1.md for degree_construction_equivalence."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.degree_construction_equivalence.degree_construction_equivalence import (
    DegreeConstructionEquivalence,
)


def main():
    random.seed(3536382515)
    task = DegreeConstructionEquivalence()
    lines = ["# Samples: degree_construction_equivalence", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for wanted in ('no', 'yes'):
            for _ in range(80):
                entry = task.generate_entry()
                if entry.answer == wanted:
                    break
            else:
                raise RuntimeError(f"Missing {wanted} example at level {level}")
            prompt = task.render_prompt(entry.metadata)
            lines.append("### Prompt")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P004v1.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
