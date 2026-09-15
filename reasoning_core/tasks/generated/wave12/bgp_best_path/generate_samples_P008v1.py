import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.bgp_best_path.bgp_best_path import BgpBestPath

random.seed(2401670496)

OUT = Path(__file__).with_name("samples_P008v1.md")

task = BgpBestPath()

with open(OUT, "w") as f:
    for level in (0, 2, 5):
        task.config.set_level(level)
        f.write(f"## Level {level}\n\n")
        for _ in range(2):
            e = task.generate_example()
            f.write(task.render_prompt(e.metadata))
            f.write("\n\nAnswer: ")
            f.write(e.answer)
            f.write("\n\n")
