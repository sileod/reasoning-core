import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.interval_nesting_forest.interval_nesting_forest import (
    IntervalNestingForest, IntervalNestingForestConfig,
)


def main():
    random.seed(682015719)
    t = IntervalNestingForest()
    out = []
    for level in [0, 2, 5]:
        cfg = IntervalNestingForestConfig()
        cfg.set_level(level)
        t.config = cfg
        out.append(f"## Level {level}")
        for _ in range(2):
            e = t.generate_entry()
            out.append("### Prompt")
            out.append(t.render_prompt(e.metadata))
            out.append("### Answer")
            out.append(e.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P008v1.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
