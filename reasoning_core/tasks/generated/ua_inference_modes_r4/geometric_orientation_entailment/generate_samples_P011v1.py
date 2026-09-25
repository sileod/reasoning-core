import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.geometric_orientation_entailment.geometric_orientation_entailment import (
    GeometricOrientationEntailment,
    GeoOrientationEntailmentConfig,
)


def main():
    random.seed(2305351643)
    out = Path(__file__).with_name("samples_P011v1.md")
    lines = []
    for level in (0, 2, 5):
        cfg = GeoOrientationEntailmentConfig()
        cfg.apply_difficulty(level)
        task = GeometricOrientationEntailment(config_cls=GeoOrientationEntailmentConfig)
        task.config = cfg
        lines.append(f"## Level {level}")
        for _ in range(2):
            e = task.generate_example()
            lines.append("### Example")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(e.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
