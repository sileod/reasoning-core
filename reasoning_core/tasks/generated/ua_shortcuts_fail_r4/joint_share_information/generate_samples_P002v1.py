import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.joint_share_information.joint_share_information import JointShareInformation


def main():
    random.seed(1475571465)
    task = JointShareInformation()
    out = []
    out.append("# Samples P002v1 - joint_share_information\n")
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(2):
            entry = task.generate_example()
            out.append("Prompt:\n")
            out.append(entry.prompt)
            out.append("\nAnswer:\n")
            out.append(entry.answer)
            out.append("\n---\n")
    path = Path(__file__).with_name("samples_P002v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
