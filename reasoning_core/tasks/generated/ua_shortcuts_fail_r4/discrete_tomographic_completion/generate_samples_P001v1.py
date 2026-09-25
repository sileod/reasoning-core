import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

random.seed(1662004003)

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.discrete_tomographic_completion.task import (
    DiscreteTomographicCompletion,
)

out = Path(__file__).with_name("samples_P001v1.md")


def render(task, level):
    task.config.set_level(level)
    x = task.generate_example()
    return x.metadata["answer_type"], x


task = DiscreteTomographicCompletion()

with open(out, "w") as f:
    for level in (0, 2, 5):
        f.write(f"## Level {level}\n\n")
        for i in range(2):
            qtype, x = render(task, level)
            f.write(f"### Example {i+1}\n\n")
            f.write("**Prompt:**\n\n")
            f.write(task.render_prompt(x.metadata))
            f.write("\n\n**Answer:**\n\n")
            f.write(x.answer)
            f.write("\n\n")
