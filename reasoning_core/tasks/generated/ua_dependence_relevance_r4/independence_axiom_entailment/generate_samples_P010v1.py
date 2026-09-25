import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.independence_axiom_entailment.independence_axiom_entailment import (
    IndependenceAxiomEntailment,
    IndependenceConfig,
)

SEED = 2409743872


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P010v1.md")
    lines = ["# Samples for independence_axiom_entailment (P010v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        cfg = IndependenceConfig()
        cfg.set_level(level)
        task = IndependenceAxiomEntailment(cfg)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
