import random
from pathlib import Path

from reasoning_core.template import Task
from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.measurement_uncertainty_propagation.measurement_uncertainty_propagation import MeasurementUncertaintyPropagation

SEED = 3867019559
OUT = Path(__file__).with_name("samples_P009v1.md")


def main():
    random.seed(SEED)
    task = MeasurementUncertaintyPropagation()
    lines = []
    for level, count in ((0, 2), (2, 2), (5, 2)):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        lines.append("")
        for _i in range(count):
            ex = task.generate_example()
            lines.append("## Example")
            lines.append("")
            lines.append("### Prompt")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
