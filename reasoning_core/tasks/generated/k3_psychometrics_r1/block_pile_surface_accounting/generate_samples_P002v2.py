"""Generate gallery samples for block_pile_surface_accounting (seeded, byte-reproducible)."""

import argparse
import random
from pathlib import Path

import importlib.util

MODULE_PATH = Path(__file__).with_name("block_pile_surface_accounting.py")
_spec = importlib.util.spec_from_file_location(
    "block_pile_surface_accounting", MODULE_PATH)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

Task = mod.BlockPileSurfaceAccounting

SEED = 1336314872
LEVELS = (0, 2, 5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    out_path = (Path(args.out) if args.out
                else Path(__file__).with_name("samples_P002v2.md"))

    random.seed(SEED)
    lines = ["# Samples: block_pile_surface_accounting (P002v2)", ""]
    for level in LEVELS:
        task = Task()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
