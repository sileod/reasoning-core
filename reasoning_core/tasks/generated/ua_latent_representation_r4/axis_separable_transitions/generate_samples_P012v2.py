"""Generate reproducible samples_P012v2.md for axis_separable_transitions."""

import random
from pathlib import Path

random.seed(214538085)

from reasoning_core.tasks.generated.ua_latent_representation_r4.axis_separable_transitions.axis_separable_transitions import (
    AxisSeparableTransitions,
)

OUT = Path(__file__).with_name("samples_P012v2.md")


def _render_example(task, level, seed_bump):
    random.seed(214538085 + seed_bump)
    task.config.set_level(level)
    x = task.generate_example()
    prompt = task.render_prompt(x.metadata)
    return prompt, x.answer


def _escape(text):
    return text.replace("```", "\\`\\`\\`")


def main():
    task = AxisSeparableTransitions()
    sections = []
    seed_bump = 0
    for level in (0, 2, 5):
        header = [f"## Level {level}", ""]
        for _ in range(2):
            seed_bump += 1
            prompt, answer = _render_example(task, level, seed_bump)
            header.append("### Example")
            header.append("")
            header.append("**Prompt**")
            header.append("")
            header.append("```")
            header.append(_escape(prompt))
            header.append("```")
            header.append("")
            header.append(f"**Answer**: `{answer}`")
            header.append("")
        sections.append("\n".join(header))
    OUT.write_text("\n".join(sections) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
