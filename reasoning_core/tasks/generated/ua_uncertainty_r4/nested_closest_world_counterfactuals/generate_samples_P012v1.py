import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.nested_closest_world_counterfactuals.nested_closest_world_counterfactuals import (
    NestedClosestWorldCounterfactuals,
)


def main():
    random.seed(1277236794)
    task = NestedClosestWorldCounterfactuals()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}")
        for _ in range(2):
            ex = task.generate_example()
            out.append("Prompt:")
            out.append(ex.prompt)
            out.append("Answer: " + ex.answer)
            out.append("")
    out.append(f"# End samples ({task.task_name})")
    text = "\n".join(out) + "\n"
    dest = Path(__file__).with_name("samples_P012v1.md")
    dest.write_text(text)


if __name__ == "__main__":
    main()
