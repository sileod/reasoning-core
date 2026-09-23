import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.prenex_skolem_clause_form.prenex_skolem_clause_form import (
    PrenexSkolemClauseForm,
)

OUT = Path(__file__).with_name("samples_P002v3.md")


def main():
    random.seed(368817805)
    t = PrenexSkolemClauseForm()
    lines = []
    lines.append("# samples_P002v3: prenex_skolem_clause_form\n")
    lines.append("Two complete prompt/answer examples at levels 0, 2 and 5. "
                 "Answers are the gold answers the task scores.\n")
    for lvl in (0, 2, 5):
        t.config.set_level(lvl)
        lines.append("## Level %d\n" % lvl)
        for _ in range(2):
            x = t.generate_example()
            prompt = t.render_prompt(x.metadata)
            lines.append("### Prompt\n")
            lines.append(prompt)
            lines.append("\n### Answer\n")
            lines.append(x.answer)
            lines.append("")
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
