import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.tree_subset_counting_dp.tree_subset_counting_dp import (
    TreeSubsetCounting,
)

random.seed(3577985643)

OUT = Path(__file__).with_name("samples_P004v2.md")
task = TreeSubsetCounting()


def emit(f, level):
    for _ in range(2):
        entry = task.generate_example(level=level)
        f.write(f"### Level {level}\n\n")
        f.write(f"**Prompt:**\n{entry.prompt}\n\n")
        f.write(f"**Answer:**\n{entry.answer}\n\n")


with OUT.open("w") as f:
    f.write("# Samples for P004v2: tree_subset_counting_dp\n\n")
    for level in (0, 2, 5):
        emit(f, level)

print(f"wrote {OUT}")
