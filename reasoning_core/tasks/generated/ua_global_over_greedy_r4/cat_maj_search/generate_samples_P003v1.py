import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.catalytic_majorization_search. \
    catalytic_majorization_search import CatMajSearch

random.seed(2267388306)

task = CatMajSearch()
out = Path(__file__).with_name("samples_P003v1.md")

lines = []
for level in (0, 2, 5):
    lines.append("Level %d\n" % level)
    for _ in range(2):
        ex = task.generate_example(level=level)
        lines.append("Prompt:\n%s\n" % ex.prompt)
        lines.append("Answer: %s\n" % ex.answer)

out.write_text("\n".join(lines))
print("\n".join(lines))
