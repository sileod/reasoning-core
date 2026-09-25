import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from reasoning_core.tasks.generated.ua_latent_structure_reconstruction_r4.scenario_recombination_stress.scenario_recombination_stress import (  # noqa: E402
    ScenarioRecombinationStress as Task,
    ScenarioConfig,
)

random.seed(1662004003)


def _run_level(name, level, count=2):
    task = Task()
    task.config = ScenarioConfig()
    task.config.set_level(level)
    lines = [f"## Level {level}", ""]
    assert isinstance(task.summary, str)
    for i in range(count):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        lines.extend([f"### Example {i+1}", "", prompt, "", f"Answer: {ex.answer}", ""])
    return "\n".join(lines)


def main():
    out = Path(__file__).with_name("samples_P001v1.md")
    parts = []
    for level in (0, 2, 5):
        parts.append(_run_level(f"level{level}", level))
    out.write_text("\n".join(parts))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR", type(e).__name__, e)
        sys.exit(1)
