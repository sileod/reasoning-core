import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_global_from_local_r4.facility_member_swap_descent.facility_member_swap_descent import \
    FacilityMemberSwapDescent


def main():
    random.seed(1475571465)
    task = FacilityMemberSwapDescent()
    out = Path(__file__).with_name("samples_P002v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append("Level %d" % level)
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("Prompt:\n```\n%s\n```" % ex.prompt)
            lines.append("Answer:\n```\n%s\n```" % ex.answer)
        lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out.resolve())


if __name__ == "__main__":
    main()
