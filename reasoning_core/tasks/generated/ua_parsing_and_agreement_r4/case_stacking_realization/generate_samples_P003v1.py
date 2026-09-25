import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.case_stacking_realization.case_stacking_realization import (
    CaseStackingRealization,
)

OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(2267388306)
    task = CaseStackingRealization()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append("**Prompt:**")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
