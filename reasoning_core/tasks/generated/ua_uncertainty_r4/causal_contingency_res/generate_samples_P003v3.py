"""Generate samples_P003v3.md reproducibly (seeded)."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.causal_contingency_responsibility.causal_contingency_responsibility import (
    CausalContingencyResV3,
)

SEED = 1259343118
OUT = Path(__file__).with_name("samples_P003v3.md")


def main():
    random.seed(SEED)
    t = CausalContingencyResV3()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            t.config.set_level(level)
            x = t.generate_example()
            lines.append("### Example")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(t.render_prompt(x.metadata))
            lines.append("```")
            lines.append("")
            lines.append(f"**Answer:** {x.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
