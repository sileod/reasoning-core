import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.bayesian_network_table_conversion.bayesian_network_table_conversion import (
    BayesianNetworkTableConversion,
)

random.seed(729651269)


def main():
    out = []
    task = BayesianNetworkTableConversion()
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}")
        for _ in range(2):
            x = task.generate_example()
            out.append("```")
            out.append(task.render_prompt(x.metadata))
            out.append("```")
            out.append(f"Answer: {x.answer}")
            out.append("")
    out.append("")
    Path(__file__).with_name("samples_P005v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
