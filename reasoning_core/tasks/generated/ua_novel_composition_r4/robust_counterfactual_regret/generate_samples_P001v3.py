import random

from reasoning_core.tasks.generated.ua_novel_composition_r4.robust_counterfactual_regret.robust_counterfactual_regret import (
    RobustCounterfactualRegret,
    best_intervention_and_witness,
    worst_regret,
)

random.seed(4238614268)


def render_examples(task, level, count):
    task.config.set_level(level)
    examples = []
    for _ in range(count):
        e = task.generate_example()
        examples.append((task.render_prompt(e.metadata), e.answer))
    return examples


def main():
    task = RobustCounterfactualRegret()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}\n")
        for prompt, answer in render_examples(task, level, 2):
            out.append("Prompt:\n")
            out.append(prompt)
            out.append("\nAnswer:\n")
            out.append(answer)
            out.append("\n")
    text = "\n".join(out)
    dest = __import__("pathlib").Path(__file__).with_name("samples_P001v3.md")
    dest.write_text(text)


if __name__ == "__main__":
    main()
