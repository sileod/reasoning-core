import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.gnfa_state_elimination.gnfa_state_elimination import (
    GnfaStateElimination,
)

SEED = 3143501959
OUT = Path(__file__).with_name("samples_P010v3.md")


def main():
    random.seed(SEED)
    task = GnfaStateElimination()
    lines = ["# Samples for gnfa_state_elimination (P010v3)\n"]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        cfg = task.config_cls()
        cfg.apply_difficulty(level)
        task.config = cfg
        for _ in range(2):
            e = task.generate_entry()
            prompt = task.render_prompt(e.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {e.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
