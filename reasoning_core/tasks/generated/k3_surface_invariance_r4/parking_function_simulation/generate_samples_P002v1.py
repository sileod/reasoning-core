import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_surface_invariance_r4.parking_function_simulation.parking_function_simulation import (
    ParkingFunctionSimulation,
)

SEED = 1475571465


def main():
    random.seed(SEED)
    task = ParkingFunctionSimulation()
    out = Path(__file__).with_name("samples_P002v1.md")
    lines = []
    with open(out, "w") as f:
        f.write("# Parking Function Simulation v1 -- P002v1 samples\n\n")
        for level in (0, 2, 5):
            task.config.set_level(level)
            f.write(f"## Level {level}\n\n")
            for _ in range(2):
                ex = task.generate_example()
                prompt = task.render_prompt(ex.metadata)
                f.write("### Example\n\n")
                f.write("**Prompt:**\n\n")
                f.write(prompt + "\n\n")
                f.write("**Answer:**\n\n")
                f.write(ex.answer + "\n\n")


if __name__ == "__main__":
    main()
