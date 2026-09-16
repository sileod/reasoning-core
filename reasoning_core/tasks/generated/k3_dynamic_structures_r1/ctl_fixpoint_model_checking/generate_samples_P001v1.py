import random
from pathlib import Path

from reasoning_core.template import Task

from ctl_fixpoint_model_checking import CtlFixpointModelChecking

random.seed(1662004003)


def main():
    task = CtlFixpointModelChecking()
    out = []
    out.append("# samples_P001v1\n")
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for i in range(2):
            entry = task.generate_example()
            out.append(f"### Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append("```\n" + entry.prompt + "\n```\n")
            out.append("Answer:\n")
            out.append("```\n" + entry.answer + "\n```\n")
    path = Path(__file__).with_name("samples_P001v1.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
