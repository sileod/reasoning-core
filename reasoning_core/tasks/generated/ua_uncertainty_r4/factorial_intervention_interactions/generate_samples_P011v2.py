import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.factorial_intervention_interactions.factorial_intervention_interactions import (
    FactorialInterventionInteractions,
)


def main():
    random.seed(525660630)
    out = []
    for level in (0, 2, 5):
        task = FactorialInterventionInteractions()
        task.config.set_level(level)
        out.append(f"## Level {level}")
        out.append("")
        for i in range(2):
            entry = task.generate_entry()
            prompt = task.render_prompt(entry.metadata)
            out.append(f"### Example {i + 1}")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append("**Answer:** `" + entry.answer + "`")
            out.append("")
    out_path = Path(__file__).with_name("samples_P011v2.md")
    out_path.write_text("\n".join(out))
    print("wrote", out_path)


if __name__ == "__main__":
    main()
