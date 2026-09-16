import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_semantics_r1.lsm_level_compaction_trace.lsm_level_compaction_trace import (
    LsmLevelCompactionTrace,
)

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")


def build_samples():
    random.seed(SEED)
    task = LsmLevelCompactionTrace()
    blocks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        blocks.append(f"## Level {level}")
        blocks.append("")
        for _ in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            blocks.append(prompt)
            blocks.append("")
            blocks.append(f"Answer: {x.answer}")
            blocks.append("")
    OUT.write_text("\n".join(blocks))


if __name__ == "__main__":
    build_samples()
