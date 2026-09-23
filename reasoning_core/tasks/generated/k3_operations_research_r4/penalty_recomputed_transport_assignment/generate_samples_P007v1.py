import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.penalty_recomputed_transport_assignment.penalty_recomputed_transport_assignment import (
    PenaltyRecomputedTransportAssignment,
    PenaltyRecomputedConfig,
)

SEED = 1139467751
OUT = Path(__file__).with_name("samples_P007v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in [0, 2, 5]:
        cfg = PenaltyRecomputedConfig()
        cfg.set_level(level)
        task = PenaltyRecomputedTransportAssignment(config=cfg)
        lines.append(f"## Level {level}")
        for k in range(1, 3):
            ex = task.generate_example()
            lines.append(f"\n### Example {k}")
            lines.append(f"**Prompt:**\n\n{ex.metadata['_prompt'] if '_prompt' in ex.metadata else task.render_prompt(ex.metadata)}")
            lines.append(f"\n**Answer:** `{ex.answer}`")
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
