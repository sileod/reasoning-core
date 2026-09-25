import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.monotonicity_context_signatures.monotonicity_context_signatures import (
    MonotonicityContextSignatures,
)

random.seed(2302342651)

LEVELS = [0, 2, 5]
PER_LEVEL = 2

task = MonotonicityContextSignatures()

out = []
for level in LEVELS:
    task.config.set_level(level)
    out.append(f"# Level {level}\n")
    for i in range(PER_LEVEL):
        ex = task.generate_example()
        out.append(f"## Example {i + 1}\n")
        out.append("Prompt:\n\n" + task.render_prompt(ex.metadata) + "\n")
        out.append(f"\nAnswer: {ex.answer}\n")

out.append("\nGenerated deterministically with seed 2302342651.\n")
Path(__file__).with_name("samples_P001v2.md").write_text("\n".join(out))
