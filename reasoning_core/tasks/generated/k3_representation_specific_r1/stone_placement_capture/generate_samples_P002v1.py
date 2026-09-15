import random
from pathlib import Path

from stone_placement_capture import StoneCaptureConfig, StonePlacementCapture


def main():
    random.seed(1475571465)
    out = Path(__file__).with_name("samples_P002v1.md")
    lines = []
    for level in (0, 2, 5):
        t = StonePlacementCapture()
        t.config = StoneCaptureConfig()
        t.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            e = t.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("**Prompt:**")
            lines.append(t.render_prompt(e.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append(e.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
