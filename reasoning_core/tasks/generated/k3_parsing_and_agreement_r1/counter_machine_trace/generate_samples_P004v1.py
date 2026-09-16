import os
import random

seed = 3536382515
random.seed(seed)

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.counter_machine_trace.counter_machine_trace import (  # noqa: E402
    CounterMachineConfig,
    CounterMachineTrace,
)


def emit(level):
    cfg = CounterMachineConfig()
    cfg.set_level(level)
    task = CounterMachineTrace()
    task.config = cfg
    lines = [f"## Level {level}"]
    for _ in range(2):
        x = task.generate_example()
        lines.append("")
        lines.append("Prompt:")
        lines.append(task.render_prompt(x.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append(x.answer)
    return "\n".join(lines)


parts = []
for lvl in (0, 2, 5):
    parts.append(emit(lvl))

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "samples_P004v1.md")
with open(out, "w") as f:
    f.write("\n".join(parts) + "\n")
