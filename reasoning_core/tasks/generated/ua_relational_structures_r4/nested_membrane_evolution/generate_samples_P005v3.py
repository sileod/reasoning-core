import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))

from reasoning_core.tasks.generated.ua_relational_structures_r4.nested_membrane_evolution.nested_membrane_evolution import NestedMembraneEvolution  # noqa: E402

random.seed(1140349348)


def main():
    task = NestedMembraneEvolution()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for k in range(2):
            ex = task.generate_example(level=level)
            out.append(f"### Example {k + 1}")
            out.append("")
            out.append("Prompt:")
            out.append("")
            out.append(ex["prompt"])
            out.append("")
            out.append("Answer:")
            out.append("")
            out.append(ex["answer"])
            out.append("")

    path = os.path.join(os.path.dirname(__file__), "samples_P005v3.md")
    with open(path, "w") as f:
        f.write("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
