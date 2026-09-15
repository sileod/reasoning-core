import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relevance_separation_r1.schwartz_zippel_identity.schwartz_zippel_identity import (
    SchwartzZippelIdentity,
    SchwartzZippelConfig,
)

SEED = 2267388306
OUT = Path(__file__).with_name("samples_P003v1.md")

TASK = SchwartzZippelIdentity()


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        cfg = SchwartzZippelConfig()
        cfg.set_level(level)
        TASK.config = cfg
        lines.append(f"# Level {level}")
        for i in range(2):
            e = TASK.generate_example()
            prompt = TASK.render_prompt(e.metadata)
            lines.append("### Example prompt")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
