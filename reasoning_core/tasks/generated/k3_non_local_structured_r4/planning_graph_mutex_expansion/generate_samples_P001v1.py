import random
import sys
from pathlib import Path

HERE = Path(__file__).with_name("planning_graph_mutex_expansion.py")
root = str(HERE.parent.parent.parent.parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)

from reasoning_core.tasks.generated.k3_non_local_structured_r4.planning_graph_mutex_expansion.planning_graph_mutex_expansion import (  # noqa: E402
    PlanningGraphMutexExpansion,
)

random.seed(1662004003)


def main():
    task = PlanningGraphMutexExpansion()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append(task.render_prompt(ex.metadata))
            out.append("\nAnswer: " + str(ex.answer) + "\n")
        out.append("")
    (HERE.parent / "samples_P001v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
