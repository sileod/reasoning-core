import random
from pathlib import Path

from reasoning_core.template import Config

from cluster_seed_evolution import ClusterSeedEvolution

random.seed(2072234021)

OUT = Path(__file__).with_name("samples_P005v2.md")


def render_one(task, level):
    task.config.set_level(level)
    x = task.generate_example()
    return task.render_prompt(x.metadata), x.answer


task = ClusterSeedEvolution()

lines = []
for level in (0, 2, 5):
    lines.append("## Level %d" % level)
    lines.append("")
    for _ in range(2):
        prompt, answer = render_one(task, level)
        lines.append(prompt)
        lines.append("")
        lines.append("Answer")
        lines.append(answer)
        lines.append("")
        lines.append("---")
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
