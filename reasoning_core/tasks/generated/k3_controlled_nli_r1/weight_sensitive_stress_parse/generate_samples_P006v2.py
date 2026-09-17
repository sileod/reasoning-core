import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.weight_sensitive_stress_parse.weight_sensitive_stress_parse import (
    WeightSensitiveStressParse,
)


def main():
    random.seed(1705404348)
    task = WeightSensitiveStressParse()
    lines = ["# Samples: weight_sensitive_stress_parse (P006v2)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.extend([f"## Level {level}", ""])
        for i in range(2):
            entry = task.generate_example()
            lines.extend([f"### Example {i + 1}", "", "Prompt:", "", entry.prompt,
                          "", f"Answer: {entry.answer}", ""])
    Path(__file__).with_name("samples_P006v2.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
