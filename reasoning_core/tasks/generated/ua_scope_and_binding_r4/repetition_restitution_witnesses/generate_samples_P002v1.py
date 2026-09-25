import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.repetition_restitution_witnesses.repetition_restitution_witnesses import (
    RepetitionRestitutionWitnesses,
)

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = RepetitionRestitutionWitnesses()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example(level=level, timeout=20)
            lines.append("**Prompt:**")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("**Answer:**")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
