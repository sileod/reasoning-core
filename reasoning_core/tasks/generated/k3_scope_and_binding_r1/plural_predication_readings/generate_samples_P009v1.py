import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.plural_predication_readings.plural_predication_readings import (
    PluralConfig,
    PluralPredicationReadings,
)

SEED = 3867019559
OUT = Path(__file__).with_name("samples_P009v1.md")

LEVELS = [0, 2, 5]
PER_LEVEL = 2


def main():
    lines = []
    for level in LEVELS:
        cfg = PluralConfig()
        cfg.set_level(level)
        t = PluralPredicationReadings()
        t.config = cfg
        lines.append(f"# Level {level}")
        lines.append("")
        for i in range(PER_LEVEL):
            entry = t.generate_example()
            lines.append(f"## Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            for pl in entry.metadata["_prompt_text"] if isinstance(entry.metadata.get("_prompt_text"), list) else [t.render_prompt(entry.metadata)]:
                lines.append(pl)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    random.seed(SEED)
    main()
