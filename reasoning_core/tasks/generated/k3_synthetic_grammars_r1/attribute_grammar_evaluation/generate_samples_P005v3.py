import random

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.attribute_grammar_evaluation.attribute_grammar_evaluation import (
    AttributeGrammarEvaluation,
    _evaluate,
    _count_env,
    score_answer,
)

random.seed(1140349348)

OUT = __import__("pathlib").Path(__file__).with_name("samples_P005v3.md")


def main():
    task = AttributeGrammarEvaluation()
    lines = []
    lines.append("# Attribute Grammar Evaluation - samples P005v3")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for k in range(2):
            ex = task.generate_entry()
            lines.append(f"### Example {k+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
