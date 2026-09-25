import importlib.util
import random
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent


def _load_task():
    mod_path = _ROOT / "renormalization_forest_subtraction.py"
    spec = importlib.util.spec_from_file_location(
        "renormalization_forest_subtraction", mod_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


SEED = 1339177894
OUT = _ROOT / "samples_P004v3.md"


def main():
    random.seed(SEED)
    mod = _load_task()
    task = mod.RenormalizationForestSubtraction()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("# Level %d" % level)
        lines.append("")
        for i in range(2):
            x = task.generate_example()
            lines.append("## Example %d" % (i + 1))
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
