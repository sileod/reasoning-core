from pathlib import Path
import random

from reasoning_core.tasks.generated.ua_state_tracking_r4.periodic_density_equivalence.periodic_density_equivalence import (
    PeriodicDensityEquivalence)

SEED = 3536382515
OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    random.seed(SEED)
    lines = ["# Samples for periodic_density_equivalence (P004v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        obj = PeriodicDensityEquivalence()
        obj.config.set_level(level)
        picked = []
        wanted = {"EQ", "NEQ"}
        attempts = 0
        while len(picked) < 2 and attempts < 100:
            entry = obj.generate_example()
            if entry.answer in wanted:
                wanted.discard(entry.answer)
                picked.append(entry)
            attempts += 1
        for i, entry in enumerate(picked):
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("```")
            lines.append(obj.render_prompt(entry.metadata))
            lines.append("```")
            lines.append("")
            lines.append(f"**Answer:** {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
