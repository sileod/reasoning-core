import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_language_implementation_r4.macro_hygiene_expansion.macro_hygiene_expansion import (
    MacroHygieneExpansion,
)

SEED = 1475571465
LEVELS = [0, 2, 5]
PER_LEVEL = 2

random.seed(SEED)
task = MacroHygieneExpansion()

out = []
out.append("# Samples for macro_hygiene_expansion (P002v1)")
out.append("")
out.append("Two complete prompt/answer examples at each of levels 0, 2 and 5.")
out.append("")

for level in LEVELS:
    random.seed(SEED + level)
    task.config.set_level(level)
    out.append("## Level %d" % level)
    out.append("")
    for i in range(PER_LEVEL):
        ex = task.generate_example()
        out.append("### Example %d (level %d)" % (i + 1, level))
        out.append("")
        out.append("Prompt:")
        out.append("")
        out.append("```")
        out.append(ex.prompt)
        out.append("```")
        out.append("")
        out.append("Answer:")
        out.append("")
        out.append("```")
        out.append(ex.answer)
        out.append("```")
        out.append("")

outfile = Path(__file__).with_name("samples_P002v1.md")
outfile.write_text("\n".join(out))
print("wrote", outfile)
