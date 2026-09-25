import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.settlement_departure_consistency.settlement_departure_consistency import (
    SettlementDepartureConsistency,
)


def _fmt_answer(e):
    return e.answer


def main():
    random.seed(1139467751)
    task = SettlementDepartureConsistency()
    out_path = Path(__file__).with_name("samples_P007v1.md")
    lines = [
        "# Samples for P007v1: settlement_departure_consistency",
        "",
        "Seed: 1139467751",
        "",
    ]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(e.metadata))
            lines.append("```")
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append("```")
            lines.append(_fmt_answer(e))
            lines.append("```")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
