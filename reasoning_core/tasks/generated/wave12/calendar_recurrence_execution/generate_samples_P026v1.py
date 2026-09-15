import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.calendar_recurrence_execution.calendar_recurrence_execution import (
    CalendarRecurrenceExecution,
)

SEED = 4088891760
OUT = Path(__file__).with_name("samples_P026v1.md")


def main():
    random.seed(SEED)
    task = CalendarRecurrenceExecution()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
