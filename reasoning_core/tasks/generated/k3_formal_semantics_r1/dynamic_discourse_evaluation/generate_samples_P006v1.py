import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_semantics_r1.dynamic_discourse_evaluation.dynamic_discourse_evaluation import (
    DynamicDiscourseEvaluation,
)

random.seed(798610012)

OUT = Path(__file__).with_name("samples_P006v1.md")
task = DynamicDiscourseEvaluation()

sections = []
for level in (0, 2, 5):
    rows = []
    for _ in range(2):
        cfg = DynamicDiscourseEvaluation().config_cls()
        cfg.seed = random.randrange(2 ** 32)
        cfg.set_level(level)
        t = DynamicDiscourseEvaluation()
        t.config = cfg
        e = t.generate_entry()
        prompt = t.render_prompt(e.metadata)
        rows.append((prompt, e.answer))
    section = "\n\n".join(
        "**Example %d**\n\nPrompt:\n```\n%s\n```\n\nAnswer:\n```\n%s\n```"
        % (i + 1, p, a)
        for i, (p, a) in enumerate(rows)
    )
    sections.append("## Level %d\n\n%s" % (level, section))

md = "\n\n".join(sections) + "\n"
OUT.write_text(md)
print("wrote %s" % OUT)
