import random
from pathlib import Path

random.seed(798610012)

from distributional_jump_derivatives import DistributionalJumpDerivatives, DistributionalJumpConfig


def main():
    out = Path(__file__).with_name("samples_P006v1.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task = DistributionalJumpDerivatives()
        cfg = DistributionalJumpConfig()
        cfg.apply_difficulty(level)
        task.config = cfg
        for _ in range(2):
            e = task.generate_example()
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(e.prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("```")
            lines.append(e.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
