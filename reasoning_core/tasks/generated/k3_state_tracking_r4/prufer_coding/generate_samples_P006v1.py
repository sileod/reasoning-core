import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_state_tracking_r4.prufer_coding import (
    prufer_coding as mod,
)


def main():
    random.seed(798610012)
    task = mod.PruferCoding()
    out = ["# Samples: prufer_coding (P006v1)\n"]
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"\n## Level {level}\n")
        for i in range(2):
            x = task.generate_example()
            out.append(f"\n### Example {i + 1}\n")
            out.append("Prompt:\n")
            out.append(task.render_prompt(x.metadata))
            out.append("\nAnswer:\n")
            out.append(x.answer)
    path = Path(__file__).with_name("samples_P006v1.md")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
