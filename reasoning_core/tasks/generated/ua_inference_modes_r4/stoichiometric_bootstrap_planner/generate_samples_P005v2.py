import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.stoichiometric_bootstrap_planning.stoichiometric_bootstrap_planning import (
    StoichiometricBootstrapPlannerV2,
)

random.seed(2072234021)

OUT = Path(__file__).with_name("samples_P005v2.md")


def example_for(level):
    t = StoichiometricBootstrapPlannerV2()
    t.config.set_level(level)
    ex = t.generate_example()
    return t.render_prompt(ex.metadata), ex.answer


def main():
    out = ["# Samples for stoichiometric_bootstrap_planning (P005v2)", ""]
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for i in range(2):
            prompt, answer = example_for(level)
            out.append(f"### Example {i + 1}")
            out.append("")
            out.append("Prompt:")
            out.append("")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append("Answer:")
            out.append("")
            out.append("```")
            out.append(answer)
            out.append("```")
            out.append("")
    OUT.write_text("\n".join(out))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
