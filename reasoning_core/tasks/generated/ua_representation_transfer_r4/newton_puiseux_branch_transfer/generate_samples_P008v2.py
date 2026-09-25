import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.newton_puiseux_branch_transfer.newton_puiseux_branch_transfer import (
    NewtonPuiseuxBranchTransfer,
)

SEED = 3020341981


def main():
    random.seed(SEED)
    task = NewtonPuiseuxBranchTransfer()
    out = []
    out.append("# samples_P008v2\n")
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for i in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            answer = entry.answer
            out.append(f"### Example {i + 1}\n")
            out.append("**Prompt:**\n")
            out.append("```\n")
            out.append(prompt.rstrip("\n"))
            out.append("\n```\n")
            out.append("**Answer:**\n")
            out.append("```\n")
            out.append(answer)
            out.append("\n```\n")
    text = "\n".join(out)
    target = Path(__file__).with_name("samples_P008v2.md")
    target.write_text(text, encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
