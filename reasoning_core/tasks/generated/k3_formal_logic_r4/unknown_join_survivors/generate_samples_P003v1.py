import random
from pathlib import Path

import reasoning_core.tasks.generated.k3_formal_logic_r4.unknown_join_survivors.unknown_join_survivors as mod

random.seed(2267388306)
task = mod.UnknownJoinSurvivors()

out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append("## Level %d" % level)
    for _ in range(2):
        e = task.generate_example()
        out.append("")
        out.append(e.prompt)
        out.append("")
        out.append("Answer: %s" % e.answer)
        out.append("")

dest = Path(__file__).with_name("samples_P003v1.md")
dest.write_text("\n".join(out))
print("wrote", dest)
