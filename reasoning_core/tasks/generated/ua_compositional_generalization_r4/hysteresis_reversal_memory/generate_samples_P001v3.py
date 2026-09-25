import random
import sys
from pathlib import Path

random.seed(4238614268)

sys.path.insert(0, str(Path(__file__).resolve().parent) + "/../../../..")

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.hysteresis_reversal_memory.hysteresis_reversal_memory import (
    HysteresisReversalMemory,
)

task = HysteresisReversalMemory()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"# Level {level}\n")
    for i in range(2):
        e = task.generate_example()
        out.append(f"## Example {i+1}\n")
        out.append("Prompt:\n")
        out.append(task.render_prompt(e.metadata))
        out.append("\n\nAnswer:\n")
        out.append(e.answer)
        out.append("\n\n---\n\n")

path = Path(__file__).with_name("samples_P001v3.md")
path.write_text("".join(out))
print("wrote", path)
