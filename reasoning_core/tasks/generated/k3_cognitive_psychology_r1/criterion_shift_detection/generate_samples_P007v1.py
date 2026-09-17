import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.criterion_shift_detection.criterion_shift_detection import (
    CriterionShiftDetection,
)

SEED = 1139467751


def main():
    random.seed(SEED)
    lines = ["# Samples for criterion_shift_detection (P007v1)", ""]
    for level in (0, 2, 5):
        lines.extend([f"## Level {level}", ""])
        task = CriterionShiftDetection()
        task.config.set_level(level)
        for i, mode in enumerate(("responses", "totals", "criterion"), 1):
            for _ in range(128):
                entry = task.generate_entry()
                if entry.metadata["mode"] == mode:
                    break
            else:
                raise RuntimeError(f"No sample for {mode}")
            lines.extend([f"### Example {i}", "", "Prompt:", "",
                          task.render_prompt(entry.metadata), "",
                          f"Answer: {entry.answer}", ""])
    path = Path(__file__).with_name("samples_P007v1.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
