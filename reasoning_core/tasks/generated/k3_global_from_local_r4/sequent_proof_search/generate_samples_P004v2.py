import os
import random

seed = 3577985643
random.seed(seed)

from reasoning_core.tasks.generated.k3_global_from_local_r4.sequent_proof_search.sequent_proof_search import (  # noqa: E402
    SequentProofConfig,
    SequentProofSearch,
)


def emit(level):
    cfg = SequentProofConfig()
    cfg.set_level(level)
    task = SequentProofSearch()
    task.config = cfg
    lines = [f"### Level {level}"]
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
with open(os.path.join(here, "samples_P004v2.md"), "w") as f:
    f.write("\n".join(parts) + "\n")
