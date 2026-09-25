import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.stopped_expectation_conservation.stopped_expectation_conservation import (
    StoppedExpectationConservation as T,
)

random.seed(729651269)

task = T()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}")
    for _ in range(2):
        e = task.generate_example()
        out.append(f"**Prompt:**\n{e.prompt}")
        out.append(f"\n**Answer:**\n{e.answer}\n")

path = Path(__file__).with_name("samples_P005v1.md")
path.write_text("\n".join(out) + "\n")
print(f"wrote {path}")
