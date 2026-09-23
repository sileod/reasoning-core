import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_interacting_updates_r4.integer_tatonnement_clearing.integer_tatonnement_clearing import (
    IntegerTatonnementClearing,
)

random.seed(1475571465)


def generate(level, count):
    cfg = IntegerTatonnementClearing.config_cls()
    cfg.set_level(level)
    t = IntegerTatonnementClearing(config=cfg)
    return [t.generate_example() for _ in range(count)]


def main():
    out = Path(__file__).with_name("samples_P002v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        for _ in range(2):
            ex = generate(level, 1)[0]
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.metadata["_prompt"] if "_prompt" in ex.metadata else _render(ex))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines))


def _render(ex):
    t = IntegerTatonnementClearing()
    return t.render_prompt(ex.metadata)


if __name__ == "__main__":
    main()
