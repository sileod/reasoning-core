import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.forecast_diagnostic_decomposition.forecast_diagnostic_decomposition import (
    ForecastDiagnosticConfig,
    ForecastDiagnosticDecomposition,
)

SEED = 2409743872


def main():
    random.seed(SEED)
    task = ForecastDiagnosticDecomposition()
    out = []
    for level in (0, 2, 5):
        cfg = ForecastDiagnosticConfig()
        cfg.set_level(level)
        task.config = cfg
        out.append("## Level %d" % level)
        out.append("")
        for idx in range(2):
            e = task.generate_example()
            out.append("**Example %d**" % (idx + 1))
            out.append("")
            out.append("Prompt:")
            out.append("")
            out.append("```")
            out.append(task.render_prompt(e.metadata))
            out.append("```")
            out.append("")
            out.append("Answer: %s" % e.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P010v1.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
