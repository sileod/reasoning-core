import pathlib
import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.strategic_commitment_optimization.strategic_commitment_optimization import StrategicCommitmentOptimization

SEED = 729651269


def main():
    random.seed(SEED)
    task = StrategicCommitmentOptimization()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}\n")
        for _ in range(2):
            ex = task.generate_example()
            out.append("### Prompt\n")
            out.append(ex.prompt)
            out.append("\n\n### Answer\n")
            out.append(ex.answer)
            out.append("\n")
    path = pathlib.Path(__file__).with_name("samples_P005v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
