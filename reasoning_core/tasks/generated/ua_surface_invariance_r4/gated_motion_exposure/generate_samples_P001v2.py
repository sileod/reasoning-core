import random
from pathlib import Path

random.seed(2302342651)

from reasoning_core.tasks.generated.ua_surface_invariance_r4.gated_motion_exposure.gated_motion_exposure import (
    GatedMotionExposure,
    GatedMotionExposureConfig,
)


def main():
    out = Path(__file__).with_name("samples_P001v2.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        cfg = GatedMotionExposureConfig()
        cfg.set_level(level)
        task = GatedMotionExposure(config=cfg)
        for n in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {n + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
