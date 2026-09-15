import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.instruction_data_boundary.instruction_data_boundary import (
    InstructionDataBoundary,
)

SEED = 1356906099

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = InstructionDataBoundary()
    out = []
    for level, count in LEVELS.items():
        out.append(f"## Level {level}")
        for _ in range(count):
            task.config.set_level(level)
            ex = task.generate_example()
            prompt = ex.metadata["prompt"]
            answer = ex.answer
            out.append(f"### Prompt")
            out.append(prompt)
            out.append(f"### Answer")
            out.append(answer)
        out.append("")
    Path(__file__).with_name("samples_P002v1.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
