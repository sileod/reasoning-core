import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_latent_representation_r4.support_function_composition.support_function_composition import (
    SupportFunctionComposition,
    SupportFunctionCompositionConfig,
)

SEED = 3867019559
OUT = Path(__file__).with_name("samples_P009v1.md")


def main():
    random.seed(SEED)
    task = SupportFunctionComposition()
    lines = ["# Samples for support_function_composition (P009v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        cfg = SupportFunctionCompositionConfig()
        cfg.set_level(level)
        task.config = cfg
        for i in range(2):
            e = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(e.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
