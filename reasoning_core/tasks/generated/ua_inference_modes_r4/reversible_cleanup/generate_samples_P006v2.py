import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.reversible_workspace_cleanup.reversible_workspace_cleanup import (
    ReversibleCleanupV2,
    WorkspaceConfig,
)

random.seed(1705404348)

OUT = Path(__file__).with_name("samples_P006v2.md")


def main():
    task = ReversibleCleanupV2()
    blocks = []
    for level, label in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
        cfg = WorkspaceConfig().set_level(level)
        task.config = cfg
        examples = [task.generate_example() for _ in range(2)]
        parts = ["## %s\n" % label]
        for ex in examples:
            prompt = task.render_prompt(ex.metadata)
            parts.append("### Prompt\n```\n%s\n```\n" % prompt)
            parts.append("### Answer\n```\n%s\n```\n" % ex.answer)
        blocks.append("\n".join(parts))
    OUT.write_text("\n".join(blocks) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
