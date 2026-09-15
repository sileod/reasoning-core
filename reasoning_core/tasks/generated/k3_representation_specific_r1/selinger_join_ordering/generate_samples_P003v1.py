import random
from pathlib import Path

random.seed(2267388306)

from reasoning_core.tasks.generated.k3_representation_specific_r1.selinger_join_ordering.selinger_join_ordering import (
    SelingerJoinOrdering,
)


def main():
    out = Path(__file__).with_name("samples_P003v1.md")
    task = SelingerJoinOrdering()
    with open(out, "w") as f:
        f.write("# Samples P003v1: Selinger join ordering\n\n")
        for level in (0, 2, 5):
            f.write(f"## Level {level}\n\n")
            task.config.set_level(level)
            for i in range(2):
                e = task.generate_example()
                f.write(f"### Example {i+1}\n\n")
                f.write("**Prompt:**\n\n")
                f.write(task.render_prompt(e.metadata))
                f.write("\n\n**Answer:**\n\n")
                f.write(e.answer)
                f.write("\n\n")


if __name__ == "__main__":
    main()
