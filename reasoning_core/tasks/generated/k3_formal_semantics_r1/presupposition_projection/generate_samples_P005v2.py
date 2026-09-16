import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_semantics_r1.presupposition_projection.presupposition_projection import (
    PresuppositionProjection,
)

SEED = 2072234021


def main():
    random.seed(SEED)
    task = PresuppositionProjection()
    out = []
    for level in (0, 2, 5):
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        out.append(f"## Level {level}\n")
        for _ in range(4):
            entry = task.generate_example()
            out.append("### Example")
            out.append("")
            out.append(task.render_prompt(entry.metadata))
            out.append("")
            out.append(f"Answer: {entry.answer}")
            out.append("")
    path = Path(__file__).with_name("samples_P005v2.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
