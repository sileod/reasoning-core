import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.anyon_fusion_reassociation.anyon_fusion_reassociation import (
    AnyonFusionReassociation,
)

random.seed(729651269)


def main():
    task = AnyonFusionReassociation()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for _ in range(2):
            ex = task.generate_example(level=level)
            out.append("### Example")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            for line in ex.prompt.splitlines():
                out.append(line)
            out.append("")
            out.append("**Answer:** " + str(ex.answer))
            out.append("")
    path = Path(__file__).with_name("samples_P005v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
