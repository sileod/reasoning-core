import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_latent_representation_r4.stereochemical_parity_transport.stereochemical_parity_transport import (
    StereochemicalParityTransport,
)

SEED = 382564971
OUT = Path(__file__).with_name("samples_P003v2.md")

TASK = StereochemicalParityTransport()


def render(cfg):
    ex = TASK.generate_example()
    return ex


def main():
    random.seed(SEED)
    lines = []
    for lvl in (0, 2, 5):
        TASK.config.set_level(lvl)
        lines.append(f"## Level {lvl}")
        lines.append("")
        for i in range(2):
            ex = TASK.generate_example()
            prompt = TASK.render_prompt(ex.metadata)
            lines.append(f"**Example {i + 1}**")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
