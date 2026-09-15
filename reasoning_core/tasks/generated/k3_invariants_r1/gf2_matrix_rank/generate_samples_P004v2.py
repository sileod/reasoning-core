import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.gf2_matrix_rank.gf2_matrix_rank import (
    GF2MatrixRank,
)

random.seed(3577985643)

task = GF2MatrixRank()


def render_example(level):
    task.config.set_level(level)
    x = task.generate_example()
    return task.render_prompt(x.metadata), x.answer


out = []
for level in (0, 2, 5):
    out.append(f"## Level {level}\n")
    for i in range(2):
        prompt, answer = render_example(level)
        out.append(f"### Example {i+1}\n")
        out.append(prompt + "\n")
        out.append(f"Answer: {answer}\n")
    out.append("")

Path(__file__).with_name("samples_P004v2.md").write_text("\n".join(out))
