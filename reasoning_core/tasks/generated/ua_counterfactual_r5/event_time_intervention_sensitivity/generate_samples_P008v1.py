import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r5.event_time_intervention_sensitivity.event_time_intervention_sensitivity import (
    EventTimeInterventionSensitivity,
)


def main():
    random.seed(682015719)
    task = EventTimeInterventionSensitivity()
    out = Path(__file__).with_name("samples_P008v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("Prompt:")
            lines.append(ex.prompt)
            lines.append("Answer:")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
