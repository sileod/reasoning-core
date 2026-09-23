import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.design_column_alias_audit.design_column_alias_audit import (
    DesignColumnAliasAudit,
)

SEED = 3536382515


def main():
    random.seed(SEED)
    task = DesignColumnAliasAudit()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            out.append(prompt)
            out.append(f"\nAnswer: {x.answer}\n")
    Path(__file__).with_name("samples_P004v1.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
