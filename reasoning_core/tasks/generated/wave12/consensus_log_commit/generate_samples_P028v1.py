import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.consensus_log_commit.consensus_log_commit import (
    ConsensusLogCommit,
)

SEED = 4126195972
OUT = Path(__file__).with_name("samples_P028v1.md")


def build_samples():
    random.seed(SEED)
    task = ConsensusLogCommit()
    blocks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        blocks.append(f"## Level {level}\n")
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
