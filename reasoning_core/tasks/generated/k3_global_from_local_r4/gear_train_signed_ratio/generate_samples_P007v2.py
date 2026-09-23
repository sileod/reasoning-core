import random
from pathlib import Path

random.seed(241712510)

from reasoning_core.tasks.generated.k3_global_from_local_r4.gear_train_signed_ratio import (
    gear_train_signed_ratio as gt,
)


def main():
    task = gt.GearTrainSignedRatio()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}")
            out.append("Prompt:")
            out.append(ex.prompt)
            out.append("Answer:")
            out.append(ex.answer)
            out.append("")
        out.append("")

    out_path = Path(__file__).with_name("samples_P007v2.md")
    out_path.write_text("\n".join(out), encoding="utf-8")
    print("wrote", out_path)


if __name__ == "__main__":
    main()
