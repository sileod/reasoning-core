import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.cyclic_proof_closure.cyclic_proof_closure import (
    CyclicProofClosure,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")
task = CyclicProofClosure()

LEVELS = [0, 0, 2, 2, 5, 5]
lines = []


def render_lines(ex):
    out = [ex.prompt, "", "Answer: %s" % ex.answer, ""]
    return out


for idx, level in enumerate(LEVELS):
    ex = task.generate_example(level=level)
    heading = {0: "Level 0", 2: "Level 2", 5: "Level 5"}[level]
    if idx % 2 == 0:
        lines.append("## %s" % heading)
    lines.extend(render_lines(ex))

OUT.write_text("\n".join(lines) + "\n")
print("wrote", OUT)
