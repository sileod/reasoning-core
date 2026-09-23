import random
from pathlib import Path

from reasoning_core.template import Task

from mealy_trace_machine_induction import MealyTraceMachineInduction

random.seed(3867019559)


def main():
    task = MealyTraceMachineInduction()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}\n")
        for _ in range(2):
            ex = task.generate_example()
            out.append("**Prompt:**")
            out.append("```")
            out.append(ex.prompt)
            out.append("```")
            out.append("")
            out.append("**Answer:**")
            out.append("```")
            out.append(ex.answer)
            out.append("```")
            out.append("")
    path = Path(__file__).with_name("samples_P009v1.md")
    path.write_text("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
