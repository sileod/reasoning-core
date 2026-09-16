import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.suffix_automaton_growth_trace.suffix_automaton_growth_trace import (
    suffix_automaton_growth_trace,
)

SEED = 1139467751
OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    random.seed(SEED)
    task = suffix_automaton_growth_trace()
    lines = ["# Samples for suffix_automaton_growth_trace (P007v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
