import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.trick_taking_adjudication.trick_taking_adjudication import TrickTakingAdjudication


def main():
    random.seed(1336314872)
    task = TrickTakingAdjudication()
    lines = ["# Samples for trick_taking_adjudication (P002v2)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.extend([f"## Level {level}", ""])
        for mode in ("legal", "winner", "points"):
            for _ in range(100):
                entry = task.generate_entry()
                if entry.metadata["mode"] == mode:
                    break
            else:
                raise RuntimeError(f"No {mode} sample in 100 attempts")
            lines.extend([f"### {mode.capitalize()} example", "", task.render_prompt(entry.metadata),
                          "", f"Answer: {entry.answer}", ""])
    Path(__file__).with_name("samples_P002v2.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
